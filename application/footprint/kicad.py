from typing import Literal
from dataclasses import dataclass

from sexpdata import dumps, String

from .types import COORD, POS, SIZE


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


    def add_text(self, text: str, at: POS, type: Literal["reference", "value", "user"] = "value", layer: str = "F.SilkS") -> None:
        self.__items.append(["fp_text",
            type, text,
            ["at", *at],
            ["layer", String(layer)],
            ["effects", ["font",
                ["size", 1, 1],
                ["thickness", 0.15],
            ]]
        ])


    def add_line(self, start: COORD, end: COORD, width: float, layer=None, type="default") -> None:
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


    def add_rectangle(self, start: COORD, end: COORD, width: float, layer="F.SilkS", type="default") -> None:
        self.__items.append(["fp_rect",
            ["start", *start],
            ["end", *end],
            ["stroke",
                ["width", width],
                ["type", type],
            ],
            ["layer", layer],
        ])

    def add_smd_pad(self, number: str, ratio:float, position: POS, size: SIZE, layers=["F.Cu", "F.Paste", "F.Mask"]) -> None:
        self.__items.append(["pad",
            String(number), "smd", "roundrect",
            ["at", *position],
            ["size", *size],
            ["layers", *layers],
            ["roundrect_rratio", ratio],
            ["thermal_bridge_angle", 45],
        ])



    def evaluate(self) -> str:
        items = ["footprint", String(self.name),
            ["version", self.version],
            ["generator", self.generator],
            ["layer", String("F.Cu")],
            ["attr", self.type, "exclude_from_pos_files", "exclude_from_bom"],
        ]
        return dumps(items + self.__items, str_as="symbol")
