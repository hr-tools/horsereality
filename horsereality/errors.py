
__all__ = (
    'HorseRealityException',
    'HTTPException',
    'AuthenticationException',
    'PageAlertException',
)


class HorseRealityException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class HTTPException(HorseRealityException):
    def __init__(self, response, message: str):
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
