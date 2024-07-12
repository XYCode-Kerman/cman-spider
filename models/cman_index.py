from pydantic import BaseModel
from .modrinth import ModrinthProject, ModrinthVersion, ModrinthVersionFile
from typing import List
from utils import modrinth_http_session, logger


class CMANFile(BaseModel):
    sha512: str
    url: str
    filename: str
    primary: bool
    size: int

    @staticmethod
    def load_from_modrinth_file(modrinth_file: ModrinthVersionFile) -> "CMANFile":
        return CMANFile(
            sha512=modrinth_file.hashes.sha512,
            url=modrinth_file.url,
            filename=modrinth_file.filename,
            primary=modrinth_file.primary,
            size=modrinth_file.size,
        )


class CMANVersion(BaseModel):
    id: str
    name: str
    version_number: str
    game_versions: List[str] = []
    loaders: List[str] = []
    files: List[CMANFile] = []

    @staticmethod
    def load_from_modrinth_version(modrinth_version: ModrinthVersion) -> "CMANVersion":
        return CMANVersion(
            id=modrinth_version.id,
            name=modrinth_version.name,
            version_number=modrinth_version.version_number,
            game_versions=modrinth_version.game_versions,
            loaders=modrinth_version.loaders,
            files=[CMANFile.load_from_modrinth_file(x) for x in modrinth_version.files],
        )


class CMANProject(BaseModel):
    id: str
    slug: str
    name: str
    description: str
    versions: List[CMANVersion]

    @staticmethod
    async def load_from_modrinth_project(
        modrinth_project: ModrinthProject,
    ) -> "CMANProject":
        logger.info(f"正在获取 {modrinth_project.slug} 的详细信息")

        async with modrinth_http_session() as session:
            return CMANProject(
                id=modrinth_project.slug.replace('"', ""),
                slug=modrinth_project.slug.replace(
                    '"', ""
                ),  # fresh-animations 导致的问题
                name=modrinth_project.title,
                description=modrinth_project.description,
                versions=[
                    CMANVersion.load_from_modrinth_version(
                        ModrinthVersion.model_validate(x)
                    )
                    for x in await (
                        await session.get(
                            f"/v2/project/{modrinth_project.slug}/version"
                        )
                    ).json()
                ],
            )
