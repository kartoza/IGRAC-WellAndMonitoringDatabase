from django.core.exceptions import PermissionDenied
from gwml2.models.well import Well


class ViewWellFormMixin(object):

    def has_permissions(self, user, parameters):
        try:
            id = parameters['id']
            well = Well.objects.get(id=id)
            return well.editor_permission(user) or well.view_permission(user)
        except KeyError:
            return False
        except Well.DoesNotExist:
            return True

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permissions(request.user, kwargs):
            raise PermissionDenied('You do not have permission.')
        return super(ViewWellFormMixin, self).dispatch(request, *args, **kwargs)


class EditWellFormMixin(object):

    def has_permissions(self, user, parameters):
        try:
            id = parameters['id']
            well = Well.objects.get(id=id)
            return well.editor_permission(user)
        except KeyError:
            return False
        except Well.DoesNotExist:
            return True

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permissions(request.user, kwargs):
            raise PermissionDenied('You do not have permission.')
        return super(ViewWellFormMixin, self).dispatch(request, *args, **kwargs)
