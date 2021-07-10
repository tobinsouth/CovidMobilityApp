from typing import List

class ApiError:
    def __init__(self, code, field, message):
        self.code = code
        self.field = field
        self.message = message

    @classmethod
    def from_json(cls, data: dict):
        code = ' '.join(x.title() for x in data["code"].split('_'))
        field = data["field"]
        message = data["message"]
        return cls(code, field, message)
    
    def __str__(self):
        return '{0}: {1}'.format(self.code, self.message)

class Error:
    def __init__(self, code:str, message:str, errors:List[ApiError]):
        self.code = code
        self.message = message
        self.errors = errors

    @classmethod
    def from_json(cls, data: dict):
        code = ' '.join(x.title() for x in data["code"].split('_'))
        message = data["message"]
        errors = []
        if "errors" in data:
            errors = list(map(ApiError.from_json, data["errors"]))
        return cls(code, message, errors)
    
    def __str__(self):
        return '{0}: {1}'.format(self.code, self.message)