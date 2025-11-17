from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Group,
    Permission, 
)
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class UserManager(BaseUserManager):

    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("O email é obrigatório")

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser deve ter is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser deve ter is_superuser=True")

        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name="Email",
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Email único do usuário",
    )

    name = models.CharField(
        verbose_name="Nome", max_length=255, help_text="Nome completo do usuário"
    )

    is_active = models.BooleanField(
        verbose_name="Ativo",
        default=True,
        help_text="Indica se o usuário está ativo no sistema",
    )

    is_staff = models.BooleanField(
        verbose_name="Staff",
        default=False,
        help_text="Indica se o usuário pode acessar o admin",
    )

    created_at = models.DateTimeField(
        verbose_name="Criado em",
        default=timezone.now,
        help_text="Data e hora de criação do usuário",
    )

    updated_at = models.DateTimeField(
        verbose_name="Atualizado em",
        auto_now=True,
        help_text="Data e hora da última atualização",
    )
    
    groups = models.ManyToManyField(
        Group,
        verbose_name="grupos",
        blank=True,
        help_text="Os grupos aos quais este usuário pertence.",
        related_name="custom_user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name="permissões do usuário",
        blank=True,
        help_text="Permissões específicas para este usuário.",
        related_name="custom_user_permissions_set",
        related_query_name="user",
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ["-created_at"]
        db_table = "users"

    def __str__(self):
        return f"{self.name} ({self.email})"

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name.split()[0] if self.name else ""


@receiver(post_save, sender=User)
def sync_user_with_sqlalchemy(sender, instance, created, **kwargs):
    pass
