class Response:
    def __init__(self, json_data=None, status_code=200):
        self._json = json_data
        self.status_code = status_code
    def json(self):
        return self._json
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception('HTTP error')

def get(*args, **kwargs):
    raise RuntimeError('requests.get called in stub')

def post(*args, **kwargs):
    raise RuntimeError('requests.post called in stub')
