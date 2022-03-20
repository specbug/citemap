import re
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Union


class Plot(BaseModel):
    filename: str = Field(..., description="output file name (.html)", example="plot.html", regex=r'\.html$')
    height: Optional[Union[int, str]] = 1200
    width: Optional[Union[int, str]] = '70%'
