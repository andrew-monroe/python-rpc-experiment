from starlette.requests import Request

class AuthContext:
    def __init__(self, request: Request):
        self._request = request

    def get_url(self):
        return self._request.url
