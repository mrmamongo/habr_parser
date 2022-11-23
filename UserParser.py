import asyncio
import logging
from pathlib import Path

import aiofiles.os
import aiohttp
from aiocsv import AsyncDictReader
from bs4 import BeautifulSoup


class UserParser:
    def __init__(self, filename: str, dirname: str):
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.dirname: str = dirname
        self.filename: str = filename
        self.session: aiohttp.ClientSession | None = None
        self.file: aiofiles.threadpool = None
        self.parsed_urls: tuple[str] = ()

    @staticmethod
    async def __parse_file(filename: Path) -> str:
        with open(filename, "r", encoding='utf-8') as f:
            for line in f:
                return line[:-1]

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        self.file = await aiofiles.open(self.filename, "r", encoding='utf-8')
        if Path(self.dirname).exists():
            self.parsed_urls = tuple(
                await asyncio.gather(*[self.__parse_file(file) for file in Path(self.dirname).glob("*.txt")]))
        else:
            await aiofiles.os.mkdir(self.dirname)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session is not None:
            await self.session.close()
        await self.file.close()

    async def __parse_user(self, url: str) -> None:
        page = await self.session.get(url)
        html_page: str = await page.text()
        name: str = BeautifulSoup(html_page, 'lxml').title.get_text().split(' — ')[0]
        await self.__dump_user(url, name, html_page)

    async def parse_users(self) -> int:
        try:
            tasks = []
            async for row in AsyncDictReader(self.file, fieldnames=['url']):
                if row['url'] != 'url' and row['url'] not in self.parsed_urls and row['url'] not in self.parsed_urls:
                    tasks.append(asyncio.create_task(self.__parse_user(row['url'])))
            if len(tasks) > 0:
                done_tasks, _ = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
                return len(done_tasks)
            return 0
        except Exception as e:
            self.logger.error(e)
            return 0

    async def __dump_user(self, url: str, name: str, html_page: str) -> None:
        async with aiofiles.open(f"{self.dirname}/{name}.txt", "w", encoding='utf-8') as f:
            await f.writelines(map(lambda x: x + '\n', (url, name, html_page)))
