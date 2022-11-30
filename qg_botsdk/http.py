from ssl import create_default_context
from typing import Optional

from aiohttp import (
    ClientSession,
    ClientTimeout,
    FormData,
    TCPConnector,
    hdrs,
    multipart,
    payload,
)

from ._queue import Queue
from ._utils import exception_handler, general_header, retry_err_code

try:
    from importlib.metadata import version

    aio_version = version("aiohttp")
except (ImportError, ModuleNotFoundError):
    from pkg_resources import get_distribution

    aio_version = get_distribution("aiohttp").version

version_checking = (3, 8, 1)
for version_index in range(3):
    try:
        if int(aio_version[2 * version_index]) < version_checking[version_index]:
            print(
                f"\033[1;33m[warning] 注意你的aiohttp版本为{aio_version}，SDK建议升级到3.8.1，避免出现无法预计的错误\033[0m"
            )
            break
    except (ValueError, IndexError):
        pass


# derived from aiohttp FormData object, changing the return of _is_processed to allow retry using the same data object
class FormData_(FormData):
    def _gen_form_data(self) -> multipart.MultipartWriter:
        """Encode a list of fields using the multipart/form-data MIME format"""
        if self._is_processed:
            return self._writer
        for dispparams, headers, value in self._fields:
            try:
                if hdrs.CONTENT_TYPE in headers:
                    part = payload.get_payload(
                        value,
                        content_type=headers[hdrs.CONTENT_TYPE],
                        headers=headers,
                        encoding=self._charset,
                    )
                else:
                    part = payload.get_payload(
                        value, headers=headers, encoding=self._charset
                    )
            except Exception as exc:
                print(value)
                raise TypeError(
                    "Can not serialize value type: %r\n "
                    "headers: %r\n value: %r" % (type(value), headers, value)
                ) from exc

            if dispparams:
                part.set_content_disposition(
                    "form-data", quote_fields=self._quote_fields, **dispparams
                )
                assert part.headers is not None
                part.headers.popall(hdrs.CONTENT_LENGTH, None)

            self._writer.append_payload(part)

        self._is_processed = True
        return self._writer


class Session:
    def __init__(self, loop, is_retry, is_log_error, logger, max_concurrency, **kwargs):
        self._is_retry = is_retry
        self._is_log_error = is_log_error
        self._logger = logger
        self._queue = Queue(max_concurrency)
        self._kwargs = kwargs
        if kwargs.get("connector") is None:
            kwargs["connector"] = TCPConnector(
                limit=500, ssl=create_default_context(), force_close=True
            )
        self._session: Optional[ClientSession] = None
        self._timeout = ClientTimeout(total=20)
        self._loop = loop
        loop.run_until_complete(self._check_session())

    def __del__(self):
        if self._session and not self._session.closed:
            self._loop.run_until_complete(self._session.close())

    async def _check_session(self):
        if not self._session or self._session.closed:
            self._session = ClientSession(**self._kwargs)

    async def _warning(self, url, resp):
        self._logger.warning(
            f"HTTP API(url:{url})调用错误[{resp.status}]，详情：{await resp.text()}，"
            f'trace_id：{resp.headers.get("X-Tps-Trace-Id", None)}'
        )

    def __getattr__(self, item):
        if item in ("get", "post", "delete", "patch", "put"):

            def wrap(*args, **kwargs):
                try:
                    return self._queue.create_task(self._request, item, *args, **kwargs)
                except Exception as e:
                    self._logger.error(
                        f"HTTP API(url:{args[0]})调用错误，详情：{exception_handler(e)}"
                    )

            return wrap

    async def _request(self, method, url, retry=False, **kwargs):
        await self._check_session()
        kwargs["headers"] = kwargs.get("headers", general_header)
        resp = await self._session.request(method, url, timeout=self._timeout, **kwargs)
        if resp.ok:
            return resp
        if self._is_log_error and (not self._is_retry or retry):
            await self._warning(url, resp)
        if self._is_retry and not retry:
            if resp.headers["content-type"] == "application/json":
                json_ = await resp.json()
                if (
                    not isinstance(json_, dict)
                    or json_.get("code", None) not in retry_err_code
                ):
                    await self._warning(url, resp)
                    return resp
            return await self.request(method, url, True, **kwargs)
        return resp
