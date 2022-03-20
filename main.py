import os
import asyncio
import uvicorn
from app import app

HOST = os.getenv('SERVER_HOST', '0.0.0.0')
PORT = int(os.getenv('SERVER_PORT', 9271))

if __name__ == '__main__':
    uvicorn.run(app, host=HOST, port=PORT)

