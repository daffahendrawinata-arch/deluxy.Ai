"""Unit conversion utilities"""

from typing import Literal
from enum import Enum


class LengthUnit(Enum):
    """Length units"""
    MM = 1.0
    CM = 10.0
    M = 1000.0
    INCH = 25.4
    FOOT = 304.8
    THOU = 0.0254  # 1/1000 inch


class UnitConverter:
    """Unit conversion utility"""
    
    @staticmethod
    def to_mm(value: float, unit: str) -> float:
        """Convert any length unit to millimeters"""
        unit_upper = unit.upper()
        
        conversions = {
            "MM": 1.0,
            "CM": 10.0,
            "M": 1000.0,
            "INCH": 25.4,
            "IN": 25.4,
            "FOOT": 304.8,
            "FT": 304.8,
            "THOU": 0.0254
        }
        
        if unit_upper not in conversions:
            raise ValueError(f"Unknown unit: {unit}")
        
        return value * conversions[unit_upper]
    
    @staticmethod
    def from_mm(value: float, unit: str) -> float:
        """Convert from millimeters to any length unit"""
        unit_upper = unit.upper()
        
        conversions = {
            "MM": 1.0,
            "CM": 0.1,
            "M": 0.001,
            "INCH": 1.0 / 25.4,
            "IN": 1.0 / 25.4,
            "FOOT": 1.0 / 304.8,
            "FT": 1.0 / 304.8,
            "THOU": 1.0 / 0.0254
        }
        
        if unit_upper not in conversions:
            raise ValueError(f"Unknown unit: {unit}")
        
        return value * conversions[unit_upper]
