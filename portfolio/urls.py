from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('robots.txt', views.robots, name='robots'),
    path('healthz', views.healthz, name='healthz'),
    path('projects/<slug:slug>/', views.project_detail, name='project_detail'),
]
