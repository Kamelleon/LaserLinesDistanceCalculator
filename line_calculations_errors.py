class NoCoordinatesFoundError(Exception):
    """Raised when there are no coordinates found"""
    pass

class JumpValueError(Exception):
    """Raised when there is too big jump value"""
    pass

class ReferencedObjectPixelWidthError(Exception):
    """Raised when there is no pixel width assigned"""
    pass

class ReferencedObjectRealWidthError(Exception):
    """Raised when there is no real width assigned"""
    pass

class SourceImageNotFoundError(Exception):
    """Raised when there is no image found"""
    pass