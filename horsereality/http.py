import aiohttp
from bs4 import BeautifulSoup

from . import __version__
from .errors import *


class HTTPClient:
    def __init__(self, *, loop):
        self.loop = loop
        self.credentials = {
            'email': None,
            'password': None,
        }
        self.session = None
        self.cookies = {}

        # We have to provide a user agent in order to avoid getting blocked from creating sessions.
        # 
        self.user_agent = f'HorseReality/{__version__}'

    async def request(self, method: str, path: str, *, v2: bool = False, **kwargs):
        url = f'https://{"v2" if v2 else "www"}.horsereality.com{path}'

        # We want to default to false in case we get a 302
        return_headers = kwargs.pop('return_headers', False)
        kwargs['allow_redirects'] = kwargs.pop('allow_redirects', False)
        if self.cookies:
            kwargs['headers'] = {
                'Cookie': '; '.join(f'{key}={value}' for key, value in self.cookies.items()),
                **kwargs.pop('headers', {}),
            }

        tries = 0
        async def perform():
            response = await self.session.request(method=method, url=url, **kwargs)

            if (
                response.headers.get('location') in (
                    'https://v2.horsereality.com/error-404',
                    'https://www.horsereality.com/error-404',
                )
                or response.status == 404
            ):
                # HR does not properly return a 404 page and instead cycles the client between two URLs,
                # so we have to handle this ourselves.
                raise HTTPException(response, f'Page not found: {url}')

            elif response.status == 302:
                # We are not authenticated properly
                if tries > 5:
                    # Give up
                    raise AuthenticationException('Failed to re-authorize 5 times in a row.')

                await self.login()
                await perform()
                tries += 1

            elif response.status == 429:
                # We are unlikely to be rate limited, but back-off just in case anyway.
                if tries > 5:
                    # Give up
                    raise HTTPException(response, 'Failed to back-off a rate limit 5 times in a row.')

                await asyncio.sleep(3)
                await perform()
                tries += 1

            if (response.headers['Content-Type'] or '').split('/')[0] == 'image':
                data = await response.read()
            else:
                data = await response.text()

            return {'status': response.status, 'data': data, 'headers': (response.headers if return_headers else None)}
        return await perform()

    async def login(self):
        self.session = self.session if self.session and not self.session.closed else aiohttp.ClientSession(headers={'User-Agent': self.user_agent})

        # HR generates a unique token on each page load of /login for XSRF protection, and requires it when actually logging in.
        # They provide this token in a cookie (XSRF-TOKEN) on pages viewable without authorization, but it is not usable directly.
        get_response = await self.session.request(
            method='GET',
            url='https://v2.horsereality.com/login',
        )
        soup = BeautifulSoup((await get_response.text()), 'html.parser')
        inputs = soup.find_all('input', attrs={'name': '_token', 'type': 'hidden'})
        try:
            token = inputs[0]['value']
        except:
            raise AuthenticationException()

        # We found the token, now to log in with it as well as our static credentials
        # self.request is not used here because we want to avoid its HTTP 302 logic, which assumes we are already logged in.
        post_response = await self.session.request(
            method='POST',
            url='https://v2.horsereality.com/login',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data={
                **self.credentials,
                '_token': token,
            },
            allow_redirects=False,
            # When redirects are enabled, we will land on /horses,
            # but this is not what we want because then the location
            # header is not present.
        )

        if post_response.status != 302:
            raise AuthenticationException('Invalid credentials.')

        # We make yet another request--to the auth token "page"--to finally get our cookie.
        # self.request is not used here because we want to use whatever URL HR throws at us, which _could_ change unexpectedly.
        cookie_response = await self.session.request(
            method='GET',
            url=post_response.headers['location'],  # https://www.horsereality.com/?v2_auth_token=...
            allow_redirects=False,
        )

        try:
            self.cookies['horsereality'] = cookie_response.cookies['horsereality'].value
        except KeyError as exc:
            raise AuthenticationException()

    async def get_horse(self, lifenumber: int):
        data = await self.request('GET', f'/horses/{lifenumber}/')
        return data['data']
