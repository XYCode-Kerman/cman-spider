from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class ModrinthVersionHashes(BaseModel):
    sha512: str
    sha1: str


class ModrinthVersionFile(BaseModel):
    hashes: ModrinthVersionHashes
    url: str
    filename: str
    primary: bool
    size: int


class ModrinthVersion(BaseModel):
    id: str
    project_id: str
    name: str
    version_number: str
    game_versions: List[str] = []
    version_type: Literal["release", "beta", "alpha"]
    loaders: List[str] = []
    files: List[ModrinthVersionFile] = []


class ModrinthProject(BaseModel):
    slug: str
    title: str
    description: str
    categories: List[str]
    client_side: Literal["required", "optional", "unsupported", "unknown"]
    server_side: Literal["required", "optional", "unsupported", "unknown"]
    project_type: Literal["mod", "modpack", "resourcepack", "shader"]
    game_versions: List[str] = Field(alias="versions")
