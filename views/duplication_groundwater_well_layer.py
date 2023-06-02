import time

from braces.views import SuperuserRequiredMixin
from django.forms.utils import ErrorList
from django.shortcuts import render, redirect
from django.views.generic.list import View

from gwml2.forms.duplication_groundwater_well_layer import (
    DuplicationGroundwaterWellLayerForm
)


class DuplicationGroundwaterWellLayerFormView(SuperuserRequiredMixin, View):
    template_name = 'duplication_groundwater_well_layer.html'

    def get(self, request, *args, **kwargs):
        context = {
            'form': DuplicationGroundwaterWellLayerForm()
        }
        return render(
            request, self.template_name, context
        )

    def post(self, request, *args, **kwargs):
        form = DuplicationGroundwaterWellLayerForm(request.POST)
        if form.is_valid():
            try:
                redirect_url = form.run()
                return redirect(redirect_url)
            except Exception as e:
                errors = form._errors.setdefault("name", ErrorList())
                errors.append(f'{e}')
        return render(request, self.template_name, {"form": form})
