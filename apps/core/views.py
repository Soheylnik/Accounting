
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin


class indexView(View):
    template_name = 'core/index.html'

    def get(self, request):
        return render(request, self.template_name)


class DashboardHomeView(LoginRequiredMixin, View):
    template_name = 'base/home_dashboard.html'
    login_url = 'accounts:login'

    def get(self, request):
        return render(request, self.template_name)
