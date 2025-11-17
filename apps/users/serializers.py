from rest_framework import serializers
from core.security import validate_password, EmailSecurity


class UserCreateSerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=255,
        min_length=2,
        required=True,
        error_messages={
            'required': 'O campo nome é obrigatório',
            'min_length': 'O nome deve ter pelo menos 2 caracteres',
            'max_length': 'O nome não pode ter mais de 255 caracteres'
        }
    )
    
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': 'O campo email é obrigatório',
            'invalid': 'Email inválido'
        }
    )
    
    password = serializers.CharField(
        write_only=True, 
        required=True,
        style={'input_type': 'password'},
        error_messages={
            'required': 'O campo senha é obrigatório'
        }
    )
    
    def validate_email(self, value):
        if not EmailSecurity.is_valid_email(value):
            raise serializers.ValidationError("Formato de email inválido")
        return EmailSecurity.normalize_email(value)
    
    def validate_password(self, value):
        is_valid, errors = validate_password(value)
        if not is_valid:
            raise serializers.ValidationError(errors)
        return value
    
    def validate_name(self, value):
        name = ' '.join(value.split())
        
        if ' ' not in name:
            raise serializers.ValidationError("Por favor, informe nome e sobrenome")
        
        return name


class UserUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=255,
        min_length=2,
        required=False
    )
    
    email = serializers.EmailField(required=False)
    
    password = serializers.CharField(
        write_only=True,
        required=False,
        style={'input_type': 'password'}
    )
    
    is_active = serializers.BooleanField(required=False)
    
    def validate_email(self, value):
        if not EmailSecurity.is_valid_email(value):
            raise serializers.ValidationError("Formato de email inválido")
        return EmailSecurity.normalize_email(value)
    
    def validate_password(self, value):
        is_valid, errors = validate_password(value)
        if not is_valid:
            raise serializers.ValidationError(errors)
        return value
    
    def validate_name(self, value):
        name = ' '.join(value.split())
        if ' ' not in name:
            raise serializers.ValidationError("Por favor, informe nome e sobrenome")
        return name


class UserResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate_new_password(self, value):
        is_valid, errors = validate_password(value)
        if not is_valid:
            raise serializers.ValidationError(errors)
        return value
    
    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'As senhas não coincidem'
            })
        return data