from cmath import phase

from django.db import models
from django.core.validators import RegexValidator, ValidationError
from django.template.defaultfilters import phone2numeric_filter
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, send_mail

from django.core.exceptions import ValidationError
from django.utils.text import phone2numeric


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone_number, email, password, is_staff, is_superuser, is_admin, **extra_fields):
        if len(password) < 4:
            raise ValueError("Password must be at least 4 characters long")

        if not phone_number:
            raise ValueError('The phone number must be set')

        if not email:
            raise ValueError('The email must be set')

        if User.objects.filter(phone_number=phone_number).exists():
            raise ValidationError(f"The phone number {phone_number} is already in use.")

        if User.objects.filter(email=email).exists():
            raise ValidationError(f"The email {email} is already in use.")

        email = self.normalize_email(email) if email else None

        user = self.model(
            phone_number=phone_number,
            email=email,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_admin=is_admin,
            is_active=True,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, email, password=None, **extra_fields):
        return self._create_user(
            phone_number=phone_number,
            email=email,
            password=password,
            is_staff=False,
            is_superuser=False,
            is_admin=False,
            **extra_fields
        )

    def create_superuser(self, phone_number, email, password=None, **extra_fields):
        return self._create_user(
            phone_number=phone_number,
            email=email,
            password=password,
            is_staff=True,
            is_superuser=True,
            is_admin=True,
            **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True,
        default=None
    )
    phone_number = models.CharField(
        max_length=11,
        unique=True,
        validators=[RegexValidator(r'^\d{11}$', 'Enter a valid phone number.')]
    )
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone_number', 'email']

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.is_admin = True
            self.is_staff = True
        elif self.is_admin:
            self.is_staff = True

        if not self.is_staff:
            self.is_admin = False
            self.is_superuser = False
        elif not self.is_admin:
            self.is_superuser = False

        if not self.username:
            self.username = self.phone_number

        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            print(f"User created: {self.phone_number} with default password.")

    def __str__(self):
        return f'{self.username}'

    class Meta:
        db_table = 'users'
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)