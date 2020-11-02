from django.core.exceptions import PermissionDenied
from gwml2.models.well import Well
from gwml2.utilities import allow_to_edit_well


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
            id = parameters.get('id', None)
            well = Well.objects.get(id=id)
            return well.editor_permission(user)
        except Well.DoesNotExist:
            return allow_to_edit_well(user)

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permissions(request.user, kwargs):
            raise PermissionDenied('You do not have permission.')
        return super(EditWellFormMixin, self).dispatch(request, *args, **kwargs)
