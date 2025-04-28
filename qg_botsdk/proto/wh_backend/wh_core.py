#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import json
import os
import ssl
import sys
import time
import traceback
from argparse import ArgumentParser
from collections import Counter

import certifi
from aiohttp import ClientSession, TCPConnector, web
from ed25519 import SigningKey

redirect_table = {}
redirect_path_table = Counter()
redirect_table_lock = asyncio.Lock()

version = None


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--version", type=str, required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--log", type=str, required=True)
    parser.add_argument("--ssl_cert", type=str, required=False)
    parser.add_argument("--ssl_cert_key", type=str, required=False)
    return parser.parse_args()


async def check_backend_exists(args: ArgumentParser):
    proto = "https" if args.ssl_cert and args.ssl_cert_key else "http"
    try:
        async with ClientSession(
            connector=TCPConnector(
                ssl=ssl.create_default_context(cafile=certifi.where())
            )
        ) as session:
            async with session.head(
                f"{proto}://localhost:{args.port}/qg_botsdk?version={args.version}"
            ) as resp:
                return resp.status == 200
    except Exception:
        return False


async def check_validation(jbody: dict, bot_secret: str):
    if jbody.get("op") != 13:
        return None
    data = jbody.get("d")
    sign_key = SigningKey.from_seed(bot_secret.encode("ascii"))
    msg: str = data.get("event_ts") + data.get("plain_token")
    signature = sign_key.sign(msg.encode("ascii")).hex()
    return json.dumps(
        {
            "plain_token": data.get("plain_token"),
            "signature": signature,
        }
    )


async def ping_handle(request: web.Request):
    new_version = request.query.get("version", None)
    if not new_version:
        raise web.HTTPBadRequest(reason="lack of version argument")
    print(f"ping: {new_version} == {version}, {redirect_path_table}")
    if new_version != version or not redirect_path_table:
        # Two cases to terminate the backend:
        # 1. version mismatch, this backend is outdated
        # 2. no bot currently connected and new search request is established
        print("new connection requested, closing this app")
        raise web.GracefulExit()
    raise web.HTTPOk()


async def ws_recv_loop(ws: web.WebSocketResponse, msg_queue: asyncio.Queue):
    while not ws.closed:
        try:
            await ws.receive()  # handling auto ping pong
        except Exception as e:
            print("recv loop:", repr(e))
            traceback.print_exc()
    msg_queue.put_nowait(None)  # let the ctrl_handle know the ws is closed


async def ws_send_loop(
    ws: web.WebSocketResponse, msg_queue: asyncio.Queue, request: web.Request
):
    ws = web.WebSocketResponse(autoping=True, autoclose=True)
    await ws.prepare(request)
    request.app["websockets"].append(ws)
    recv_task = asyncio.get_event_loop().create_task(ws_recv_loop(ws, msg_queue))
    try:
        while not ws.closed:
            msg = await msg_queue.get()
            if msg is None:
                break
            # print(f"ws send({request.path}): {msg}")
            await ws.send_str(msg)
    finally:
        request.app["websockets"].remove(ws)
        recv_task.cancel()
    return ws


async def ctrl_handle(request: web.Request):
    # setup new robot redirect ws connection
    # /qg_botsdk/{id}?secret={secret}&path={path}
    path_items = request.path.lstrip("/").split("/")
    if len(path_items) != 2:
        raise web.HTTPBadRequest(
            reason="path format: /qg_botsdk/{id}, current: " + request.path
        )
    bot_id = path_items[1]
    bot_secret = request.query["secret"]
    path = request.query["path"]
    if not bot_id:
        raise web.HTTPBadRequest(reason="lack of bot_id")
    if not bot_secret:
        raise web.HTTPBadRequest(reason="lack of bot_secret")
    if not path:
        raise web.HTTPBadRequest(reason="lack of path")
    if not path.startswith("/"):
        raise web.HTTPBadRequest(reason="path must start with /")

    if request.method != "GET":  # HEAD can be used to check if connection is available
        raise web.HTTPOk()

    msg_queue = asyncio.Queue()
    async with redirect_table_lock:
        if bot_id in redirect_table:
            redirect_table[bot_id][0] = bot_secret
            redirect_table[bot_id][1].add(msg_queue)
            redirect_table[bot_id][2].add(path)
        else:
            redirect_table[bot_id] = [bot_secret, {msg_queue}, {path}]
        redirect_path_table[path] += 1

    try:
        # upgrade to websocket, get data from queue and send back
        print(f"ws connected: {bot_id}::{path}")
        ws = await ws_send_loop(request, msg_queue, request)
        return ws

    except Exception as e:
        raise web.HTTPBadRequest(reason=repr(e))
    finally:
        async with redirect_table_lock:
            if bot_id in redirect_table:
                redirect_table[bot_id][1].remove(msg_queue)
                if not redirect_table[bot_id][1]:
                    del redirect_table[bot_id]
            redirect_path_table[path] -= 1
            if redirect_path_table[path] <= 0:
                del redirect_path_table[path]
        print(f"ws closed: {bot_id}::{path}")


