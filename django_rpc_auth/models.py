from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class UserSession(models.Model):
    session_key = models.CharField(_('Session key'), max_length=40, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('User'))
    expire_date = models.DateTimeField(_('Expire date'), db_index=True)

    def __str__(self):
        return self.session_key
