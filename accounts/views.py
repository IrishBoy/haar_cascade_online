from django.core.urlresolvers import reverse_lazy
from django.views.generic import CreateView

from .forms import RegisterForm

class RegisterView(CreateView):
    template_name = 'accounts/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('accounts:login')