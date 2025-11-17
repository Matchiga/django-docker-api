from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.id == request.user.id


class IsOwner(permissions.BasePermission):    
    message = 'Você não tem permissão para acessar este recurso.'
    
    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id


class IsAdminOrOwner(permissions.BasePermission):    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        return obj.id == request.user.id


class IsActiveUser(permissions.BasePermission):    
    message = 'Sua conta está inativa. Entre em contato com o suporte.'
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active


class CanCreateUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        
        return request.user and request.user.is_authenticated


class CanDeleteUser(permissions.BasePermission):
    message = 'Apenas administradores podem deletar usuários.'
    
    def has_permission(self, request, view):
        if request.method == 'DELETE':
            return request.user and request.user.is_staff
        return True
    
    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            if request.user.is_staff:
                return True
            return obj.id == request.user.id
        return True


class IsNotSelf(permissions.BasePermission):
    message = 'Você não pode realizar esta ação em si mesmo.'
    
    def has_object_permission(self, request, view, obj):
        return obj.id != request.user.id


class RateLimitPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return True


class IsSuperUserOrOwner(permissions.BasePermission):    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        return obj.id == request.user.id


def check_user_permission(user, obj, action='view'):
    if not user or not user.is_authenticated:
        return False
    
    if user.is_staff or user.is_superuser:
        return True
    
    if not user.is_active:
        return False
    
    if action == 'view':
        return True  
    
    elif action == 'edit':
        return obj.id == user.id  
    
    elif action == 'delete':
        return obj.id == user.id  
    
    return False