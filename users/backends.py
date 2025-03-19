from django.contrib.auth import get_user_model

User = get_user_model()


class MultiFieldAuthBackend:
    def authenticate(self, request, login_identifier=None, password=None, **kwargs):
        if not login_identifier or not password:
            return None

        user = None

        if '@' in login_identifier:
            user = User.objects.filter(email=login_identifier).first()

        if not user and login_identifier.isdigit():
            user = User.objects.filter(phone_number=login_identifier).first()

        if not user:
            user = User.objects.filter(username=login_identifier).first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

    def user_can_authenticate(self, user):
        return user.is_active
