from django.db import connection
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.base import SessionBase

from .models import UserSession
from .rpc import get_pool

User = get_user_model()
session_util = SessionBase()


class GetUserHelper:
    @classmethod
    def get_user(cls, session_id):
        if not session_id:
            return AnonymousUser()
        try:
            session = UserSession.objects.get(
                session_key=session_id,
                expire_date__gt=timezone.now()
            )
            return session.user
        except UserSession.DoesNotExist:
            return cls.get_user_from_auth_service(session_id)

    @classmethod
    def get_user_from_auth_service(cls, session_id):
        with get_pool().next() as rpc:
            response = rpc.auth_service.get_user_by_session_key(session_id)
        if not response:
            return AnonymousUser()
        assert isinstance(response, dict) and isinstance(response.get('id'), int)

        user = cls.update_or_create_user(id=response['id'], defaults={
            'email': response.get('email'),
            'is_active': True,
            'is_staff': response.get('is_staff', False),
            'is_superuser': response.get('is_superuser', False),
            'is_trainer': response.get('is_trainer', False),
            'avatar': response.get('avatar', ''),
            'nickname': response.get('nickname', ''),
        })
        UserSession.objects.update_or_create(
            user=user,
            session_key=session_id,
            defaults={
                'expire_date': session_util.get_expiry_date()
            }
        )
        return user

    @classmethod
    def update_or_create_user(cls, **kwargs):
        defaults = kwargs.pop('defaults', {})
        user, _ = User.objects.update_or_create(defaults=defaults, **kwargs)
        cls.fix_user_pk_sequence()
        return user

    @staticmethod
    def fix_user_pk_sequence():
        query = """
          SELECT pg_catalog.setval(
            pg_get_serial_sequence('%(db_table)s', '%(pk_field)s'),
            (SELECT MAX(id) FROM %(db_table)s) + 1
          );
        """ % {'db_table': User._meta.db_table, 'pk_field': User._meta.pk.name}  # noqa
        with connection.cursor() as cursor:
            cursor.execute(query)
