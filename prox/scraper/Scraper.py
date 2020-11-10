from prox.providers import Provider, Providers
import aiohttp, asyncio, random, logging

class Proxy:
    def __init__(self, ip, port, fails=0):
        self.ip = ip
        self.port = port
        self.fails = fails

    def __eq__(self, other):
        return self.ip == other.ip and self.port == other.port

    def __hash__(self):
        return hash(self.ip + self.port)

class Proxies:

    def __init__(self, maxfails=3):
        self.proxies = set()
        self.maxfails = maxfails
        self.lock = asyncio.Lock()

    async def add_proxy(self, proxy: Proxy):
        self.proxies.add(proxy)

    async def clear_fails(self, proxy: Proxy):
        async with self.lock:
            if proxy not in self.proxies:
                return await self.add_proxy(proxy) # Already removed but adding again as working
            self.proxies.remove(proxy)
            proxy.fails = 0 # Modify value
            await self.add_proxy(proxy)

    async def remove_proxy(self, proxy: Proxy):
        self.proxies.remove(proxy)

    async def get_proxy(self):
        async with self.lock:
            while not self.proxies:
                await asyncio.sleep(1)
                logging.debug("No proxy available. waiting...")
            
            return random.choice(tuple(self.proxies))

    async def fail(self, proxy: Proxy):
        async with self.lock:
            if proxy not in self.proxies: return False # Already removed

            await self.remove_proxy(proxy) # remove proxy
            
            if proxy.fails < self.maxfails: # add again if limit not reached
                proxy.fails += 1 # increase proxy fails
                return await self.add_proxy(proxy)

        

class Scraper:
    def __init__(self):
        self.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False, limit=None))

        self.plain_provider = Provider.ProviderPlainText(self.session)
        self.cell_provider = Provider.ProviderTableCell(self.session)

        self.proxies = set()

    async def update_proxies(self):
        proxy_total_list = await self.get_all_proxies()
        for proxy in proxy_total_list:
            if len(proxy.split(":")) == 2:
                proxy = Proxy(*proxy.split(":"))
                if proxy not in self.proxies: self.proxies.add(proxy)

        return self.proxies

    async def get_all_proxies(self):
        proxy_total_list = []

        result = await asyncio.gather(
            *[self.plain_provider.result(url) for url in Providers.PLAIN_PROVIDERS],
            *[self.cell_provider.result(url) for url in Providers.CELL_PROVIDERS]
        )
        
        for proxy_list in result:
            for proxy in proxy_list:
                proxy_total_list.append(proxy)

        return proxy_total_list

    def __del__(self):
        asyncio.create_task(self.session.close())




