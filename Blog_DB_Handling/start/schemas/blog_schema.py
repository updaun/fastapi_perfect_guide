from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass
from datetime import datetime
from typing import Optional


class BlogInput(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    author: str = Field(..., max_length=100)
    content: str = Field(..., min_length=2, max_length=4000)
    image_loc: Optional[str] = Field(None, max_length=400)


class Blog(BlogInput):
    id: int
    modified_dt: datetime


@dataclass
class BlogData:
    id: int
    title: str
    author: str
    content: str
    modified_dt: datetime | None = None
    image_loc: str | None = None  # 마지막에 와야함
