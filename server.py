import os
import time
import traceback
from urllib.parse import urljoin
from fastapi import APIRouter, Request
from starlette.responses import Response

from cmap import CMap
from crawl import main
from models import Arg
from entropy import debloat

router = APIRouter(prefix='/map')


@router.post('/')
async def link_map(argp: Arg):
    """
    Generate linkmap for a site.
    Args:
        argp: Args.
    Returns:
        filename
    """
    try:
        t0 = time.time()
        c_map = CMap()
        try:
            argp.url = urljoin(argp.url, '/')
            c_map = await main(url=argp.url, c_map=c_map)
        except Exception as exc:
            traceback.print_exc()
            print('Preemptive termination', exc)
        finally:
            if c_map.size > 0:
                # TODO: support cachestore
                # graph: nx.DiGraph = c_map.load()
                # c_map.edges = graph.edges()
                graph = c_map.cart()
                print(f'Crawled {c_map.size} internal linkmaps in {time.time() - t0} s')
                c_map.edges = debloat(c_map.edges, nodes=len(graph.nodes()), threshold=(0.95, 0.95))
                print(f'Caring {c_map.size} edges')
                c_map.cart()
                c_map.save()
                out_file = c_map.plot(filename=argp.filename, height=argp.height, width=argp.width)
                print(f'Generated internal linkmap for {argp.url}')
                return Response(content=os.path.basename(out_file), status_code=200)
            else:
                return Response(content='No internal linkmap found', status_code=404)
    except Exception as exc:
        traceback.print_exc()
        return Response(content=f'Error: {exc}', status_code=500)
