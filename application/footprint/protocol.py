from typing import Protocol
from .types import COORD, POS



class Footprint(Protocol):
    def add_text(self, text: str, at: POS, **kwargs) -> None:
        ...

    def add_line(self, start: COORD, end: COORD, width: float, **kwargs) -> None:
        ...

    def evaluate(self) -> str:
        ...
