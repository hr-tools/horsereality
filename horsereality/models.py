from bs4 import BeautifulSoup
import datetime
import re

from typing import Any, Dict, Optional, List

from .enums import LayerType
from .errors import PageAlertException
from .utils import layer_path_regex, get_lifenumber_from_url

__all__ = (
    'Horse',
    'Layer',
)


class Layer:
    def __init__(self, *, http, url: str):
        self._http = http

        match = layer_path_regex.match(url)
        if not match:
            raise ValueError('Invalid layer URL.')
        path = match.group(1)
        if not path:
            raise ValueError('Invalid layer URL.')

        layer_attrs_list = path.split('/')

        self.type: LayerType = getattr(LayerType, layer_attrs_list[2])  # colours, whites
        self.horse_type: str = layer_attrs_list[3]  # mares, stallions, foals
        self.body_part: str = layer_attrs_list[4]  # body, mane, tail
        self.size: str = layer_attrs_list[5]  # small, medium, large
        self.id: str = layer_attrs_list[6]  # These are not unique

    def __repr__(self) -> str:
        return f'<Layer type={self.type.value!r} horse_type={self.horse_type!r} body_part={self.body_part!r} size={self.size!r} id={self.id!r}>'

    def url_path_with_size(self, size: str = None):
        size = size or self.size
        if size not in ('small', 'medium', 'large'):
            raise ValueError(f'Unknown size {size!r}')
        return f'/upload/{self.type.value}/{self.horse_type}/{self.body_part}/{size}/{self.id}.png'

    def url_with_size(self, size: str = None):
        return f'https://www.horsereality.com{self.url_path_with_size(size)}'

    @property
    def url_path(self):
        return self.url_path_with_size(self.size)

    @property
    def url(self):
        return self.url_with_size(self.size)

    async def read(self, size: str = None) -> bytes:
        data = await self._http.request('GET', self.url_path_with_size(size))
        return data['data']

    def to_dict(self):
        return {
            'type': self.type.value,
            'horse_type': self.horse_type,
            'body_part': self.body_part,
            'size': self.size,
            'id': self.id,
        }


