from prox.providers import Provider, Providers
import aiohttp, asyncio

class Proxy:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.fails = 0

    def __eq__(self, other):
        return self.ip == other.ip and self.port == self.port

    def __hash__(self):
        return hash(self.ip + self.port)

class Scraper:
    def __init__(self, timeout):
        self.timeout = timeout
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
        print(len(self.proxies))
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




loop = asyncio.get_event_loop()

loop.run_until_complete(Scraper(10).update_proxies())