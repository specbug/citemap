import re
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Union


class Arg(BaseModel):
    url: str = Field(
        ...,
        description="URL of the blog",
        regex=r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/"
              r")(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s("
              r")<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    )
    filename: str = Field(..., description="output file name (.html)", example="plot.html", regex=r'\w+\.html')
    height: Optional[Union[int, str]] = '100%'
    width: Optional[Union[int, str]] = '100%'
