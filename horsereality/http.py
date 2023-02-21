import datetime
from typing import Optional
from urllib.parse import urlparse
import aiohttp
import asyncio
from bs4 import BeautifulSoup

from . import __version__
from .errors import (
    ClientNotInitialized,
    HTTPException,
    RateLimitExceeded,
    AuthenticationException,
    RolloverRequired,
)


class HTTPClient:
    def __init__(
        self,
        remember_cookie_name: str,
        remember_cookie_value: str,
        *,
        auto_rollover: bool = False,
        allow_unverified_client: bool = False,
    ):
        self.session: Optional[aiohttp.ClientSession] = None
        self.remember_cookie = {remember_cookie_name: remember_cookie_value}

        self._allow_unverified_client: bool = allow_unverified_client
        self.last_request_attempt_at: Optional[datetime.datetime] = None

        self._auto_rollover: bool = auto_rollover
        self._rollover_lock: Optional[asyncio.Lock] = None

        # We have to provide a user agent in order to avoid getting blocked from creating sessions.
        # Unfortunately the very nature of this requirement prevents its solution from being very detailed.
        self.user_agent = f'HorseReality/{__version__}'

    @property
    def cookies(self):
        cookie = self.remember_cookie.copy()
        return cookie

    async def request(self, method: str, path: str, *, v2: bool = False, **kwargs):
        url = f'https://{"v2" if v2 else "www"}.horsereality.com{path}'

        # We want to default to false in case we get a 302
        return_headers = kwargs.pop('return_headers', False)
        kwargs['allow_redirects'] = kwargs.pop('allow_redirects', False)

        async with self._rollover_lock:
            for tries in range(5):
                if not self.session or self.session.closed:
                    if self.last_request_attempt_at and (datetime.datetime.utcnow() - self.last_request_attempt_at).seconds >= 600 and tries == 0:
                        await self.initialize()
                        continue
                    else:
                        raise ClientNotInitialized()

                response = await self.session.request(method=method, url=url, **kwargs)
                location = urlparse(response.headers.get('location')) if response.headers.get('location') else None

                if (location and location.path == '/error-404') or response.status == 404:
                    # In the past, HR has not properly returned a 404 page and instead cycled the
                    # client between two URLs, so we had to handle this ourselves. Nowadays this
                    # should not happen.
                    raise HTTPException(response, f'Page not found: {url}')

                elif location and location.path.startswith('/daily-rollover') and not path.startswith('/daily-rollover'):
                    # The client needs to complete the daily rollover
                    if self._auto_rollover:
                        await self.rollover()
                        continue
                    else:
                        raise RolloverRequired(url, response)

                elif response.status == 302:
                    # We are not authenticated properly
                    if tries == 5:
                        # Give up
                        raise AuthenticationException('Failed to re-authorize 5 times in a row.')

                    await self.initialize()
                    continue

                elif response.status in (403, 429):
                    # Horse Reality ended up implementing very strict rate
                    # limiting that isn't so straightforwardly backed off.
                    # Let a different timer handle it.
                    await self.uninitialize()
                    raise RateLimitExceeded(response)

                if (response.headers.get('Content-Type') or '').split('/')[0] == 'image':
                    data = await response.read()
                else:
                    data = await response.text()

                return {
                    'status': response.status,
                    'data': data,
                    'headers': (response.headers if return_headers else None),
                }

        raise Exception('Failed to finalize the request to %s %s after %s tries.' % method, path, tries)

    async def initialize(self) -> None:
        self.session = self.session if self.session and not self.session.closed else aiohttp.ClientSession(headers={'User-Agent': self.user_agent})
        self._rollover_lock = self._rollover_lock if self._rollover_lock else asyncio.Lock()

        # We need to provide `v1RedirectUrl` with our remembrance cookie so
        # that HR knows to redirect us as though we have just logged in with
        # an email & password.
        get_response = await self.session.request(
            'GET', 'https://v2.horsereality.com/login',
            params={'v1RedirectUrl': 'https://www.horsereality.com'},
            cookies=self.cookies,
            allow_redirects=False,
        )

        if self._allow_unverified_client and get_response.status != 302:
            await self.uninitialize()
            return
        elif get_response.status >= 500:
            raise HTTPException(get_response, 'Server error while logging in')
        elif get_response.status in (403, 429):
            raise RateLimitExceeded(get_response)
        elif get_response.status != 302:
            raise AuthenticationException('Failed to log in, likely due to an invalid remembrance cookie name or value.')

        self.last_request_attempt_at = None
        if urlparse(get_response.headers['location']).path.startswith('/daily-rollover'):
            # Authentication for v1 was halted by the rollover page
            if self._auto_rollover:
                # The client has indicated that they want to roll over automatically
                await self.rollover()
                await self.initialize()
                return
            else:
                raise RolloverRequired('https://v2.horsereality.com/login', get_response)

        # We make yet another request--to the auth token "page"--to finally get our cookie.
        # self.request is not used here because we want to use whatever URL HR throws at us, which _could_ change unexpectedly.
        cookie_response = await self.session.request(
            'GET',
            get_response.headers['location'],  # https://www.horsereality.com/?v2_auth_token=...
            allow_redirects=False,
        )

        try:
            # self.cookies['horsereality'] = 
            cookie_response.cookies['horsereality'].value
        except (KeyError, AttributeError):
            raise AuthenticationException()

    async def uninitialize(self):
        self.last_request_attempt_at = datetime.datetime.utcnow()
        await self.session.close()
        print('Closed session without initializing due to failed login response')

    async def get_horse(self, lifenumber: int) -> str:
        data = await self.request('GET', f'/horses/{lifenumber}/')
        return data['data']

    async def rollover(self) -> None:
        get_response = await self.session.request(
            'GET', 'https://v2.horsereality.com/daily-rollover',
            params={'url': 'https://www.horsereality.com'},
        )
        if get_response.status != 200:
            # Already rolled over
            return

        soup = BeautifulSoup((await get_response.text()), 'html.parser')
        input = soup.find('input', attrs={'name': '_token'})
        try:
            token = input['value']
        except:
            raise ValueError('Could not find the required token on the daily rollover page.')

        await self.session.request(
            'POST', 'https://v2.horsereality.com/daily-rollover',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data={
                '_token': token,
                'url': 'https://www.horsereality.com',
            },
        )
