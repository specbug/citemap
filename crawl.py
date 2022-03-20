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

site_uri = None
base_uri = None
memo = defaultdict(lambda: False)


async def crawl(url: str, parent: Optional[str] = None, c_map: CMap = None) -> CMap:
    global site_uri, base_uri, memo
    tasks = []
    is_done = False
    try:
        resource = Resource(url=url, base_url=base_uri, site_url=site_uri)
        if not memo.get(resource.url, False):
            memo[resource.url] = True
            await resource.parse()
        else:
            is_done = True
    except DDoSException:
        [task.cancel() for task in tasks if not task.done()]
        return c_map
    except Exception as exc:
        print(f'Warning! Failed to parse {url}: {exc}')
        return c_map
    if not parent:
        c_map.connect(None, resource.site_url)
        parent = resource.site_url
        site_uri = resource.site_url
        base_uri = resource.base_url
    if c_map.connected(parent, resource.url):
        return c_map
    c_map.connect(parent, resource.url)
    if is_done:
        return c_map
    for child_url in resource.links:
        if not c_map.connected(resource.url, child_url):
            tasks.append(
                asyncio.ensure_future(crawl(child_url, resource.url, c_map=c_map))
            )
    await asyncio.gather(*tasks)
    return c_map


async def main(url, c_map: CMap) -> CMap:
    try:
        await crawl(url, c_map=c_map)
    except Exception as e:
        raise e
    finally:
        return c_map


# if __name__ == '__main__':
#     uri = ''
#     t0 = time.time()
#     g_c_map = CMap()
#     try:
#         asyncio.run(main(uri, g_c_map))
#     except Exception:
#         print('Preemptive termination')
#         traceback.print_exc()
#     # graph: nx.DiGraph = g_c_map.load()
#     # g_c_map.edges = graph.edges()
#     graph = g_c_map.cart()
#     print(f'Crawled {g_c_map.size} internal linkmaps in {time.time() - t0} s')
#     g_c_map.edges = debloat(g_c_map.edges, nodes=len(graph.nodes()), threshold=(0.95, 0.95))
#     print(f'Caring {g_c_map.size} edges')
#     g_c_map.cart()
#     g_c_map.save()
#     g_c_map.plot()
