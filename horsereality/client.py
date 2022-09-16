from .models import Layer, Horse
from .http import HTTPClient


__all__ = (
    'Client',
)


class Client:
    """Basic client for reading pages."""
    def __init__(
        self,
        remember_cookie_name: str,
        remember_cookie_value: str,
        *,
        auto_rollover: bool = False,
    ):
        self.http = HTTPClient(
            remember_cookie_name,
            remember_cookie_value,
            auto_rollover=auto_rollover,
        )

    async def verify(self) -> None:
        """Prime the client for use."""
        await self.http.initialize()

    async def get_horse(self, lifenumber: int) -> Horse:
        """:class:`Horse`: Fetch a horse from Horse Reality."""
        html_text = await self.http.get_horse(lifenumber)
        horse = await Horse._from_page(http=self.http, html_text=html_text)
        return horse

    def create_layer(self, url: str) -> Layer:
        """:class:`Layer`: A helper function to create a :class:`Layer` from a one-off layer URL."""
        return Layer(http=self.http, url=url)

    async def rollover(self) -> None:
        """Complete the daily rollover required every day after 0:00 CET/CEST
        (i.e. the current timezone in the Netherlands depending on DST)."""
        await self.http.rollover()
