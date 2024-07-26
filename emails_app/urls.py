from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('test/', views.test, name='test'),
    path('obtain-token/', views.obtain_token, name='obtain_token'),
    path('send-single-email/', views.send_single_email, name='send_single_email'),
    path('send-bulk-email/', views.send_bulk_email, name='send_bulk_email'),
]
