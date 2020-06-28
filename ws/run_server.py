# WS server example

import asyncio
import websockets

from config import Config, env

async def hello(websocket, path):
    name = await websocket.recv()
    print(f"< {name}")

    greeting = f"Hello {name}!"

    await websocket.send(greeting)
    print(f"> {greeting}")

def main():
    start_server = websockets.serve(hello, "localhost", Config.WS_PORT)
    print(f'Listening on ws://localhost:{Config.WS_PORT}')

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    main()