class Horse:
    def __init__(self, *, http, data):
        self._http = http

        self.lifenumber: int = data.get('lifenumber')
        self.name: str = data.get('name')
        self.sex: str = data.get('sex')
        self.raw_breed: str = data.get('breed')
        self.breed: str = self.raw_breed.lower().replace(' ', '_').replace('-', '_')
        self.age: str = data.get('age')
        self.birthdate: str = data.get('birthdate')
        self.height: str = data.get('horse_height')
        self.location: str = data.get('location')
        self.owner: str = data.get('owner')
        self.registry: str = data.get('registry')
        self.predicates: str = data.get('predicates')

        self.looking_at: Optional[str] = data.get('looking_at')
        self.multiple_on_page: bool = self.looking_at is not None

        all_layers = data.get('layers', {})
        self.adult_layers: List[Layer] = all_layers.get('adult', [])
        self.foal_layers: List[Layer] = all_layers.get('foal', [])
        self.foal_lifenumber: Optional[int] = data.get('foal_lifenumber')

    def __repr__(self) -> str:
        return f'<Horse lifenumber={self.lifenumber!r} name={self.name!r} foal={self.is_foal()!r}>'

    @property
    def birthdate_date(self) -> datetime.date:
        day, month, year = self.birthdate.split('-')
        return datetime.date(int(year), int(month), int(day))

    def is_foal(self) -> bool:
        return (
            len(self.foal_layers) > 0
            and (
                self.looking_at == 'foal'
                or len(self.adult_layers) < 1
            )
        )

    @property
    def layers(self) -> List[Layer]:
        """Returns the layers of whichever horse on the page you are looking at."""
        return self.foal_layers if self.is_foal() else self.adult_layers

    def to_dict(self) -> Dict[str, Any]:
        return {
            'lifenumber': self.lifenumber,
            'name': self.name,
            'sex': self.sex,
            'age': self.age,
            'birthdate': self.birthdate,
            'breed': self.breed,
            'height': self.height,
            'location': self.location,
            'owner': self.owner,
            'registry': self.registry,
            'predicates': self.predicates,
            'foal': self.is_foal(),
            'foal_lifenumber': self.foal_lifenumber,
            'layers': [layer.to_dict() for layer in self.layers],
        }

    @classmethod
    async def _from_page(cls, http, html_text):
        soup = BeautifulSoup(html_text, 'html.parser')

        # Check if this page errored before doing anything (Horse Reality does not return apt status codes)
        alert_error = soup.select_one('.error')
        if alert_error and not alert_error.attrs.get('style') == 'display:none;':
            raise PageAlertException(list(alert_error.stripped_strings)[-1])

        # Sidebar box
        data = {}
        try:
            data['name'] = soup.select_one('.horse_left>h1').string.strip()
        except:
            data['name'] = re.sub(r' - Horse Reality$', '', soup.title.string)
        try:
            data['sex'] = soup.select_one('img.icon16').attrs['alt'].lower()
        except:
            data['sex'] = None

        # Selecting the two "columns" for what we will call the key and value--left and right respectively
        left_info = soup.select('div.horse_left .infotext .left')
        right_info = soup.select('div.horse_left .infotext .right')
        for left, right in zip(left_info, right_info):
            key = left.string.strip().lower().replace(' ', '_')
            value = (right.string or '').strip() or None
            data[key] = value

        data['lifenumber'] = int(data.pop('lifenumber').replace('#', ''))

        # Image layers
        divs = soup.find_all('div', class_='horse_photo')
        data['layers'] = {
            'adult': [],
            'foal': [],
        }
        if divs:
            # When there is both a foal and a mare, there are two 'horse_photo'
            # elements - one with a 'mom' class on the parent 'horse_photocon' element.
            # We deal with this in the following loop:
            for div in divs:
                # Find all the layer URLs (does not get blank.png)
                urls = re.findall(r'\/upload\/[a-z]+\/[a-z]+\/[a-z]+\/[a-z]+\/[a-z0-9]+\.png', str(div))

                # Converting to Layers dissects the strings for us and makes them easier to deal with
                div_layers = [Layer(http=http, url=url) for url in urls]

                # We want it to be very unambiguous whether a list of layers is for a foal or an adult
                if 'foal' in div.parent['class'] or div_layers[0].horse_type == 'foals':
                    data['layers']['foal'] += div_layers
                else:
                    data['layers']['adult'] += div_layers

        # Looking at
        looking_at_element = soup.select_one('.looking_at>p>strong')
        if looking_at_element and looking_at_element.string:
            # Sometimes this class is used for unrelated strings, e.g. "This stallion is standing at stud"
            # The Realtools extension is guilty of misusing this class too, but we would never encounter that here.
            if 'looking at' in looking_at_element.string:
                age = looking_at_element.string.replace('You\'re currently looking at the', '').strip()
                data['looking_at'] = age

        if data.get('looking_at') == 'dam':
            # There's a foal on the page, but we aren't looking at it
            foal_url = divs[1].parent.parent.attrs['href']  # a>div.horse_photocon.foal>div.horse_photo
            data['foal_lifenumber'] = get_lifenumber_from_url(foal_url)

            # We could search the pedigree for the dam's lifenumber if we are
            # looking at the foal, but that was deemed more effort than it would
            # be worth--taking into account the fact that Realtools does not need
            # that information.

        return cls(http=http, data=data)

    async def fetch_foal(self):
        """Fetch this dam's foal, if it exists on the page."""
        if not self.foal_lifenumber:
            raise ValueError('This dam has no foal on its page.')

        html_text = await self._http.get_horse(self.foal_lifenumber)
        horse = await Horse._from_page(http=self._http, html_text=html_text)
        return horse
