import asyncio

from .models import Horse
from .http import HTTPClient


__all__ = (
    'Client',
)


class Client:
    """Basic client for reading pages."""
    def __init__(self, *, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.http = HTTPClient(loop=self.loop)

    async def login(self, email: str, password: str):
        self.http.credentials['email'] = email
        self.http.credentials['password'] = password
        await self.http.login()

    async def get_horse(self, lifenumber: int) -> Horse:
        html_text = await self.http.get_horse(lifenumber)
        horse = await Horse._from_page(http=self.http, html_text=html_text)
        return horse
