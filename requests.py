class Response:
    def __init__(self, json_data=None, status_code=200):
        self._json = json_data or {}
        self.status_code = status_code

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RequestException(f"Status {self.status_code}")


def post(*args, **kwargs):
    raise NotImplementedError("requests.post is not implemented in the stub")


def get(*args, **kwargs):
    raise NotImplementedError("requests.get is not implemented in the stub")


class RequestException(Exception):
    pass

class exceptions:
    RequestException = RequestException
