import io
import qrcode
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import KittenPostForm, KittenProfileForm
from .models import KittenPost, KittenProfile


def get_default_kitten():
    profile, _ = KittenProfile.objects.get_or_create(
        slug='mais',
        defaults={
            'name': 'Mais',
            'tagline': 'Femmina · 7 settimane · Piccola panterina nera',
            'age_text': '7 settimane circa',
            'gender': 'Femmina',
            'color': 'Completamente nera',
            'location': 'Pescara (zona Aeroporto) e dintorni',
            'phone_number': '',
        }
    )
    return profile


def kitten_detail(request, slug='mais'):
    profile = get_object_or_404(KittenProfile, slug=slug)
    posts = profile.posts.all().order_by('-created_at')

    # Check if request came from staff for quick edit links
    is_admin = request.user.is_authenticated and request.user.is_staff

    return render(request, 'kitten/detail.html', {
        'kitten': profile,
        'posts': posts,
        'is_admin': is_admin,
        'production_url': f'https://labustagialla.it/{profile.slug}/',
    })


def kitten_redirect(request):
    return redirect('kitten_detail')


@require_POST
def kitten_like(request, slug='mais'):
    profile = get_object_or_404(KittenProfile, slug=slug)
    post_id = request.POST.get('post_id')

    if post_id:
        post = get_object_or_404(KittenPost, id=post_id, kitten=profile)
        post.likes += 1
        post.save(update_fields=['likes'])
        return JsonResponse({'success': True, 'type': 'post', 'likes': post.likes})
    else:
        profile.likes_count += 1
        profile.save(update_fields=['likes_count'])
        return JsonResponse({'success': True, 'type': 'profile', 'likes': profile.likes_count})


def kitten_qr(request, slug='mais'):
    profile = get_object_or_404(KittenProfile, slug=slug)
    # Always target production domain for QR codes so flyers work anywhere
    target_url = f'https://labustagialla.it/{profile.slug}/'

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(target_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#181716", back_color="#ffffff")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return HttpResponse(buffer.getvalue(), content_type='image/png')


def kitten_flyer_a4(request, slug='mais'):
    profile = get_object_or_404(KittenProfile, slug=slug)
    return render(request, 'kitten/flyer_a4.html', {
        'kitten': profile,
        'target_url': f'https://labustagialla.it/{profile.slug}/',
        'is_admin': request.user.is_authenticated and request.user.is_staff,
    })


def kitten_flyer_a5(request, slug='mais'):
    profile = get_object_or_404(KittenProfile, slug=slug)
    return render(request, 'kitten/flyer_a5.html', {
        'kitten': profile,
        'target_url': f'https://labustagialla.it/{profile.slug}/',
        'is_admin': request.user.is_authenticated and request.user.is_staff,
    })


def _staff_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('panel_login')}?next={request.path}")
        if not request.user.is_staff:
            return redirect('kitten_detail')
        return view_func(request, *args, **kwargs)
    return wrapper


@_staff_required
def kitten_admin(request, slug='mais'):
    profile = get_object_or_404(KittenProfile, slug=slug)
    posts = profile.posts.all().order_by('-created_at')

    profile_form = KittenProfileForm(instance=profile)
    post_form = KittenPostForm()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_profile':
            profile_form = KittenProfileForm(request.POST, request.FILES, instance=profile)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Dati di Mais aggiornati con successo!')
                return redirect('kitten_admin')
            else:
                messages.error(request, 'Errore durante il salvataggio dei dati.')

        elif action == 'add_post':
            post_form = KittenPostForm(request.POST, request.FILES)
            if post_form.is_valid():
                new_post = post_form.save(commit=False)
                new_post.kitten = profile
                new_post.save()
                messages.success(request, 'Nuovo post pubblicato con successo nel feed!')
                return redirect('kitten_admin')
            else:
                messages.error(request, 'Errore durante il caricamento del post. Verifica i file.')

    return render(request, 'kitten/admin.html', {
        'kitten': profile,
        'posts': posts,
        'profile_form': profile_form,
        'post_form': post_form,
    })


@_staff_required
@require_POST
def kitten_delete_post(request, post_id):
    post = get_object_or_404(KittenPost, id=post_id)
    post.delete()
    messages.success(request, 'Post eliminato con successo.')
    return redirect('kitten_admin')
