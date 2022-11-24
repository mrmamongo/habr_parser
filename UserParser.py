import asyncio
import logging
from pathlib import Path

import aiofiles.os
import aiohttp
import tqdm as tqdm
from aiocsv import AsyncDictReader
from aiohttp_socks import ProxyConnector
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class UserParser:
    def __init__(self, filename: str, dirname: str, proxy: str, verbose: bool = False):
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.verbose: bool = verbose
        self.dirname: str = dirname
        self.filename: str = filename
        self.session: aiohttp.ClientSession | None = None
        self.file: aiofiles.threadpool = None
        self.parsed_urls: tuple[str] = ()
        self.user_agent: str = UserAgent().random
        self.connector = ProxyConnector().from_url(proxy)

    @staticmethod
    async def __parse_file(filename: Path) -> str:
        with open(filename, "r", encoding='utf-8') as f:
            for line in f:
                return line[:-1]

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(connector=self.connector)
        self.file = await aiofiles.open(self.filename, "r", encoding='utf-8')
        if Path(self.dirname).exists():
            self.parsed_urls = tuple(
                await asyncio.gather(*[self.__parse_file(file) for file in Path(self.dirname).glob("*.txt")]))
        else:
            await aiofiles.os.mkdir(self.dirname)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.connector.close()
        if self.session is not None:
            await self.session.close()
        await self.file.close()

    async def __parse_user(self, url: str) -> bool:
        try:
            page = await self.session.get(url, headers={"user-agent": self.user_agent})
            html_page: str = await page.text()
            name: str = BeautifulSoup(html_page, 'lxml').title.get_text().split(' — ')[0]
            await self.__dump_user(url, name, html_page)
            return True
        except Exception as e:
            self.logger.error(e)
            return False

    async def parse_users(self) -> int:
        try:
            tasks = [asyncio.create_task(self.__parse_user(row['url'])) async for row in
                     AsyncDictReader(self.file, fieldnames=['url'])
                     if row['url'] != 'url' and row['url'] not in self.parsed_urls]
            if self.verbose:
                responses = [await f
                             for f in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks))]
            else:
                responses = await asyncio.gather(*tasks)

            return len(list(filter(bool, responses)))
        except Exception as e:
            self.logger.error(e)
            return 0

    async def __dump_user(self, url: str, name: str, html_page: str) -> None:
        async with aiofiles.open(f"{self.dirname}/{name}.txt", "w", encoding='utf-8') as f:
            await f.writelines(map(lambda x: x + '\n', (url, name, html_page)))
