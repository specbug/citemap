import time
import json
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Optional

from cmap import CMap, CNode

headers = {'User-Agent': 'Mozilla/6.0'}


async def get_page(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.text()


def parse(soup: BeautifulSoup) -> dict:
    """Get name, title, & description of a page"""
    title, desc, name = None, None, None
    try:
        title = soup.find('title').text
        desc = soup.find('meta', {'name': 'description'})
        name = soup.find('meta', {'name': 'name'})
    except Exception:
        pass
    finally:
        return dict(
            title=title,
            desc=desc['content'] if desc else '',
            name=name['content'] if name else None
        )


async def crawl(base_url: str, url: str, parent: Optional[CNode], max_breadth: int, max_depth: int):
    global c_map
    if max_depth <= 0:
        return
    tasks = []
    c = 0
    try:
        page = await get_page(url)
        soup = BeautifulSoup(page, 'html.parser')
        meta = parse(soup)
    except Exception as exc:
        print(f'Warning! Failed to parse url: \n{exc}')
        return
    node = c_map.add(url, **meta)
    if parent:
        c_map.map(node, parent)
    else:
        c_map.root = node
    all_links = soup.find_all('a', href=True)
    for link in all_links:
        if c >= max_breadth:
            break
        if not link:
            continue
        link_url = link['href']
        if link_url.startswith('/'):
            link_url = base_url + link_url.lstrip('/')
        if link_url.startswith(base_url) and c_map.get(link_url) is None:
            tasks.append(crawl(base_url, link_url, node, max_breadth, max_depth - 1))
            c += 1
    await asyncio.gather(*tasks)


uri = 'https://www.yudkowsky.net/'
sweep_kernel = (4, 3)  # (breadth, depth)
t0 = time.time()
c_map = CMap()
asyncio.run(crawl(uri, uri, None, *sweep_kernel))
print(f'Crawled {c_map.size} internal linkmaps in {time.time() - t0} s')
root = c_map.root
print(f'citemap: \n{c_map.show(root)}')
json.dump(c_map.json(), open('citemap.json', 'w'), indent=2)
