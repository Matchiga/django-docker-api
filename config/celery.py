import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('user_api')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')



@app.task(name='send_welcome_email')
def send_welcome_email(user_email, user_name):
    from django.core.mail import send_mail
    
    send_mail(
        subject='Bem-vindo!',
        message=f'Olá {user_name}, bem-vindo ao nosso sistema!',
        from_email='noreply@example.com',
        recipient_list=[user_email],
        fail_silently=False,
    )
    
    return f'Email enviado para {user_email}'


@app.task(name='cleanup_inactive_users')
def cleanup_inactive_users():
    from datetime import timedelta
    from django.utils import timezone
    from apps.users.models import User

    cutoff_date = timezone.now() - timedelta(days=30)
        
    inactive_users = User.objects.filter(
        is_active = False,
        updated_at__lt=cutoff_date
    )
        
    count, _ = inactive_users.delete()[0]
        
    return f'{count} usuários inativos removidos'


@app.task(name='generate_user_report')
def generate_user_report():
    from core.database import SessionLocal, UserModel
    
    db = SessionLocal()
    try:
        total_users = db.query(UserModel).count()
        active_users = db.query(UserModel).filter(UserModel.is_active == True).count()
        inactive_users = total_users - active_users
        
        report = {
            'total': total_users,
            'active': active_users,
            'inactive': inactive_users,
            'active_percentage': (active_users / total_users * 100) if total_users > 0 else 0
        }
        
        return report
    
    finally:
        db.close()