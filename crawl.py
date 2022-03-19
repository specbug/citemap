import time
import json
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Optional

from cmap import CMap
from resource import Resource


async def crawl(url: str, parent: Optional[str] = None):
    global c_map
    tasks = []
    try:
        resource = Resource(url=url)
        await resource.parse()
    except Exception as exc:
        print(f'Warning! Failed to parse {url}: {exc}')
        return
    if not parent:
        c_map.connect(None, resource.site_url)
        parent = resource.site_url
    if c_map.connected(parent, resource.url):
        return
    c_map.connect(parent, resource.url)
    for child_url in resource.links:
        if not c_map.connected(resource.url, child_url):
            tasks.append(crawl(child_url, resource.url))
    await asyncio.gather(*tasks)

uri = 'http://www.paulgraham.com/'
# TODO: support max breadth and depth
sweep_kernel = (4, 3)  # (breadth, depth)
t0 = time.time()
c_map = CMap()
asyncio.run(crawl(uri))
print(f'Crawled {c_map.size} internal linkmaps in {time.time() - t0} s')
print(c_map.edges)
