import aiohttp

__all__ = (
    'HorseRealityException',
    'HTTPException',
    'AuthenticationException',
    'PageAlertException',
    'RolloverRequired',
)


class HorseRealityException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class HTTPException(HorseRealityException):
    def __init__(self, response: aiohttp.ClientResponse, message: str):
        self.response = response
        self.status = response.status
        self.message = message
        super().__init__(f'{self.status}: {message}')


class AuthenticationException(HorseRealityException):
    def __init__(self, message: str = None):
        super().__init__(message or 'Failed to authenticate with Horse Reality.')


class PageAlertException(HorseRealityException):
    def __init__(self, message: str):
        super().__init__(message)


class RolloverRequired(HorseRealityException):
    def __init__(self, url: str, response: aiohttp.ClientResponse):
        self.url = url
        self.response = response
        self.rollover_url: str = response.headers.get('location')
        super().__init__('Failed to access %s because the client has not rolled over.' % url)
