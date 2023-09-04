from dataclasses import dataclass
from functools import cached_property

from application.materials import Material
from application.constants import MILS_TO_MM, MM_TO_MILS



@dataclass(frozen=True)
class TraceCalculator():
    material: Material
    temperature_rise: float
    thickness: float
    current: float


    @cached_property
    def width(self) -> float:
        """
        These calculations are based on IPC 2221 (for external layers)
        Reference: See KiCAD Calculator Tools or
        https://circuitcalculator.com/wordpress/2006/01/31/pcb-trace-width-calculator/
        """
        # IPC 2221 works in mils, so for the sake of simplicity we convert everthing
        # from mm to mils and back
        a, b, c = 0.048, 0.44, 0.735
        w = (self.current/(a * self.temperature_rise**b))**(1/c) / (self.thickness*MM_TO_MILS) # in mils
        return w*MILS_TO_MM # in mm


    def resistance_from_length(self, length: float) -> float:
        area = self.thickness*self.width*1e-6
        return self.material.resistivity*length / area * 1e-3


    def length_from_resistance(self, resistance: float) -> float:
        area = self.thickness*self.width*1e-6
        return resistance*area / self.material.resistivity * 1e3
