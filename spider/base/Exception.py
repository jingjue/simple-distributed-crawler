# -*-coding:utf-8-*-

class MeanNumException(Exception):
    def __init__(self, message):
        super().__init__(message)


class NameException(Exception):
    def __init__(self, message):
        super().__init__(message)


class BriefException(Exception):
    def __init__(self, message):
        super().__init__(message)


class RespError(Exception):
    def __init__(self, resp, message=None):
        super(RespError, self).__init__()
        self.resp = resp
        if message == None:
            message = f"response.status:{resp.status_code} url:{resp._get_url()}"


class CookieError(Exception):
    def __init__(self, cookie):
        super(CookieError, self).__init__()


class NoHeaderError(Exception):
    def __init__(self, info: dict):
        super(NoHeaderError, self).__init__()
