import logging
import aiohttp
import contextlib

from rich.logging import RichHandler
from rich.console import Console

logging.basicConfig(level=logging.DEBUG, handlers=[RichHandler()])

logger = logging.getLogger("cman-spider")
console = Console()


@contextlib.asynccontextmanager
async def modrinth_http_session():
    async with aiohttp.ClientSession(
        base_url="https://api.modrinth.com/",
        timeout=aiohttp.ClientTimeout(120),
        headers={"User-Agent": "XYCode-Kerman/CMAN-spider/0.0.1"},
    ) as session:
        yield session
