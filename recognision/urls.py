from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^create_algorithm/$', views.AlgorithmCreateView.as_view(), name='algorithm_create'),
    url(r'^algorithms/$', views.AlgorithmListView.as_view(), name='algorithm_list'),
    url(r'^testing/$', views.AlgorithmTestCreateView.as_view(), name='testing'),
    url(r'^history/$', views.TestHistoryListView.as_view(), name='test_history'),
]