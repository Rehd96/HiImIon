from django.urls import path

from . import panel_views

urlpatterns = [
    path('', panel_views.dashboard, name='panel_dashboard'),
    path('login/', panel_views.panel_login, name='panel_login'),
    path('logout/', panel_views.panel_logout, name='panel_logout'),
    path('views/', panel_views.view_log, name='panel_views'),
]
