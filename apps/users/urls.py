from django.urls import path
from .views import UserListCreateView, UserDetailView, UserLoginView

app_name = 'users'

urlpatterns = [
    path('', UserListCreateView.as_view(), name='user-list-create'),
    
    path('<int:user_id>/', UserDetailView.as_view(), name='user-detail'),
    
    path('login/', UserLoginView.as_view(), name='user-login'),
]