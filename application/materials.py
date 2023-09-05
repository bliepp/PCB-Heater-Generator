from dataclasses import dataclass



@dataclass(frozen=True)
class Material():
    name: str
    symbol: str
    resistivity: float # m*Ohm



COPPER = Material("Copper", "Cu", resistivity=1.72e-8)

ALL_MATERIALS = [COPPER]
