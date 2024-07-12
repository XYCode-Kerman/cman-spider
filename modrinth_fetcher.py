import asyncio
import pickle
from typing import List
from config import CMAN_INDEX_PATH, DEBUG
from utils import logger, modrinth_http_session

from models.modrinth import ModrinthProject
from models.cman_index import CMANProject


async def fetch_one_page(page: int) -> List[CMANProject | BaseException]:
    async with modrinth_http_session() as session:
        resp = await session.get(
            f"/v2/search?index=downloads&limit=100&offset={page * 100}"
        )

        if int(resp.headers["X-Ratelimit-Remaining"]) <= 100:
            logger.warning(
                f"达到 Modrinth 限制, 休眠 {int(resp.headers['X-Ratelimit-Reset']) + 1}s"
            )
            await asyncio.sleep(int(resp.headers["X-Ratelimit-Reset"]) + 1)
            return await fetch_one_page(page)

        logger.info(f"Modrinth 的 {page} 页获取完成")

        data = await resp.json()

        projects = [ModrinthProject.model_validate(hit) for hit in data["hits"]]

        tasks = [CMANProject.load_from_modrinth_project(x) for x in projects]
        return await asyncio.gather(*tasks, return_exceptions=True)


async def fetch_batch(total_pages: int, step: int = 1) -> List[CMANProject]:
    results = []
    for page in range(0, total_pages, step):
        tasks = [
            fetch_one_page(page) for page in range(page, min(page + step, total_pages))
        ]

        resp = await asyncio.gather(*tasks, return_exceptions=True)
        for x in resp:
            if isinstance(x, BaseException):
                logger.exception(x)
                continue

            for result in x:
                if isinstance(result, BaseException):
                    logger.exception(result)
                    continue

                CMAN_INDEX_PATH.joinpath(result.id).with_suffix(
                    ".cman.json"
                ).write_text(
                    result.model_dump_json(indent=2),
                    encoding="utf-8",
                )

                CMAN_INDEX_PATH.joinpath(result.id).with_suffix(
                    ".cman.pkl"
                ).write_bytes(pickle.dumps(result, protocol=5))
            results.extend(x)
    return results


async def fetch_all() -> List[CMANProject]:
    async with modrinth_http_session() as session:
        total_hits = (await (await session.get("/v2/search")).json())["total_hits"]

        if DEBUG:
            results = await fetch_batch(5)
        else:
            results = await fetch_batch(total_hits // 100 + 1)

        return results
