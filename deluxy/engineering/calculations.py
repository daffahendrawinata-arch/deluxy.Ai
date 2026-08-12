"""Engineering calculations for components"""

import math
from typing import Dict, Any, Optional


class GearCalculations:
    """Spur gear engineering calculations"""
    
    @staticmethod
    def pitch_diameter(teeth: int, module: float) -> float:
        """Calculate pitch diameter: D = m × Z"""
        return module * teeth
    
    @staticmethod
    def base_diameter(teeth: int, module: float, pressure_angle: float) -> float:
        """Calculate base diameter: Db = D × cos(α)"""
        pitch_diameter = module * teeth
        alpha_rad = math.radians(pressure_angle)
        return pitch_diameter * math.cos(alpha_rad)
    
    @staticmethod
    def outside_diameter(teeth: int, module: float) -> float:
        """Calculate outside diameter: Da = m × (Z + 2)"""
        return module * (teeth + 2)
    
    @staticmethod
    def root_diameter(teeth: int, module: float) -> float:
        """Calculate root diameter: Df = m × (Z - 2.5)"""
        return module * (teeth - 2.5)
    
    @staticmethod
    def addendum(module: float) -> float:
        """Calculate addendum: a = m"""
        return module
    
    @staticmethod
    def dedendum(module: float) -> float:
        """Calculate dedendum: b = 1.25 × m"""
        return 1.25 * module
    
    @staticmethod
    def circular_pitch(module: float) -> float:
        """Calculate circular pitch: p = π × m"""
        return math.pi * module
    
    @staticmethod
    def tooth_thickness(module: float) -> float:
        """Calculate tooth thickness at pitch circle"""
        return module * math.pi / 2.0
    
    @staticmethod
    def angular_tooth_spacing(teeth: int) -> float:
        """Calculate angular spacing between teeth in degrees"""
        return 360.0 / teeth
    
    @classmethod
    def calculate_all(cls, teeth: int, module: float, 
                     pressure_angle: float) -> Dict[str, float]:
        """Calculate all gear parameters"""
        return {
            "pitch_diameter_mm": cls.pitch_diameter(teeth, module),
            "base_diameter_mm": cls.base_diameter(teeth, module, pressure_angle),
            "outside_diameter_mm": cls.outside_diameter(teeth, module),
            "root_diameter_mm": cls.root_diameter(teeth, module),
            "addendum_mm": cls.addendum(module),
            "dedendum_mm": cls.dedendum(module),
            "circular_pitch_mm": cls.circular_pitch(module),
            "tooth_thickness_mm": cls.tooth_thickness(module),
            "angular_tooth_spacing_deg": cls.angular_tooth_spacing(teeth),
        }


class ShaftCalculations:
    """Stepped shaft engineering calculations"""
    
    @staticmethod
    def volume(length: float, main_diameter: float, 
               left_diameter: float, right_diameter: float) -> float:
        """Calculate approximate shaft volume"""
        left_length = length * 0.25
        main_length = length * 0.50
        right_length = length * 0.25
        
        left_radius = left_diameter / 2.0
        main_radius = main_diameter / 2.0
        right_radius = right_diameter / 2.0
        
        left_vol = math.pi * (left_radius ** 2) * left_length
        main_vol = math.pi * (main_radius ** 2) * main_length
        right_vol = math.pi * (right_radius ** 2) * right_length
        
        return left_vol + main_vol + right_vol
    
    @classmethod
    def calculate_all(cls, length: float, main_diameter: float,
                     left_diameter: float, right_diameter: float) -> Dict[str, float]:
        """Calculate all shaft parameters"""
        return {
            "length_mm": length,
            "main_diameter_mm": main_diameter,
            "left_diameter_mm": left_diameter,
            "right_diameter_mm": right_diameter,
            "volume_mm3": cls.volume(length, main_diameter, left_diameter, right_diameter),
        }


class CylinderCalculations:
    """Cylinder engineering calculations"""
    
    @staticmethod
    def volume(diameter: float, height: float) -> float:
        """Calculate cylinder volume: V = π × r² × h"""
        radius = diameter / 2.0
        return math.pi * (radius ** 2) * height
    
    @staticmethod
    def surface_area(diameter: float, height: float) -> float:
        """Calculate cylinder surface area"""
        radius = diameter / 2.0
        lateral = 2 * math.pi * radius * height
        top_bottom = 2 * math.pi * (radius ** 2)
        return lateral + top_bottom
    
    @classmethod
    def calculate_all(cls, diameter: float, height: float) -> Dict[str, float]:
        """Calculate all cylinder parameters"""
        return {
            "diameter_mm": diameter,
            "height_mm": height,
            "volume_mm3": cls.volume(diameter, height),
            "surface_area_mm2": cls.surface_area(diameter, height),
        }
