import time
import json
import aiohttp
import asyncio
import traceback
import networkx as nx
from bs4 import BeautifulSoup
from typing import List, Optional
from collections import defaultdict

from cmap import CMap
from entropy import debloat
from resource import Resource
from exceptions import DDoSException

sem = None
connector = None
site_uri = None
base_uri = None
memo = defaultdict(lambda: False)
c_map = None


async def crawl(url: str, parent: Optional[str] = None):
    global c_map, site_uri, base_uri, memo
    tasks = []
    is_done = False
    try:
        resource = Resource(url=url, base_url=base_uri, site_url=site_uri)
        if not memo.get(resource.url, False):
            memo[resource.url] = True
            await resource.parse(connector=connector)
        else:
            is_done = True
    except DDoSException:
        [task.cancel() for task in tasks if not task.done()]
        return
    except Exception as exc:
        print(f'Warning! Failed to parse {url}: {exc}')
        return
    if not parent:
        c_map.connect(None, resource.site_url)
        parent = resource.site_url
        site_uri = resource.site_url
        base_uri = resource.base_url
    if c_map.connected(parent, resource.url):
        return
    c_map.connect(parent, resource.url)
    if is_done:
        return
    for child_url in resource.links:
        if not c_map.connected(resource.url, child_url):
            async with sem:
                tasks.append(
                    asyncio.ensure_future(crawl(child_url, resource.url))
                )
    await asyncio.gather(*tasks)


async def main(url, t_cmp: CMap) -> CMap:
    global sem, connector, c_map
    c_map = t_cmp
    sem = asyncio.Semaphore(20)
    connector = aiohttp.TCPConnector(limit=20)
    try:
        await crawl(url)
    except Exception as e:
        raise e
    finally:
        await connector.close()
        return c_map


# if __name__ == '__main__':
#     uri = ''
#     t0 = time.time()
#     c_map = CMap()
#     try:
#         asyncio.run(main(uri))
#     except Exception as exc:
#         traceback.print_exc()
#         print('Preemptive termination', exc)
#     # graph: nx.DiGraph = c_map.load()
#     # c_map.edges = graph.edges()
#     graph = c_map.cart()
#     print(f'Crawled {c_map.size} internal linkmaps in {time.time() - t0} s')
#     c_map.edges = debloat(c_map.edges, nodes=len(graph.nodes()), threshold=(0.95, 0.95))
#     print(f'Caring {c_map.size} edges')
#     c_map.cart()
#     c_map.save()
#     c_map.plot()
