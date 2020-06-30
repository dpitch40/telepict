#!/usr/bin/env python

# WS server that sends messages at random intervals

import asyncio
import datetime
import random
import json

import websockets

from config import Config, env

handlers = dict()

def handler(key):
    def wrapper(func):
        handlers[key] = func
        return func
    return wrapper

STATE = {"value": 0}
USERS = set()

def state_event():
    return json.dumps({'action': 'state', 'payload': {'count': STATE['value'],
                                                      'users': len(USERS)}})

async def notify_state():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = state_event()
        await asyncio.wait([user.send(message) for user in USERS])

async def register(websocket):
    USERS.add(websocket)
    await notify_state()

async def unregister(websocket):
    USERS.remove(websocket)
    await notify_state()

@handler('minus')
def minus():
    STATE['value'] -= 1

@handler('plus')
def plus():
    STATE['value'] += 1

async def counter(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        await websocket.send(state_event())
        async for message in websocket:
            data = json.loads(message)
            action = data.pop('action');
            if action in handlers:
                handlers[action](**data)
                await notify_state()
            else:
                print(f"unsupported event: {data}")
    finally:
        await unregister(websocket)

def main():
    start_server = websockets.serve(counter, "localhost", Config.WS_PORT)
    print(f'Running on ws://localhost:{Config.WS_PORT}')

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    main()
