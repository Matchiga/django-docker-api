import re
from django.core.exceptions import ValidationError
from django.core.validators import validate_email as django_validate_email


class PasswordValidator:
    
    @staticmethod
    def validate(password):
        errors = []
        
        if len(password) < 8:
            errors.append("A senha deve ter no mínimo 8 caracteres")
        
        if len(password) > 128:
            errors.append("A senha não pode ter mais de 128 caracteres")
        
        if not re.search(r'[A-Z]', password):
            errors.append("A senha deve conter pelo menos uma letra maiúscula")
        
        if not re.search(r'[a-z]', password):
            errors.append("A senha deve conter pelo menos uma letra minúscula")
        
        if not re.search(r'\d', password):
            errors.append("A senha deve conter pelo menos um número")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;/~`]', password):
            errors.append("A senha deve conter pelo menos um caractere especial")
        
        common_passwords = [
            'password', '12345678', 'qwerty', 'abc123', 'password123',
            '123456789', '12345', '1234567', 'password1', '123456'
        ]
        
        if password.lower() in common_passwords:
            errors.append("Senha muito comum, escolha uma senha mais segura")
        
        if re.search(r'(012|123|234|345|456|567|678|789|890)', password):
            errors.append("Evite sequências numéricas óbvias")
        
        if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij)', password.lower()):
            errors.append("Evite sequências alfabéticas óbvias")
        
        if errors:
            raise ValidationError(errors)
        
        return True


class EmailValidator:
    
    @staticmethod
    def validate(email):
        try:
            django_validate_email(email)
        except ValidationError:
            raise ValidationError("Email inválido")
        
        email = email.strip().lower()
        
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError("Formato de email inválido")
        
        if len(email) > 255:
            raise ValidationError("Email muito longo")
        
        disposable_domains = [
            'tempmail.com', '10minutemail.com', 'guerrillamail.com',
            'mailinator.com', 'throwaway.email'
        ]
        
        domain = email.split('@')[1]
        if domain in disposable_domains:
            raise ValidationError("Emails temporários não são permitidos")
        
        return True


class NameValidator:
    
    @staticmethod
    def validate(name):
        if not name or not name.strip():
            raise ValidationError("Nome é obrigatório")
        
        name = name.strip()
        
        if len(name) < 2:
            raise ValidationError("Nome deve ter pelo menos 2 caracteres")
        
        if len(name) > 255:
            raise ValidationError("Nome muito longo")
        
        if ' ' not in name:
            raise ValidationError("Por favor, informe nome e sobrenome")
        
        if not re.match(r'^[a-zA-ZÀ-ÿ\s\'-]+$', name):
            raise ValidationError("Nome contém caracteres inválidos")
        
        if not any(c.isalpha() for c in name):
            raise ValidationError("Nome deve conter letras")
        
        return True


class UsernameValidator:
    
    @staticmethod
    def validate(username):
        if not username or not username.strip():
            raise ValidationError("Username é obrigatório")
        
        username = username.strip().lower()
        
        if len(username) < 3:
            raise ValidationError("Username deve ter pelo menos 3 caracteres")
        
        if len(username) > 30:
            raise ValidationError("Username muito longo")
        
        if not re.match(r'^[a-z0-9_-]+$', username):
            raise ValidationError("Username pode conter apenas letras, números, _ e -")
        
        if username.startswith(('_', '-')) or username.endswith(('_', '-')):
            raise ValidationError("Username não pode começar ou terminar com _ ou -")
        
        reserved = [
            'admin', 'root', 'system', 'administrator', 'api',
            'user', 'users', 'login', 'logout', 'register'
        ]
        
        if username in reserved:
            raise ValidationError("Username não disponível")
        
        return True


class PhoneValidator:
    
    @staticmethod
    def validate(phone):
        if not phone:
            return True  # Opcional

        phone_digits = re.sub(r'\D', '', phone)
        
        if len(phone_digits) < 10:
            raise ValidationError("Telefone muito curto")
        
        if len(phone_digits) > 13: 
            raise ValidationError("Telefone muito longo")
        
        if phone_digits.startswith('55') and len(phone_digits) > 11:
            phone_digits = phone_digits[2:]
        
        ddd = phone_digits[:2]
        if not (10 <= int(ddd) <= 99):
            raise ValidationError("DDD inválido")
        
        if len(phone_digits) == 11 and phone_digits[2] != '9':
            raise ValidationError("Número de celular deve começar com 9")
        
        return True


def validate_user_data(data, is_update=False):
    errors = {}
    
    if 'name' in data or not is_update:
        try:
            NameValidator.validate(data.get('name'))
        except ValidationError as e:
            errors['name'] = e.messages
    
    if 'email' in data or not is_update:
        try:
            EmailValidator.validate(data.get('email'))
        except ValidationError as e:
            errors['email'] = e.messages
    
    if 'password' in data:
        try:
            PasswordValidator.validate(data['password'])
        except ValidationError as e:
            errors['password'] = e.messages
    
    if 'phone' in data:
        try:
            PhoneValidator.validate(data.get('phone'))
        except ValidationError as e:
            errors['phone'] = e.messages
    
    return (len(errors) == 0, errors)


def validate_data(validator_class):
    def decorator(func):
        def wrapper(*args, **kwargs):
            data = args[0] if args else kwargs.get('data')
            
            try:
                validator_class.validate(data)
            except ValidationError as e:
                return {'error': True, 'message': str(e)}
            
            return func(*args, **kwargs)
        return wrapper
    return decorator