from django.contrib.auth.models import UserManager
from django.contrib.auth.hashers import make_password

class UserManager(UserManager):
    use_in_migrations = True

    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        else:
            user = self.model(email = email, **extra_fields)
            user.set_password(password)
            user.save()
            return user

    def create_user(self, user, password = None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is  True:
            raise ValueError('user must have is_staff=Fales.')
        if extra_fields.get('is_superuser') is  True:
            raise ValueError('user must have is_superuser=Fales.')
        if extra_fields.get('is_active') is False:
            raise ValueError('user must have is_acive=True')

        return self._create_user(user, password, **extra_fields)
        

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self._create_user(email, password, **extra_fields)