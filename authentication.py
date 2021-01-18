from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework.authentication import (
    TokenAuthentication, exceptions)
from gwml2.models.well_management.user import UserUUID

User = get_user_model()


class GWMLTokenAthentication(TokenAuthentication):
    """ Authentication using GWML token
        """

    def authenticate_credentials(self, key):
        model = UserUUID
        try:
            token = model.objects.get(uuid=key)
            user = User.objects.get(id=token.user_id)
        except (model.DoesNotExist, ValidationError):
            raise exceptions.AuthenticationFailed(_('Invalid token.'))
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('No user found for the token.'))

        if not user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        return (user, token)