def remote_sign_check(sign: str, bot_id: str, bot_secret: str):
    sign_key = SigningKey.from_seed(bot_secret.encode("ascii"))
    real_sign = sign_key.sign(bot_id.encode("ascii")).hex()
    return sign == real_sign


async def remote_ctrl_handle(request: web.Request):
    # setup new robot redirect ws connection
    # /qg_botsdk_remote/{id}?sign={signature}
    path_items = request.path.lstrip("/").split("/")
    if len(path_items) != 2 and len(path_items) != 3:
        raise web.HTTPBadRequest(
            reason="path format: /qg_botsdk_remote/{id}, current: " + request.path
        )
    if len(path_items) == 3 and path_items[2] != "ping":
        raise web.HTTPBadRequest(
            reason="path format: /qg_botsdk_remote/{id}/ping, current: " + request.path
        )

    bot_id = path_items[1]
    if not bot_id:
        raise web.HTTPBadRequest(reason="lack of bot_id")
    if bot_id not in redirect_table:
        raise web.HTTPNotFound(reason="remote bot not found")

    signature = request.query.get("sign", None)
    if not signature:
        raise web.HTTPBadRequest(reason="lack of signature")
    if not remote_sign_check(signature, bot_id, redirect_table[bot_id][0]):
        raise web.HTTPUnauthorized(
            reason="signature check failed, please check for id and secret"
        )

    if len(path_items) == 3:  # used to check if parameters is available
        raise web.HTTPOk()

    msg_queue = asyncio.Queue()
    async with redirect_table_lock:
        redirect_table[bot_id][1].add(msg_queue)
        for path in redirect_table[bot_id][2]:
            redirect_path_table[path] += 1
    try:
        # upgrade to websocket, get data from queue and send back
        print(f"remote ws connected: {bot_id}")
        ws = await ws_send_loop(request, msg_queue, request)
        return ws
    except Exception as e:
        raise web.HTTPBadRequest(reason=repr(e))
    finally:
        async with redirect_table_lock:
            redirect_table[bot_id][1].remove(msg_queue)
            for path in redirect_table[bot_id][2]:
                redirect_path_table[path] -= 1
                if redirect_path_table[path] <= 0:
                    del redirect_path_table[path]
        print(f"remote ws closed: {bot_id}")


async def redirect_handle(request: web.Request):
    if request.headers.get("User-Agent") != "QQBot-Callback":
        raise web.HTTPUnauthorized()
    bot_id = request.headers.get("X-Bot-Appid", None)
    if bot_id not in redirect_table:
        raise web.HTTPNotFound(reason="Bot not found")
    # send body to queue
    try:
        body = await request.text()
        resp = await check_validation(json.loads(body), redirect_table[bot_id][0])

        if resp is None:  # not validation request, push to clients
            for queue in redirect_table[bot_id][1]:
                await queue.put(body)

        return web.Response(status=200, body=resp)
    except Exception as e:
        print(repr(e))
        traceback.print_exc()
        raise web.HTTPBadRequest(reason=repr(e))


async def dispatch_handler(request: web.Request):
    # print(request.method, request.path)
    if request.path == "/qg_botsdk":
        return await ping_handle(request)
    elif request.path.startswith("/qg_botsdk_remote"):
        return await remote_ctrl_handle(request)
    elif request.path.startswith("/qg_botsdk"):
        return await ctrl_handle(request)
    elif request.path in redirect_path_table:
        return await redirect_handle(request)
    else:
        raise web.HTTPNotFound(reason="Not Found, path: " + request.path)


async def on_shutdown(app):
    for ws in app["websockets"]:
        await ws.close(code=web.WSCloseCode.GOING_AWAY, message="Server shutdown")


async def create_backend(args: ArgumentParser):
    app = web.Application()
    app["websockets"] = app.get("websockets", [])
    app.on_shutdown.append(on_shutdown)
    app.add_routes([web.route("*", "/{tail:.*}", dispatch_handler)])
    runner = web.AppRunner(app)
    if args.ssl_cert and args.ssl_cert_key:
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(args.ssl_cert, args.ssl_cert_key)
    else:
        ssl_context = None
    while True:
        try:
            await runner.setup()
            site = web.TCPSite(runner, port=args.port, ssl_context=ssl_context)
            print("Backend started")
            await site.start()
            await site._server.serve_forever()
        except Exception as e:
            print(f"Backend error: {repr(e)}")
            traceback.print_exc()
            await asyncio.sleep(3)
        finally:
            await runner.cleanup()


async def main():
    global version
    args = parse_args()

    # redirect all print() to log file
    dirs = os.path.dirname(args.log)
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    sys.stdout = open(args.log, "w", 1)
    sys.stderr = sys.stdout
    try:
        version = args.version
        if await check_backend_exists(args):
            print("already exists same application")
            time.sleep(3)
        else:
            # send signal to parent process to notify the new backend is ready
            await create_backend(args)
    finally:
        sys.stdout.close()
        try:
            os.remove(args.log)
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
