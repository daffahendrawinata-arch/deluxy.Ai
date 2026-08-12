"""Material database for DELUXY.Ai"""

from typing import Dict, Optional
from deluxy.models import Material


class MaterialDatabase:
    """Material property database"""
    
    def __init__(self):
        self.materials = Material.predefined()
    
    def get(self, name: str) -> Optional[Material]:
        """Get material by name"""
        return self.materials.get(name)
    
    def list_names(self) -> list:
        """List all material names"""
        return list(self.materials.keys())
    
    def add_material(self, material: Material) -> None:
        """Add custom material"""
        self.materials[material.name] = material
    
    def get_density(self, name: str) -> float:
        """Get material density in kg/m³"""
        material = self.get(name)
        if material is None:
            raise ValueError(f"Material '{name}' not found")
        return material.density
    
    def get_color(self, name: str) -> str:
        """Get material color hex code"""
        material = self.get(name)
        if material is None:
            raise ValueError(f"Material '{name}' not found")
        return material.color
