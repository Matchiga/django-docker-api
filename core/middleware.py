import time
import logging
import json
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from rest_framework import status

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    
    def process_request(self, request):
        request._start_time = time.time()
        
        logger.info(
            f"Request: {request.method} {request.path}",
            extra={
                'method': request.method,
                'path': request.path,
                'ip': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown')
            }
        )
    
    def process_response(self, request, response):
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            logger.info(
                f"Response: {request.method} {request.path} - {response.status_code} ({duration:.2f}s)",
                extra={
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'duration': duration,
                    'ip': self.get_client_ip(request)
                }
            )
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response


class APIVersionMiddleware(MiddlewareMixin):
    
    def process_request(self, request):
        version = request.META.get('HTTP_X_API_VERSION')
        
        if not version:
            path_parts = request.path.split('/')
            for part in path_parts:
                if part.startswith('v') and part[1:].replace('.', '').isdigit():
                    version = part[1:]
                    break
        
        if not version:
            version = '1.0'
        
        valid_versions = ['1.0', '1.1', '2.0']
        if version not in valid_versions:
            return JsonResponse(
                {
                    'error': f'Versão da API {version} não suportada',
                    'supported_versions': valid_versions
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        request.api_version = version


class JSONRequestMiddleware(MiddlewareMixin):
    
    def process_request(self, request):
        if request.content_type == 'application/json':
            try:
                if request.body:
                    request.json_data = json.loads(request.body.decode('utf-8'))
                else:
                    request.json_data = {}
            except json.JSONDecodeError:
                return JsonResponse(
                    {'error': 'JSON inválido no body da requisição'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            request.json_data = {}


class CORSMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-API-Version'
        response['Access-Control-Max-Age'] = '3600'
        
        return response


class RequestIDMiddleware(MiddlewareMixin):
    def process_request(self, request):
        import uuid
        request.id = str(uuid.uuid4())
        
        logger.info(
            f"Request ID: {request.id}",
            extra={'request_id': request.id}
        )
    
    def process_response(self, request, response):
        if hasattr(request, 'id'):
            response['X-Request-ID'] = request.id
        return response


class MaintenanceModeMiddleware(MiddlewareMixin):    
    def process_request(self, request):
        from django.conf import settings
        
        maintenance_mode = getattr(settings, 'MAINTENANCE_MODE', False)
        
        if maintenance_mode:
            if hasattr(request, 'user') and request.user.is_staff:
                return None
            
            return JsonResponse(
                {
                    'error': 'Sistema em manutenção',
                    'message': 'Voltaremos em breve. Desculpe o inconveniente.',
                    'retry_after': 3600 
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class RateLimitMiddleware(MiddlewareMixin):
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.requests = {} 
    
    def process_request(self, request):
        ip = RequestLoggingMiddleware.get_client_ip(request)
        now = time.time()
        
        if ip in self.requests:
            self.requests[ip] = [
                (ts, count) for ts, count in self.requests[ip]
                if now - ts < 60
            ]
        
        request_count = sum(count for _, count in self.requests.get(ip, []))
        
        if request_count >= 100:
            return JsonResponse(
                {
                    'error': 'Rate limit excedido',
                    'message': 'Muitas requisições. Tente novamente em alguns segundos.',
                    'retry_after': 60
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        if ip not in self.requests:
            self.requests[ip] = []
        self.requests[ip].append((now, 1))


class UserActivityMiddleware(MiddlewareMixin):
    
    def process_request(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            from django.utils import timezone
            from core.database import SessionLocal, UserModel
            
            db = SessionLocal()
            try:
                user = db.query(UserModel).filter(
                    UserModel.id == request.user.id
                ).first()
                
                if user:
                    pass
            finally:
                db.close()
