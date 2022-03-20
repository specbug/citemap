import time
import traceback
from fastapi import APIRouter, Query
from starlette.responses import HTMLResponse

from cmap import CMap
from crawl import main
from models import Plot
from entropy import debloat

router = APIRouter(prefix='/map')


@router.get('/{url}', response_class=HTMLResponse)
async def link_map(
        url: str,
        plot_config: Plot
):
    """
    Generate linkmap for a site.
    Args:
        url: base url.
        plot_config: Plot object.
    Returns:
        redirects to linkmap
    """
    t0 = time.time()
    c_map = CMap()
    try:
        await main(url=url)
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
            out_file = c_map.plot()
            print(f'Generated internal linkmap for {url}')
            of = open(out_file, 'rb').read()
            return HTMLResponse(content=of, status_code=200)


