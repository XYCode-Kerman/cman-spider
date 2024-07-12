import asyncio
import datetime
import modrinth_fetcher

import git
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import CMAN_INDEX_PATH, CMAN_INDEX_REPO_URL
from utils import logger, console
from rich import print

if not CMAN_INDEX_PATH.exists():
    index_repo = git.Repo.clone_from(
        CMAN_INDEX_REPO_URL, to_path=CMAN_INDEX_PATH, branch="main"
    )
else:
    index_repo = git.Repo(CMAN_INDEX_PATH)

scheduler = AsyncIOScheduler()


async def main():
    logger.info("Starting CMAN spider")

    with console.status("Pulling index"):
        try:
            index_repo.remotes.origin.pull(rebase=True)
        except git.GitCommandError:
            logger.fatal(
                f"拉取远程CMAN-Index仓库时出现错误，请删除 {CMAN_INDEX_PATH.absolute()} 并重新运行，或检查网络环境。"
            )
            exit()

    await modrinth_fetcher.fetch_all()

    index_repo.git.add(update=True)
    index_repo.git.commit(m=f"Update CMAN-Index at {datetime.datetime.now()}")
    index_repo.remotes.origin.push()

    logger.info("CMAN spider finished")


if "__main__" == __name__:
    scheduler.add_job(
        main,
        "interval",
        hours=6,
        start_date=datetime.datetime.now() + datetime.timedelta(seconds=1),
    )
    scheduler.start()
    asyncio.get_event_loop().run_forever()
