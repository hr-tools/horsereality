import aiohttp

__all__ = (
    'HorseRealityException',
    'ClientNotInitialized',
    'HTTPException',
    'RateLimitExceeded',
    'AuthenticationException',
    'PageAlertException',
    'RolloverRequired',
)


class HorseRealityException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ClientNotInitialized(HorseRealityException):
    def __init__(self):
        super().__init__(
            'This client is not yet initialized (or it was forcefully uninitialized), '
            'so it cannot make requests to Horse Reality. Try again later.'
        )


class HTTPException(HorseRealityException):
    def __init__(self, response: aiohttp.ClientResponse, message: str):
        self.response = response
        self.status = response.status
        self.message = message
        super().__init__(f'{self.status}: {message}')


class RateLimitExceeded(HorseRealityException):
    def __init__(self, response: aiohttp.ClientResponse, message: str = None):
        self.response = response
        self.status = response.status
        self.message = message or 'Client is rate limited or banned by Cloudflare. Try again later.'
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
