import os
import asyncio
import uvicorn
from app import app

HOST = os.getenv('SERVER_HOST', '0.0.0.0')
PORT = int(os.getenv('SERVER_PORT', 9271))

if __name__ == '__main__':
    print(f'Hosting web server at {HOST}:{PORT}')
    config = uvicorn.Config(app, host=HOST, port=PORT)
    server_app = uvicorn.Server(config=config)
    app.debug = True
    asyncio.run(server_app.serve())

