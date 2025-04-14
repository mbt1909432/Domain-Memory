from enum import IntEnum
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")

#TODO:可能可以把error改了
class CODE(IntEnum):
    # Success
    SUCCESS = 0

    # Client-side errors (4xx)
    BAD_REQUEST = 400  # The request could not be understood by the server due to malformed syntax.
    UNAUTHORIZED = 401  # The request requires user authentication.
    FORBIDDEN = 403  # The server understood the request, but is refusing to fulfill it.
    NOT_FOUND = 404  # The server has not found anything matching the Request-URI.
    METHOD_NOT_ALLOWED = 405  # The method specified in the Request-Line is not allowed for the resource identified by the Request-URI.
    CONFLICT = 409  # The request could not be completed due to a conflict with the current state of the resource.
    UNPROCESSABLE_ENTITY = 422  # The server understands the content type of the request entity, and the syntax is correct, but it was unable to process the contained instructions.

    # Server-side errors (5xx)
    INTERNAL_SERVER_ERROR = 500  # The server encountered an unexpected condition which prevented it from fulfilling the request.
    NOT_IMPLEMENTED = 501  # The server does not support the functionality required to fulfill the request.
    BAD_GATEWAY = 502  # The server, while acting as a gateway or proxy, received an invalid response from the upstream server.
    SERVICE_UNAVAILABLE = 503  # The server is currently unable to handle the request due to a temporary overloading or maintenance of the server.
    GATEWAY_TIMEOUT = 504  # The server, while acting as a gateway or proxy, did not receive a timely response from the upstream server.




class Response(BaseModel, Generic[T]):
    """
    统一响应模型
    - code: 1 表示成功，0 和其它数字表示失败
    - msg: 错误信息
    - data: 响应数据，可选
    """

    code: int
    msg: str
    data: Optional[T] = None

    @staticmethod
    def success(data: T = None) -> "Response[T]":
        """
        成功响应
        :param data: 响应数据（可选）
        :return: 成功的响应模型
        """
        return Response[T](code=1, msg="success", data=data)

    @staticmethod
    def error(msg: str = "unknown error", code: int = 0) -> "Response[T]":
        """
        错误响应
        :param msg: 错误信息
        :param code: 错误码，默认为 0
        :return: 错误的响应模型
        """
        return Response[T](code=code, msg=msg, data=None)

    def ok(self) -> bool:
        return self.code == CODE.SUCCESS

    def get_data(self) -> Optional[T]:
        return self.__data

    def get_message(self) -> str:
        if not self.ok():
            return f"Promise contains error: CODE {self.code}; MSG {self.msg}"
        return ""

