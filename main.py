import os
import asyncio
import uvicorn
from app import app

HOST = os.getenv('SERVER_HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 9271))

if __name__ == '__main__':
    print(f'Starting server at {HOST}:{PORT}')
    uvicorn.run(app, host=HOST, port=PORT)

