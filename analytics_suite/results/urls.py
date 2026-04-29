from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('upload/', views.upload_csv),
    path('preview/', views.preview_csv),
    path('save/', views.save_csv),
    path('analytics/', views.analytics),
    path('pdf/', views.generate_pdf),
]