"""Parameter validation for components"""

from typing import Dict, Any
from deluxy.models import GearParameters, ShaftParameters, CylinderParameters
from deluxy.utils.errors import ValidationError


class ParameterValidator:
    """Validate component parameters"""
    
    @staticmethod
    def validate_gear(params: Dict[str, Any]) -> GearParameters:
        """Validate and create gear parameters"""
        try:
            gear = GearParameters(
                teeth=int(params.get("teeth", 24)),
                module=float(params.get("module", 2.0)),
                pressure_angle=float(params.get("pressure_angle", 20.0)),
                thickness=float(params.get("thickness", 8.0)),
                bore=float(params.get("bore", 10.0))
            )
            gear.validate()
            return gear
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid gear parameters: {str(e)}")
    
    @staticmethod
    def validate_shaft(params: Dict[str, Any]) -> ShaftParameters:
        """Validate and create shaft parameters"""
        try:
            shaft = ShaftParameters(
                length=float(params.get("length", 120.0)),
                main_diameter=float(params.get("main_diameter", 25.0)),
                left_diameter=float(params.get("left_diameter", 18.0)),
                right_diameter=float(params.get("right_diameter", 20.0))
            )
            shaft.validate()
            return shaft
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid shaft parameters: {str(e)}")
    
    @staticmethod
    def validate_cylinder(params: Dict[str, Any]) -> CylinderParameters:
        """Validate and create cylinder parameters"""
        try:
            cylinder = CylinderParameters(
                diameter=float(params.get("diameter", 30.0)),
                height=float(params.get("height", 50.0))
            )
            cylinder.validate()
            return cylinder
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid cylinder parameters: {str(e)}")
