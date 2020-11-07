from prox.scraper import Scraper, Proxies, Proxy
import asyncio, aiohttp

COUNT = 0
try:
    from asyncio.exceptions import TimeoutError
except ModuleNotFoundError:
    from concurrent.futures._base import TimeoutError

class Checker(Proxies):
    def __init__(self, maxfails=3, refresh_time=60):
        self.refresh_time = refresh_time
        
        super(Checker, self).__init__(maxfails=maxfails)
        self.scraper = Scraper()
        timeout = aiohttp.ClientTimeout(sock_connect=10)
        self.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False, limit=1000), timeout=timeout)

    async def check_and_update(self, proxy: Proxy) -> bool:
        try:
            async with self.session.get('https://api.ipify.org?format=json', proxy=f"http://{proxy.ip}:{proxy.port}") as response:
                html = await response.json()
                if html and html["ip"]:
                    print(f"[!] {proxy.ip}:{proxy.port}")
                    COUNT+=1
                    await self.add_proxy(Proxy(proxy.ip, proxy.port))
                    return True
                #print(f"[x] {proxy.ip}:{proxy.port}, {html}")
                return False

        except aiohttp.ClientError as e:
            #print("Client Exception", e)
            return False

        except TimeoutError as e:
            #print("Timeout Exception", e)
            return False

    async def refresh(self):
        updated_proxies = await self.scraper.update_proxies()
        proxy_to_check = updated_proxies - self.proxies
        res = await asyncio.gather(*[self.check_and_update(proxy) for proxy in proxy_to_check])
        print(f"Found {sum(res)}/{len(proxy_to_check)} working proxies!")


    async def start(self):
        while True:
            await self.refresh() 
            print("done")
            await asyncio.sleep(self.refresh_time)
            print("gode")
    
loop = asyncio.get_event_loop()

loop.run_until_complete(Checker(refresh_time=60).start())