from django.contrib.auth import get_user_model, user_logged_in
from django.contrib.auth.hashers import check_password
from django.http.response import HttpResponseBadRequest, HttpResponse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from rest_framework import serializers
from rest_framework.views import APIView
from gwml2.models.well_management.user import UserUUID

User = get_user_model()


class TokenAuth(APIView):
    """
    Login with token
    """
    permission_classes = []

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TokenAuth, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args):
        try:
            username = request.data['username']
            password = request.data['password']
            user = self.authenticate(username=username, password=password)
            userUUID, created = UserUUID.objects.get_or_create(user_id=user.id)
            user_logged_in.send(sender=user.__class__, request=request, user=user)
            return HttpResponse('{}'.format(str(userUUID.uuid)))
        except KeyError:
            return HttpResponseBadRequest('username and password is needed in data')

    def authenticate(self, username, password):
        """Custom authentication using case sensitive username."""

        try:
            user = User.objects.get(username__exact=username)
            if check_password(password, user.password):
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise serializers.ValidationError(msg, code='authorization')
                else:
                    return user
            else:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        except User.DoesNotExist:
            msg = _('User does not exist.')
            raise serializers.ValidationError(msg, code='authorization')
