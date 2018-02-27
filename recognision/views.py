from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView, ListView
from django.shortcuts import get_object_or_404

from .forms import AlgorithmCreationForm, TestAlgorithmCreationForm
from .models import Algorithm, ImageExample, History
from .tasks import run_image_processing, run_test_processing

class AlgorithmCreateView(LoginRequiredMixin, FormView):
    form_class = AlgorithmCreationForm
    template_name = 'recognision/create_algorithm.html'
    success_url = reverse_lazy('recognision:algorithm_list')

    def form_valid(self, form):
        name = form.cleaned_data.get('name')
        algorithm = Algorithm.objects.create(owner=self.request.user, name=name, type='CUSTOM', status='In progress')

        positive_files = form.cleaned_data.get('positive_files')
        positive_url = form.cleaned_data.get('positive_url')
        negative_url = form.cleaned_data.get('negative_url')

        if positive_files:
            for file in self.request.FILES.getlist('positive_files'):
                ImageExample.objects.create(algorithm=algorithm, image_type='positive', file=file)
        run_image_processing.delay(algorithm.id, positive_url, negative_url)
        return super(AlgorithmCreateView, self).form_valid(form)


class AlgorithmListView(LoginRequiredMixin, ListView):
    template_name = 'recognision/algorithm_list_view.html'
    # добавить скачивание xml файла с сервера

    def get_queryset(self):
        qs = Algorithm.objects.filter(type='CUSTOM', owner=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super(AlgorithmListView, self).get_context_data(**kwargs)
        print(context)
        return context


class TestHistoryListView(LoginRequiredMixin, ListView):
    template_name = 'testing/history_list_view.html'

    def get_queryset(self):
        qs = History.objects.filter(user=self.request.user)
        return qs

class AlgorithmTestCreateView(LoginRequiredMixin, FormView):
    template_name = 'testing/create_test.html'
    success_url = reverse_lazy('recognision:test_history')
    form_class = TestAlgorithmCreationForm

    def get_form_kwargs(self, form_class=None):
        return {'user': self.request.user}

    def form_valid(self, form):
        name = form.cleaned_data.get('name')
        algorithm_id = form.cleaned_data.get('algorithm_choice')
        algorithm = get_object_or_404(Algorithm, id=algorithm_id)
        ids = []
        for file in self.request.FILES.getlist('input_images'):
            example = History.objects.create(name=name, algorithm=algorithm, input_image=file, user=self.request.user, status='In progress')
            ids.append(str(example.id))
        run_test_processing.delay(ids)
        return super(AlgorithmTestCreateView, self).form_valid(form)

    def form_invalid(self, form):
        print('Form is invalid')
        return super(AlgorithmTestCreateView, self).form_invalid(form)

    def post(self, request, *args, **kwargs):
        form = TestAlgorithmCreationForm(request.POST, request.FILES, user=self.request.user)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)