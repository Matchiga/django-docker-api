import bcrypt
import re
from typing import Tuple


class PasswordSecurity:
    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, list]:
        errors = []

        if len(password) < 8:
            errors.append("A senha deve ter no mínimo 8 caracteres")

        if not re.search(r"[A-Z]", password):
            errors.append("A senha deve conter pelo menos uma letra maiúscula")

        if not re.search(r"[a-z]", password):
            errors.append("A senha deve conter pelo menos uma letra minúscula")

        if not re.search(r"\d", password):
            errors.append("A senha deve conter pelo menos um número")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("A senha deve conter pelo menos um caractere especial")

        return (len(errors) == 0, errors)


class EmailSecurity:
    @staticmethod
    def is_valid_email(email: str) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def normalize_email(email: str) -> str:
        return email.lower().strip()


def hash_password(password: str) -> str:
    return PasswordSecurity.hash_password(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return PasswordSecurity.verify_password(password, hashed_password)


def validate_password(password: str) -> Tuple[bool, list]:
    return PasswordSecurity.validate_password_strength(password)
