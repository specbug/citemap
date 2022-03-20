import os
import time
import traceback
from urllib.parse import urljoin
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import Response, HTMLResponse

from cmap import CMap
from crawl import main
from models import Arg
from entropy import debloat
from config import STATIC_FOLDER

router = APIRouter(prefix='/map')
templates = Jinja2Templates(directory=STATIC_FOLDER)


@router.post('/{url}', response_class=HTMLResponse)
async def link_map(
        request: Request,
        argp: Arg
):
    """
    Generate linkmap for a site.
    Args:
        request: Request object.
        argp: Args.
    Returns:
        redirects to linkmap.
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
                return templates.TemplateResponse(os.path.basename(out_file), {'request': request})
            else:
                return HTMLResponse(content='No internal linkmap found', status_code=200)
    except Exception as exc:
        traceback.print_exc()
        return HTMLResponse(content=f'Error: {exc}', status_code=500)
