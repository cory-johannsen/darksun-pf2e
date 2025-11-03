"""Shared data models used by the PDF parsing pipeline."""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


def slugify(title: str) -> str:
    """Generate a filesystem-safe slug from a heading title."""

    keep = []
    for ch in title.lower():
        if ch.isalnum():
            keep.append(ch)
        elif ch in {" ", ":", "-", "_"}:
            keep.append("-")
    slug = "".join(keep).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "section"


class TocEntry(BaseModel):
    level: int
    title: str
    page: int = Field(..., ge=1)

    model_config = ConfigDict(extra="forbid")


class Section(BaseModel):
    title: str
    level: int
    start_page: int = Field(..., ge=1)
    end_page: int = Field(..., ge=1)
    slug: str
    children: List["Section"] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")

    @property
    def page_span(self) -> range:
        return range(self.start_page, self.end_page + 1)

    def find_child(self, title: str) -> Optional["Section"]:
        for child in self.children:
            if child.title == title:
                return child
        return None


class Manifest(BaseModel):
    pdf_path: str
    page_count: int
    sections: List[Section]

    model_config = ConfigDict(extra="forbid")


class Span(BaseModel):
    text: str
    font: Optional[str] = None
    size: Optional[float] = None
    flags: Optional[int] = None
    color: Optional[str] = None
    ascender: Optional[float] = None
    descender: Optional[float] = None

    model_config = ConfigDict(extra="forbid")


class Line(BaseModel):
    bbox: List[float]
    spans: List[Span]

    model_config = ConfigDict(extra="forbid")


class ImageData(BaseModel):
    xref: Optional[int] = None
    name: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    colorspace: Optional[str] = None
    ext: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


class Block(BaseModel):
    bbox: List[float]
    type: Literal["text", "image", "vector"]
    lines: List[Line] = Field(default_factory=list)
    image: Optional[ImageData] = None

    model_config = ConfigDict(extra="forbid")


class TableCell(BaseModel):
    text: Optional[str] = None
    bbox: List[float]
    rowspan: int = Field(default=1, ge=1)
    colspan: int = Field(default=1, ge=1)

    model_config = ConfigDict(extra="forbid")


class TableRow(BaseModel):
    cells: List[TableCell]

    model_config = ConfigDict(extra="forbid")


class Table(BaseModel):
    bbox: List[float]
    rows: List[TableRow]

    model_config = ConfigDict(extra="forbid")


class Page(BaseModel):
    page_number: int = Field(..., ge=1)
    width: float
    height: float
    rotation: int
    blocks: List[Block]
    tables: List[Table] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


class StructuredSection(BaseModel):
    title: str
    slug: str
    level: int
    start_page: int = Field(..., ge=1)
    end_page: int = Field(..., ge=1)
    parent_slugs: List[str] = Field(default_factory=list)
    pages: List[Page]

    model_config = ConfigDict(extra="forbid")

