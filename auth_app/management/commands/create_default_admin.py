from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates the default admin account'

    def handle(self, *args, **kwargs):
        email = 'admin@milk.com'
        password = 'Admin@1234'
        username = 'admin'

        # Find by username OR email
        user = User.objects.filter(username=username).first() or \
               User.objects.filter(email=email).first()

        if user:
            user.email = email
            user.set_password(password)
            user.role = 'ADMIN'
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Admin updated: {email} / {password}'))
        else:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            user.role = 'ADMIN'
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Admin created: {email} / {password}'))
