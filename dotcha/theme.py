from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple, Union


@dataclass(frozen=True)
class ColorSchema:
    background: Union[str, Tuple[int, int, int]]
    text_colors: List[Union[str, Tuple[int, int, int]]]
    background_colors: List[Union[str, Tuple[int, int, int]]]


class Theme(Enum):
    LIGHT = "light"
    DARK = "dark"
    CUSTOM = "custom"


class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


LIGHT_SCHEMA = ColorSchema(
    background=(255, 255, 255),
    text_colors=[
        (20, 20, 20),     # Dark Gray
        (0, 51, 102),     # Deep Blue
        (102, 0, 0),      # Dark Red
        (0, 102, 51),     # Dark Green
    ],
    background_colors=[
        (240, 240, 240, 60),
        (255, 228, 225, 60),
        (224, 255, 255, 60),
    ]
)

DARK_SCHEMA = ColorSchema(
    background=(10, 10, 10),
    text_colors=[
        (0, 255, 255),    # Cyan
        (255, 0, 255),    # Magenta
        (255, 255, 0),    # Yellow
        (0, 255, 0),      # Neon Green
    ],
    background_colors=[
        (40, 40, 40, 80),
        (60, 60, 60, 80),
        (30, 30, 50, 80),
    ]
)
