class RequestInfo:
    url = None
    method = "get"
    headers = None
    data = None
    params = None
    cookies = None
    timestamp = None
    is_matched = False

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def to_request_parameters(self):
        return {k: v for k, v in self.__dict__.items() if k not in ("timestamp", "is_matched")}