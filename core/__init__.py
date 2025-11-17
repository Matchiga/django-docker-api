__version__ = '1.0.0'
__author__ = 'Matchiga'

from .exceptions import (
    APIException,
    ValidationException,
    AuthenticationException,
    PermissionDeniedException,
    ResourceNotFoundException
)

__all__ = [
    'APIException',
    'ValidationException',
    'AuthenticationException',
    'PermissionDeniedException',
    'ResourceNotFoundException',
]