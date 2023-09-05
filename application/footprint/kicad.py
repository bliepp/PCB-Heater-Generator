from typing import Literal
from dataclasses import dataclass

from sexpdata import dumps, String



__COORD = tuple[float|int, float|int]
__POS = tuple[float|int, float|int] | tuple[float|int, float|int, float|int]



@dataclass
class KiCADFootprint():
    """
    KiCAD stores its Footprints in the form of S-expressions. Although most  S-expressions allow
    strings to be with or without quotes, KiCAD requires quotes for actuall strings and no quotes
    for keywords. This class takes care of that.
    """
    name: str
    version: int
    type: Literal["smd", "through_hole"] = "smd"
    layer: str = "F.Cu"
    generator: str = "custom"


    def __post_init__(self) -> None:
        self.__items = []


    def add_text(self, text: str, at: "__POS", type: Literal["reference", "value", "user"] = "value", layer: str = "F.SilkS") -> None:
        self.__items.append(["fp_text",
            type, text,
            ["at", *at],
            ["layer", String(layer)],
            ["effects", ["font",
                ["size", 1, 1],
                ["thickness", 0.15],
            ]]
        ])


    def add_line(self, start: "__COORD", end: "__COORD", width: float, layer=None, type="default") -> None:
        layer = layer or self.layer

        self.__items.append(["fp_line",
            ["start", *start],
            ["end", *end],
            ["stroke",
                ["width", width],
                ["type", type],
            ],
            ["layer", String(layer)]
        ])


    def evaluate(self) -> str:
        items = ["footprint", String(self.name),
            ["version", self.version],
            ["generator", self.generator],
            ["layer", String("F.Cu")],
            ["attr", self.type, "exclude_from_pos_files", "exclude_from_bom"],
        ]
        return dumps(items + self.__items, str_as="symbol")
