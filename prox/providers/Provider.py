import aiohttp, asyncio
from bs4 import BeautifulSoup

class ProviderPlainText:
    def __init__(self, session):
        self.session = session

    async def get(self, url):
        res = await self.session.get(url)
        return await res.text()

    async def result(self, url):
        res = await self.get(url)
        proxies = [x.strip() for x in res.split("\n")]
        return proxies

class ProviderTableCell:
    def __init__(self, session):
        self.session = session

    async def get(self, url):
        res = await self.session.get(url)
        return await res.text()

    def proxyscrape(self, table):
        proxies = set()
        for row in table.findAll('tr'):
            count = 0
            proxy = ""
            for cell in row.findAll('td'):
                if count == 1:
                    proxy += ":" + cell.text.replace('&nbsp;', '')
                    proxies.add(proxy)
                    break
                proxy += cell.text.replace('&nbsp;', '')
                count += 1
        return proxies

    async def result(self, url):
        res = await self.get(url)
        soup = BeautifulSoup(res,"html.parser")
        result = self.proxyscrape(soup.find('table', attrs={'id': 'proxylisttable'}))
        return result
