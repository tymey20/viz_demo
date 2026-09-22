"""Exhibit registry. Each exhibit type knows how to render itself to PowerPoint and HTML,
and how to reconcile its rendered numbers back to source. Adding a type = one module here
plus a line in AnyExhibit."""
from __future__ import annotations

from typing import Annotated, Union

from pydantic import Field

from .base import Ctx, Exhibit
from .bar import Bar, Column
from .commentary import CommentarySlide
from .line import Line
from .table import Table

AnyExhibit = Annotated[Union[Table, Bar, Column, Line, CommentarySlide], Field(discriminator="type")]
__all__ = ["AnyExhibit", "Ctx", "Exhibit"]
