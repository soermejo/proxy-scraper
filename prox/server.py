from aiohttp import web
import random, asyncio, logging
from prox.checker import Checker, Proxy


# ip = lambda: ".".join(map(str, (random.randint(0, 255) for _ in range(4))))
# port = lambda: str(random.randint(0, 99999))

prox = Checker(refresh_time=60)

async def get_proxy(request):
    proxy = await prox.get_proxy()
    data = {'ip':proxy.ip, 'port':proxy.port, 'fails':proxy.fails}
    return web.json_response(data)

async def fail_proxy(request):
    data = await request.json()
    print(data)
    ip, port, fails = data["ip"], data["port"], data["fails"]
    await prox.fail(Proxy(ip, port, fails))

    data = {'status':'ok'}

    return web.json_response(data)

async def good_proxy(request):
    data = await request.json()
    ip, port, fails = data["ip"], data["port"], data["fails"]
    live = await prox.clear_fails(Proxy(ip, port, fails))

    data = {'status':'ok' if live else 0}
    
    return web.json_response(data)



app = web.Application()
app.add_routes([web.get('/proxy', get_proxy),
                web.post('/fail', fail_proxy),
                web.post('/good', good_proxy)])


loop = asyncio.get_event_loop()

asyncio.gather(
    prox.start()
   
)

tasks = asyncio.gather(
    web.run_app(app)
   
)
loop.run_until_complete(tasks)