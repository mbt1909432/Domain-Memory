from fastapi import FastAPI, HTTPException, Request
from starlette.responses import JSONResponse
from utils.config import LOG

from core.response_model import Response


def register_exception_handlers(app: FastAPI):
    """
    注册全局异常处理器
    """

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        捕获 FastAPI 内置的 HTTPException
        """
        LOG.error(f"HTTPException: {exc}")
        return JSONResponse(
            status_code=200,
            content=Response.error(msg=exc.detail, code=0).model_dump(),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """
        捕获所有未处理的异常
        """
        err_msg = f"Internal Server Error: {exc}"
        LOG.error(err_msg)
        return JSONResponse(
            status_code=200,
            content=Response.error(msg=err_msg, code=0).model_dump(),
        )
