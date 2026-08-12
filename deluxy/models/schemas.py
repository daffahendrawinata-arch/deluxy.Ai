"""Data schemas for DELUXY.Ai parameters and results"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class GearParameters:
    """Spur gear parameters"""
    teeth: int
    module: float
    pressure_angle: float = 20.0
    thickness: float = 8.0
    bore: float = 10.0
    
    def validate(self) -> None:
        """Validate gear parameters"""
        if self.teeth < 4:
            raise ValueError("Teeth must be at least 4")
        if self.module <= 0:
            raise ValueError("Module must be positive")
        if not (10 <= self.pressure_angle <= 45):
            raise ValueError("Pressure angle must be between 10 and 45 degrees")
        if self.thickness <= 0:
            raise ValueError("Thickness must be positive")
        if self.bore < 0:
            raise ValueError("Bore cannot be negative")


@dataclass
class ShaftParameters:
    """Stepped shaft parameters"""
    length: float
    main_diameter: float
    left_diameter: float
    right_diameter: float
    
    def validate(self) -> None:
        """Validate shaft parameters"""
        if self.length <= 0:
            raise ValueError("Length must be positive")
        if self.main_diameter <= 0:
            raise ValueError("Main diameter must be positive")
        if self.left_diameter <= 0:
            raise ValueError("Left diameter must be positive")
        if self.right_diameter <= 0:
            raise ValueError("Right diameter must be positive")


@dataclass
class CylinderParameters:
    """Cylinder parameters"""
    diameter: float
    height: float
    
    def validate(self) -> None:
        """Validate cylinder parameters"""
        if self.diameter <= 0:
            raise ValueError("Diameter must be positive")
        if self.height <= 0:
            raise ValueError("Height must be positive")


@dataclass
class Material:
    """Material definition"""
    name: str
    density: float  # kg/m³
    color: str  # hex color
    
    @classmethod
    def predefined(cls) -> Dict[str, 'Material']:
        """Get predefined materials"""
        return {
            "Steel": cls("Steel", 7.85, "#64748b"),
            "Stainless Steel": cls("Stainless Steel", 8.00, "#cbd5e1"),
            "Aluminium": cls("Aluminium", 2.70, "#d1d5db"),
            "Brass": cls("Brass", 8.40, "#eab308"),
            "Copper": cls("Copper", 8.96, "#b45309"),
            "Titanium": cls("Titanium", 4.50, "#94a3b8"),
            "Plastic": cls("Plastic", 1.05, "#38bdf8"),
        }


@dataclass
class EngineringData:
    """Engineering calculation results"""
    component_type: str
    material: str
    volume_mm3: float
    mass_kg: float
    parameters: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "component_type": self.component_type,
            "material": self.material,
            "volume_mm3": self.volume_mm3,
            "mass_kg": self.mass_kg,
            "parameters": self.parameters
        }
