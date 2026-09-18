from django.urls import path
from . import views

urlpatterns = [
    # Public page
    path('mais/', views.kitten_detail, name='kitten_detail'),
    path('mais/like/', views.kitten_like, name='kitten_like'),
    path('mais/qr/', views.kitten_qr, name='kitten_qr'),
    path('mais/volantino/a4/', views.kitten_flyer_a4, name='kitten_flyer_a4'),
    path('mais/volantino/a5/', views.kitten_flyer_a5, name='kitten_flyer_a5'),

    # Admin management panel (also linked inside /panel/)
    path('mais/gestione/', views.kitten_admin, name='kitten_admin'),
    path('mais/post/<int:post_id>/delete/', views.kitten_delete_post, name='kitten_delete_post'),

    # Friendly redirects
    path('adotta/', views.kitten_redirect, name='kitten_adotta'),
    path('gattino/', views.kitten_redirect, name='kitten_gattino'),
]
