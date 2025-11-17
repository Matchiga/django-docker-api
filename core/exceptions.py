from rest_framework.exceptions import APIException as DRFAPIException
from rest_framework import status


class APIException(DRFAPIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Ocorreu um erro no servidor.'
    default_code = 'error'


class ValidationException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Dados inválidos.'
    default_code = 'validation_error'
    
    def __init__(self, detail=None, field=None):
        if field:
            detail = {field: detail} if detail else {field: self.default_detail}
        super().__init__(detail)


class AuthenticationException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Credenciais inválidas.'
    default_code = 'authentication_failed'


class PermissionDeniedException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Você não tem permissão para realizar esta ação.'
    default_code = 'permission_denied'


class ResourceNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Recurso não encontrado.'
    default_code = 'not_found'
    
    def __init__(self, resource_name=None, resource_id=None):
        if resource_name and resource_id:
            detail = f'{resource_name} com ID {resource_id} não encontrado.'
        elif resource_name:
            detail = f'{resource_name} não encontrado.'
        else:
            detail = self.default_detail
        super().__init__(detail)


class DuplicateResourceException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Recurso já existe.'
    default_code = 'duplicate_resource'
    
    def __init__(self, field=None, value=None):
        if field and value:
            detail = f'{field} "{value}" já está em uso.'
        elif field:
            detail = f'{field} já está em uso.'
        else:
            detail = self.default_detail
        super().__init__(detail)


class RateLimitExceededException(APIException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Muitas requisições. Tente novamente mais tarde.'
    default_code = 'rate_limit_exceeded'
    
    def __init__(self, retry_after=None):
        detail = self.default_detail
        if retry_after:
            detail = f'{detail} Tente novamente em {retry_after} segundos.'
        super().__init__(detail)


class InvalidTokenException(AuthenticationException):
    default_detail = 'Token inválido ou expirado.'
    default_code = 'invalid_token'


class ExpiredTokenException(AuthenticationException):
    default_detail = 'Token expirado. Faça login novamente.'
    default_code = 'expired_token'


class InactiveUserException(AuthenticationException):
    default_detail = 'Sua conta está inativa. Entre em contato com o suporte.'
    default_code = 'inactive_user'


class WeakPasswordException(ValidationException):
    default_detail = 'Senha não atende aos requisitos mínimos de segurança.'
    default_code = 'weak_password'


class EmailAlreadyExistsException(DuplicateResourceException):
    default_detail = 'Este email já está cadastrado.'
    default_code = 'email_exists'


class DatabaseException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Erro ao acessar banco de dados.'
    default_code = 'database_error'


class ExternalServiceException(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Serviço externo indisponível.'
    default_code = 'external_service_error'


def custom_exception_handler(exc, context):
    from rest_framework.views import exception_handler
    import logging
    
    logger = logging.getLogger(__name__)
    
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'success': False,
            'error': {
                'code': getattr(exc, 'default_code', 'error'),
                'message': str(exc),
                'details': response.data if isinstance(response.data, dict) else {'detail': response.data}
            }
        }
        
        response.data = custom_response_data
        
        logger.error(
            f"API Error: {exc.__class__.__name__} - {str(exc)}",
            extra={
                'status_code': response.status_code,
                'path': context['request'].path,
                'method': context['request'].method
            }
        )
    
    else:
        logger.exception(
            f"Unhandled Exception: {exc.__class__.__name__}",
            extra={
                'path': context['request'].path,
                'method': context['request'].method
            }
        )
    
    return response


def handle_exceptions(func):

    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationException as e:
            return {'error': True, 'message': str(e), 'status': 400}
        except AuthenticationException as e:
            return {'error': True, 'message': str(e), 'status': 401}
        except PermissionDeniedException as e:
            return {'error': True, 'message': str(e), 'status': 403}
        except ResourceNotFoundException as e:
            return {'error': True, 'message': str(e), 'status': 404}
        except Exception as e:
            return {'error': True, 'message': 'Erro interno do servidor', 'status': 500}
    
    return wrapper