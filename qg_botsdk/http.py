from asyncio import AbstractEventLoop, get_event_loop
from asyncio import sleep as async_sleep
from time import time
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

from ._api_model import StrPtr
from ._queue import Queue
from ._utils import exception_handler, general_header, retry_err_code

try:
    from pkg_resources import get_distribution, parse_version

    aio_version = get_distribution("aiohttp").version

    if parse_version(aio_version) < parse_version("3.8.1"):
        print(
            f"\033[1;33m[warning] 注意你的aiohttp版本为{aio_version}，SDK建议升级到3.8.1以上，避免出现无法预计的错误\033[0m"
        )
except (ImportError, ModuleNotFoundError):
    from importlib.metadata import version

    def __to_int(s):
        ret = ""
        for i in s:
            if i.isdigit():
                ret += i
        return int(ret) if ret else 0

    def __simple_version_cmp(version: str, target: str):
        version_cmp = zip(version.split("."), target.split("."))
        for a, b in version_cmp:
            if __to_int(a) < __to_int(b):
                return False
        return True

    aio_version = version("aiohttp")
    if not __simple_version_cmp(aio_version, "3.8.1"):
        print(
            f"\033[1;33m[warning] 注意你的aiohttp版本为{aio_version}，SDK建议升级到3.8.1以上，避免出现无法预计的错误\033[0m"
        )


# derived from aiohttp FormData object, changing the return of _is_processed to allow retry using the same data object
class FormData_(FormData):
    def _gen_form_data(self) -> multipart.MultipartWriter:
        """Encode a list of fields using the multipart/form-data MIME format"""
        if self._is_processed:
            return self._writer
        for dispparams, headers, value in self._fields:
            try:
                # handle custom datatype in sdk
                if isinstance(value, StrPtr):
                    value = value.value
                if value is None:
                    continue

                # original process
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
                e = TypeError(
                    "Can not serialize value type: %r\n "
                    "headers: %r\n value: %r" % (type(value), headers, value)
                )
                print(e)
                raise e from exc

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
    def __init__(
        self,
        bot_id: str,
        bot_token: str,
        bot_secret: str,
        access_token: StrPtr,
        loop: AbstractEventLoop,
        is_retry,
        is_log_error,
        logger,
        max_concurrency,
        timeout,
        **kwargs,
    ):
        self._bot_id = bot_id
        self._bot_token = bot_token
        self._bot_secret = bot_secret
        self._access_token = access_token
        self._access_token_expire = 0
        self._access_token_last_update = time()
        self._is_retry = is_retry
        self._is_log_error = is_log_error
        self._logger = logger
        self._queue = Queue(max_concurrency)
        if not kwargs.get("connector", None):
            if not loop.is_running():
                kwargs["connector"] = loop.run_until_complete(self._create_connector())
            else:

                def __callback(f):
                    self._kwargs["connector"] = f.result()

                loop.create_task(self._create_connector()).add_done_callback(__callback)
        self._kwargs = kwargs
        self._session: Optional[ClientSession] = None
        self._timeout = ClientTimeout(total=timeout)
        self._loop = loop
        if not loop.is_running():
            loop.run_until_complete(self._check_session())
        else:
            loop.create_task(self._check_session())
        loop.create_task(self._access_token_loop())

    def __del__(self):
        if self._session and not self._session.closed:
            try:
                loop = get_event_loop()
                if loop.is_running():
                    loop.create_task(self._session.close())
                else:
                    loop.run_until_complete(self._session.close())
            except Exception:
                pass

    @staticmethod
    async def _create_connector(*args, **kwargs):
        return TCPConnector(*args, **kwargs)

    async def _check_session(self):
        if not self._bot_secret:
            headers = {"Authorization": f"Bot {self._bot_id}.{self._bot_token}"}
        else:
            headers = {
                "Authorization": self._access_token.value,
                "X-Union-Appid": self._bot_id,
            }
        if not self._session or self._session.closed:
            self._session = ClientSession(
                timeout=self._timeout, headers=headers, **self._kwargs
            )
            self._session.headers.update(general_header)

    async def _access_token_loop(self):
        if not self._bot_secret:  # 无需获取access_token
            return
        self._access_token_last_update = time()
        while True:
            if self._access_token_expire > 0:
                await async_sleep(10)
                self._access_token_expire -= time() - self._access_token_last_update
                self._access_token_last_update = time()
            else:
                await self._request_access_token()

    async def _request_access_token(self):
        if not self._bot_secret:  # 无需获取access_token
            return
        self._access_token_expire = 30  # if fail, retry after 30s
        resp = await self._session.post(
            "https://bots.qq.com/app/getAppAccessToken",
            json={"appId": self._bot_id, "clientSecret": self._bot_secret},
        )
        if not resp.ok:
            content = await resp.text()
            self._logger.warning(
                f"HTTP API(url:https://bots.qq.com/app/getAppAccessToken)调用错误[{resp.status}]，详情：{content}，"
                f'trace_id：{resp.headers.get("X-Tps-Trace-Id", None)}'
            )
            return
        json_ = await resp.json()
        access_token = json_.get("access_token", None)
        expire = int(json_.get("expires_in", 0))
        if access_token and expire:
            self._access_token.value = f"QQBot {access_token}"
            self._access_token_expire = (
                expire - 59
            )  # can get new token 1 min before expire
            self._session.headers["Authorization"] = self._access_token.value
        else:
            self._logger.warning(
                f"HTTP API(url:https://bots.qq.com/app/getAppAccessToken)调用错误[{resp.status}]，详情：{json_}，"
                f'trace_id：{resp.headers.get("X-Tps-Trace-Id", None)}'
            )

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
        if self._bot_secret and (
            not self._access_token.value or self._access_token_expire <= 0
        ):
            await self._request_access_token()
        resp = await self._session.request(method, url, **kwargs)
        if resp.ok:
            return resp
        if self._is_log_error and (not self._is_retry or retry):
            await self._warning(url, resp)
        if self._is_retry and not retry:
            if resp.headers.get("content-type", "") == "application/json":
                json_ = await resp.json()
                if (
                    not isinstance(json_, dict)
                    or json_.get("code", None) not in retry_err_code
                ):
                    await self._warning(url, resp)
                    return resp
            await async_sleep(0.05)
            return await self._request(method, url, True, **kwargs)
        return resp
