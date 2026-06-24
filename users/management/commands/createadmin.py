from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    def handle(self, *args, **options):
        User = get_user_model()

        email = 'testadmin@mail.ru'

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'Пользователь {email} уже существует.'))
            return

        user = User.objects.create(
            email=email,
            first_name='Admin',
            last_name='Adminoff',
            is_staff=True,
            is_superuser=True,
        )

        user.set_password('1234')
        user.save()

        self.stdout.write(self.style.SUCCESS(f'Успешное создание суперпользователя {user.email}.'))
