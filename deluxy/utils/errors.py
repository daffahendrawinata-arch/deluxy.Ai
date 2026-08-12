"""Error definitions for DELUXY.Ai"""

class DELUXYError(Exception):
    """Base exception for DELUXY.Ai"""
    pass


class CADGenerationError(DELUXYError):
    """Exception during CAD generation"""
    pass


class ValidationError(DELUXYError):
    """Exception during parameter validation"""
    pass


class ExportError(DELUXYError):
    """Exception during file export"""
    pass


class AIParsingError(DELUXYError):
    """Exception during AI parsing"""
    pass
