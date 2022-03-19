import time
import json
import aiohttp
import asyncio
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
tasks = []
site_uri = None
base_uri = None
nodes = defaultdict(lambda: False)


async def crawl(url: str, parent: Optional[str] = None):
    global c_map, site_uri, base_uri, nodes, tasks
    try:
        resource = Resource(url=url, base_url=base_uri, site_url=site_uri)
        await resource.parse(connector=connector)
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
    if nodes[resource.url]:
        return
    nodes[resource.url] = True
    for child_url in resource.links:
        if not c_map.connected(resource.url, child_url):
            async with sem:
                tasks.append(
                    asyncio.ensure_future(crawl(child_url, resource.url))
                )
    await asyncio.gather(*[t for t in tasks if not t.done()])


async def main(url):
    global sem, connector
    sem = asyncio.Semaphore(20)
    connector = aiohttp.TCPConnector(limit=20)
    await crawl(url)
    await connector.close()


if __name__ == '__main__':
    uri = 'https://www.waitbutwhy.com/'
    # TODO: support max breadth and depth
    sweep_kernel = (4, 3)  # (breadth, depth)
    t0 = time.time()
    c_map = CMap()
    # try:
    #     asyncio.run(main(uri))
    # except Exception:
    #     print('Preemptive termination')
    graph: nx.DiGraph = c_map.load('waitbutwhy.gpickle')
    c_map.edges = graph.edges()
    graph = c_map.cart()
    c_map.edges = debloat(c_map.edges, nodes=len(graph.nodes()), threshold=(0.95, 0.95))
    print(f'Crawled {c_map.size} internal linkmaps in {time.time() - t0} s')
    c_map.cart()
    c_map.save('waitbutwhy.gpickle')
    c_map.plot('waitbutwhy.html')
