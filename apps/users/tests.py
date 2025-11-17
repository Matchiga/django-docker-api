import pytest 
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from core.database import SessionLocal, UserModel, reset_database
from core.security import hash_password, verify_password

@pytest.fixture(scope='function')
def api_client():
    return APIClient()

@pytest.fixture(scope='function')
def clean_database():
    if True:
        reset_database()
    yield
    
class TestUserSecurity(TestCase):
    def test_password_hashing(self):
        password = "SenhaForte123!"
        hashed = hash_password(password)
        
        self.assertNotEqual(password, hashed)
        self.assertTrue(hashed.startswith('$2b$'))
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("SenhaErrada", hashed))
        
    def test_password_not_returned_in_response(self):
        db = SessionLocal()
        try:
            user = UserModel(
                name="Test User",
                email="test@example.com",
                password_hash=hash_password("SenhaForte123!"),
                is_active=True
            )
            
            user_dict = user.to_dict()
            
            self.assertNotIn('password', user_dict)
            self.assertNotIn('password_hash', user_dict)
            
            self.assertIn('id', user_dict)
            self.assertIn('name', user_dict)
            self.assertIn('email', user_dict)
            
        finally:
            db.close()
            
@pytest.mark.django_db
class TestUserAPI:
    def test_create_user_success(self, api_client, clean_database):
        data = {
            "name": "João Silva",
            "email": "joao@example.com",
            "password": "SenhaForte123!"
        }
        
        response = api_client.post('/api/users/', data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert response.data['user']['email'] == data['email']
        
        assert 'password' not in response.data['user']
        assert 'password_hash' not in response.data['user']
        
    def test_create_user_duplicate_email(self, api_client, clean_database):
        data = {
            "name": "João Silva",
            "email": "joao@example.com",
            "password": "SenhaForte123!"
        }
        
        response1 = api_client.post('/api/users/', data, format='json')
        assert response1.status_code == status.HTTP_201_CREATED
        
        response2 = api_client.post('/api/users/', data, format='json')
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in str(response2.data).lower()
        
    def test_list_users(self, api_client, clean_database):
        for i in range(3):
            data = {
                "name": f"User {i}",
                "email": f"user{i}@example.com",
                "password": "SenhaForte123!"
            }
            api_client.post('/api/users/', data, format='json')
            
        response = api_client.get('/api/users/')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) == 3
        
        for user in response.data['results']:
            assert 'password' not in user
            assert 'password_hash' not in user
        
    def test_get_user_by_id(self, api_client, clean_database):
        data = {
            "name": "João Silva",
            "email": "joao@example.com",
            "password": "SenhaForte123!"
        }
        
        create_response = api_client.post('/api/users/', data, format='json')
        user_id = create_response.data['user']['id']
        
        response = api_client.get(f'/api/users/{user_id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == data['email']
        
        assert 'password' not in response.data
        assert 'password_hash' not in response.data
        
    def test_update_user(self, api_client, clean_database):
        data = {
            "name": "João Silva",
            "email": "joao@example.com",
            "password": "SenhaForte123!"
        }
        create_response = api_client.post('/api/users/', data, format='json')
        user_id = create_response.data['user']['id']
        
        # Atualiza usuário
        update_data = {"name": "João Silva Atualizado"}
        response = api_client.put(
            f'/api/users/{user_id}/',
            update_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['name'] == update_data['name']
    
    def test_delete_user_soft_delete(self, api_client, clean_database):
        """Testa soft delete de usuário"""
        # Cria usuário
        data = {
            "name": "João Silva",
            "email": "joao@example.com",
            "password": "SenhaForte123!"
        }
        create_response = api_client.post('/api/users/', data, format='json')
        user_id = create_response.data['user']['id']
        
        # Deleta usuário
        response = api_client.delete(f'/api/users/{user_id}/')
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verifica se usuário foi desativado (não deletado do banco)
        db = SessionLocal()
        try:
            user = db.query(UserModel).filter(UserModel.id == user_id).first()
            assert user is not None  # Ainda existe no banco
            assert user.is_active is False  # Mas está inativo
        finally:
            db.close()
    
    def test_login_success(self, api_client, clean_database):
        """Testa login com sucesso"""
        # Cria usuário
        password = "SenhaForte123!"
        data = {
            "name": "João Silva",
            "email": "joao@example.com",
            "password": password
        }
        api_client.post('/api/users/', data, format='json')
        
        # Tenta fazer login
        login_data = {
            "email": "joao@example.com",
            "password": password
        }
        response = api_client.post('/api/users/login/', login_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'user' in response.data
    
    def test_login_wrong_password(self, api_client, clean_database):
        """Testa login com senha errada"""
        # Cria usuário
        data = {
            "name": "João Silva",
            "email": "joao@example.com",
            "password": "SenhaForte123!"
        }
        api_client.post('/api/users/', data, format='json')
        
        # Tenta fazer login com senha errada
        login_data = {
            "email": "joao@example.com",
            "password": "SenhaErrada123!"
        }
        response = api_client.post('/api/users/login/', login_data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_invalid_email_format(self, api_client, clean_database):
        """Testa criação com email inválido"""
        data = {
            "name": "João Silva",
            "email": "email-invalido",  # Email sem @
            "password": "SenhaForte123!"
        }
        
        response = api_client.post('/api/users/', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST