from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from rpc.get_output import get_output
from utils.rpc_router import RpcRouter

async def homepage(request):
    return JSONResponse({'hello': 'world'})

router = RpcRouter(app_name="example-test", routes=[
    get_output,
])

if True:
    router.write()

app = Starlette(debug=True, routes=[
    Route('/', homepage),
    *router.get_routes(),
])