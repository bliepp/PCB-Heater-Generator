from typing import Protocol
from .types import COORD, POS, SIZE



class Footprint(Protocol):
    def add_text(self, text: str, at: POS, **kwargs) -> None:
        ...

    def add_line(self, start: COORD, end: COORD, width: float, **kwargs) -> None:
        ...

    def add_rectangle(self, start: COORD, end: COORD, width: float, **kwargs) -> None:
        ...

    def add_smd_pad(self, number: str, ratio: float, position: POS, size: SIZE, **kwargs) -> None:
        ...

    def evaluate(self) -> str:
        ...
