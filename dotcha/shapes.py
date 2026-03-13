import random
from abc import ABC, abstractmethod
from typing import Tuple, Union
from PIL import ImageDraw


class Shape(ABC):
    """Base class for all geometric shapes used in the captcha."""

    def __init__(self, x: int, y: int, size: int):
        self.x = x
        self.y = y
        self.size = size

    @property
    def center(self) -> Tuple[int, int]:
        return (self.x, self.y)

    @abstractmethod
    def draw(self, draw: ImageDraw.ImageDraw, color: Union[str, Tuple[int, ...]]) -> None:
        """Draw the shape on the given PIL ImageDraw object."""
        pass


class Circle(Shape):
    def draw(self, draw: ImageDraw.ImageDraw, color: Union[str, Tuple[int, ...]]) -> None:
        left_up = (self.x - self.size, self.y - self.size)
        right_down = (self.x + self.size, self.y + self.size)
        draw.ellipse([left_up, right_down], fill=color)


class Triangle(Shape):
    def draw(self, draw: ImageDraw.ImageDraw, color: Union[str, Tuple[int, ...]]) -> None:
        points = [
            (self.x, self.y - self.size),
            (self.x - self.size, self.y + self.size),
            (self.x + self.size, self.y + self.size),
        ]
        draw.polygon(points, fill=color)


class Line(Shape):
    def draw(self, draw: ImageDraw.ImageDraw, color: Union[str, Tuple[int, ...]]) -> None:
        angle = random.uniform(0, 3.14159)
        dx = int(self.size * 1.5 * (1 if random.random() > 0.5 else -1))
        dy = int(self.size * 1.5 * (1 if random.random() > 0.5 else -1))
        
        start = (self.x - dx, self.y - dy)
        end = (self.x + dx, self.y + dy)
        draw.line([start, end], fill=color, width=max(1, self.size // 3))


class Square(Shape):
    def draw(self, draw: ImageDraw.ImageDraw, color: Union[str, Tuple[int, ...]]) -> None:
        left_up = (self.x - self.size, self.y - self.size)
        right_down = (self.x + self.size, self.y + self.size)
        draw.rectangle([left_up, right_down], fill=color)


class Star(Shape):
    def draw(self, draw: ImageDraw.ImageDraw, color: Union[str, Tuple[int, ...]]) -> None:
        # Simple 5-point star
        points = []
        for i in range(10):
            r = self.size if i % 2 == 0 else self.size // 2
            angle = i * 36 * 0.0174533  # degrees to radians
            px = self.x + int(r * random.random() * 0.5 + r * 0.5) # some jitter
            px = self.x + int(r * 0.8 * (1 if i%2==0 else 0.5) * (random.uniform(0.8, 1.2))) # jitter
            # Let's do a simpler star
            pass
        
        # Better simple 4-point star (cross-like)
        points = [
            (self.x, self.y - self.size * 1.5),
            (self.x + self.size * 0.5, self.y - self.size * 0.5),
            (self.x + self.size * 1.5, self.y),
            (self.x + self.size * 0.5, self.y + self.size * 0.5),
            (self.x, self.y + self.size * 1.5),
            (self.x - self.size * 0.5, self.y + self.size * 0.5),
            (self.x - self.size * 1.5, self.y),
            (self.x - self.size * 0.5, self.y - self.size * 0.5),
        ]
        draw.polygon(points, fill=color)
