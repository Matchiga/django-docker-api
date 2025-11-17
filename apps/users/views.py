from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.db import IntegrityError

from .models import User
from .serializers import (
    UserCreateSerializer,
    UserUpdateSerializer,
    UserResponseSerializer,
    UserLoginSerializer,
    ChangePasswordSerializer,
)
from drf_yasg.utils import swagger_auto_schema

import logging

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class UserListCreateView(APIView):
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        return [IsAuthenticated()]

    @swagger_auto_schema(responses={200: UserResponseSerializer(many=True)})
    @method_decorator(ratelimit(key="ip", rate="100/h", method="GET"))
    def get(self, request):
        try:
            users = User.objects.filter(is_active=True)
            paginator = StandardResultsSetPagination()
            page = paginator.paginate_queryset(users, request)

            if page is not None:
                serializer = UserResponseSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = UserResponseSerializer(users, many=True)
            return Response(
                {"count": users.count(), "results": serializer.data},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Erro ao listar usuários: {e}")
            return Response(
                {"error": "Erro ao buscar usuários"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(request_body=UserCreateSerializer)
    @method_decorator(ratelimit(key="ip", rate="10/h", method="POST"))
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        validated_data = serializer.validated_data

        try:
            new_user = User.objects.create_user(
                name=validated_data["name"],
                email=validated_data["email"],
                password=validated_data["password"],
                is_active=True,
            )

            response_serializer = UserResponseSerializer(new_user)
            logger.info(f"Usuário criado: {new_user.email}")
            return Response(
                {
                    "message": "Usuário criado com sucesso",
                    "user": response_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        except IntegrityError:
            return Response(
                {"error": "Email já cadastrado"}, status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            logger.error(f"Erro ao criar usuário: {e}")
            return Response(
                {"error": "Erro ao criar usuário"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, user_id, request_user):
        try:
            if request_user.is_staff:
                return User.objects.get(id=user_id)

            return User.objects.get(id=user_id, is_active=True)

        except User.DoesNotExist:
            return None

    @swagger_auto_schema(responses={200: UserResponseSerializer})
    def get(self, request, user_id):
        user = self.get_object(user_id, request.user)

        if not user:
            return Response(
                {"error": "Usuário não encontrado"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserResponseSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=UserUpdateSerializer)
    def put(self, request, user_id):
        if not request.user.is_staff and request.user.id != user_id:
            return Response(
                {"error": "Você não tem permissão para editar este usuário."},
                status=status.HTTP_403_FORBIDDEN,
            )
        user = self.get_object(user_id, request.user)
        if not user:
            return Response(
                {"error": "Usuário não encontrado"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        validated_data = serializer.validated_data
        try:
            user.name = validated_data.get("name", user.name)
            user.email = validated_data.get("email", user.email)

            if request.user.is_staff:
                user.is_active = validated_data.get("is_active", user.is_active)

            if "password" in validated_data:
                user.set_password(validated_data["password"])

            user.save()

            response_serializer = UserResponseSerializer(user)
            logger.info(f"Usuário atualizado: {user.email}")
            return Response(
                {
                    "message": "Usuário atualizado com sucesso",
                    "user": response_serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except IntegrityError:
            return Response(
                {"error": "Email já cadastrado por outro usuário"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            logger.error(f"Erro ao atualizar usuário {user_id}: {e}")
            return Response(
                {"error": "Erro ao atualizar usuário"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        responses={200: '{"message": "Usuário desativado com sucesso"}'}
    )
    def delete(self, request, user_id):

        if not request.user.is_staff and request.user.id != user_id:
            return Response(
                {"error": "Você não tem permissão para deletar este usuário."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user = self.get_object(user_id, request.user)
        if not user:
            return Response(
                {"error": "Usuário não encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        user.is_active = False
        user.save(update_fields=["is_active"])

        logger.info(f"Usuário desativado: {user.email}")
        return Response(
            {"message": "Usuário desativado com sucesso"}, status=status.HTTP_200_OK
        )


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=UserLoginSerializer,
        responses={200: "{'access': '...', 'refresh': '...', 'user': {...}}"},
    )
    @method_decorator(ratelimit(key="ip", rate="5/m", method="POST"))
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        validated_data = serializer.validated_data
        try:
            user = User.objects.get(email=validated_data["email"])

            if (
                not user.check_password(validated_data["password"])
                or not user.is_active
            ):
                return Response(
                    {"error": "Credenciais inválidas"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            refresh = RefreshToken.for_user(user)

            response_serializer = UserResponseSerializer(user)
            logger.info(f"Login bem-sucedido: {user.email}")

            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": response_serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            return Response(
                {"error": "Credenciais inválidas"}, status=status.HTTP_401_UNAUTHORIZED
            )

        except Exception as e:
            logger.error(f"Erro no login: {e}")
            return Response(
                {"error": "Erro ao realizar login"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
