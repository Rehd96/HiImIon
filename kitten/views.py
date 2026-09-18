import hashlib
import io
import json
import uuid
import qrcode
from django.conf import settings
from django.contrib import messages
from django.db.models import Avg, Count
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .forms import KittenPostForm, KittenProfileForm
from .models import (
    KittenInquiry,
    KittenInquiryMessage,
    KittenPost,
    KittenPostImpression,
    KittenProfile,
    KittenVisitorSession,
)
from .telegram import notify_new_inquiry, send_telegram_message


BOT_MARKERS = (
    'bot', 'crawler', 'spider', 'slurp', 'curl/', 'wget', 'python-requests',
    'httpx', 'go-http-client', 'headlesschrome', 'lighthouse', 'monitor',
    'uptime', 'scrapy', 'facebookexternalhit', 'preview', 'fetcher',
)


def get_client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '').strip()
    return (
        forwarded.split(',')[0].strip()
        or request.META.get('HTTP_X_REAL_IP', '').strip()
        or request.META.get('REMOTE_ADDR', '')
        or ''
    )


def is_bot_request(user_agent):
    if not user_agent:
        return False
    ua = user_agent.lower()
    return any(marker in ua for marker in BOT_MARKERS)


def compute_visitor_hash(ip, user_agent):
    raw = f"{timezone.localdate().isoformat()}|{ip}|{user_agent}"
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:32]


def detect_device_type(user_agent):
    if not user_agent:
        return 'desktop'
    ua = user_agent.lower()
    if 'tablet' in ua or 'ipad' in ua:
        return 'tablet'
    if 'mobile' in ua or 'android' in ua or 'iphone' in ua:
        return 'mobile'
    return 'desktop'


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
    is_admin = request.user.is_authenticated and request.user.is_staff

    # Ref or utm_source from query params (e.g. ?ref=flyer_a4)
    ref = request.GET.get('ref', '') or request.GET.get('utm_source', '')

    return render(request, 'kitten/detail.html', {
        'kitten': profile,
        'posts': posts,
        'is_admin': is_admin,
        'ref_param': ref,
        'production_url': f'https://labustagialla.it/{profile.slug}/',
    })


def kitten_redirect(request):
    return redirect('kitten_detail')


@csrf_exempt
@require_POST
def kitten_like(request, slug='mais'):
    profile = get_object_or_404(KittenProfile, slug=slug)
    post_id = request.POST.get('post_id')
    sid = request.POST.get('sid', '').strip()

    # Track like in session if sid provided
    if sid:
        session = KittenVisitorSession.objects.filter(session_id=sid).first()
        if session:
            session.likes_given += 1
            session.save(update_fields=['likes_given', 'updated_at'])

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
    ref = request.GET.get('ref', '')
    target_url = f'https://labustagialla.it/{profile.slug}/'
    if ref:
        target_url = f'{target_url}?ref={ref}'

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
        'target_url': f'https://labustagialla.it/{profile.slug}/?ref=flyer_a4',
        'qr_ref': 'flyer_a4',
        'is_admin': request.user.is_authenticated and request.user.is_staff,
    })


def kitten_flyer_a5(request, slug='mais'):
    profile = get_object_or_404(KittenProfile, slug=slug)
    return render(request, 'kitten/flyer_a5.html', {
        'kitten': profile,
        'target_url': f'https://labustagialla.it/{profile.slug}/?ref=flyer_a5',
        'qr_ref': 'flyer_a5',
        'is_admin': request.user.is_authenticated and request.user.is_staff,
    })


# ─────────────────────────────────────────────────────────────────────────────
#  ANALYTICS & BEACON LOGGING (Cookieless, GDPR-compliant)
# ─────────────────────────────────────────────────────────────────────────────

@csrf_exempt
@require_POST
def kitten_analytics_log(request, slug='mais'):
    """
    Heartbeat and interaction logging beacon.
    Does NOT set or require any tracking cookies: uses an ephemeral session ID generated
    in client sessionStorage and a daily salted hash of IP/UA.
    """
    profile = get_object_or_404(KittenProfile, slug=slug)

    # Parse JSON or POST body
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request.POST
    except Exception:
        data = request.POST

    sid = str(data.get('sid', '')).strip()[:64]
    if not sid:
        return JsonResponse({'ok': False, 'error': 'Missing session ID'}, status=400)

    ip = get_client_ip(request)
    ua = request.META.get('HTTP_USER_AGENT', '')[:400]

    # Don't track known bots
    if is_bot_request(ua):
        return JsonResponse({'ok': True, 'bot': True})

    seconds = int(data.get('seconds', 0) or 0)
    scroll = min(100, max(0, int(data.get('scroll', 0) or 0)))
    ref = str(data.get('ref', '')).strip()[:500]
    utm = str(data.get('utm', '')).strip()[:100]
    action = str(data.get('action', '')).strip()[:50]
    posts_seen = data.get('posts', [])
    if isinstance(posts_seen, str):
        try:
            posts_seen = json.loads(posts_seen)
        except Exception:
            posts_seen = []

    visitor_hash = compute_visitor_hash(ip, ua)
    device = detect_device_type(ua)

    session, created = KittenVisitorSession.objects.get_or_create(
        session_id=sid,
        defaults={
            'kitten': profile,
            'visitor_hash': visitor_hash,
            'ip_address': ip,
            'user_agent': ua,
            'device_type': device,
            'referer': ref,
            'utm_source': utm,
            'total_seconds': seconds,
            'max_scroll_percent': scroll,
            'reached_feed': scroll >= 30,
            'reached_adoption': scroll >= 70,
            'clicked_whatsapp': action == 'whatsapp',
            'clicked_call': action == 'call',
            'clicked_chat': action == 'chat_open',
        }
    )

    if not created:
        update_fields = ['total_seconds', 'max_scroll_percent', 'updated_at']
        if seconds > session.total_seconds:
            session.total_seconds = seconds
        if scroll > session.max_scroll_percent:
            session.max_scroll_percent = scroll
        if scroll >= 30 and not session.reached_feed:
            session.reached_feed = True
            update_fields.append('reached_feed')
        if scroll >= 70 and not session.reached_adoption:
            session.reached_adoption = True
            update_fields.append('reached_adoption')

        # Action signals
        if action == 'whatsapp' and not session.clicked_whatsapp:
            session.clicked_whatsapp = True
            update_fields.append('clicked_whatsapp')
        elif action == 'call' and not session.clicked_call:
            session.clicked_call = True
            update_fields.append('clicked_call')
        elif action == 'chat_open' and not session.clicked_chat:
            session.clicked_chat = True
            update_fields.append('clicked_chat')

        session.save(update_fields=update_fields)

    # Record post impressions
    if posts_seen and isinstance(posts_seen, list):
        for pid in posts_seen:
            try:
                pid_int = int(pid)
                KittenPostImpression.objects.get_or_create(
                    session=session,
                    post_id=pid_int
                )
            except Exception:
                continue

    return JsonResponse({'ok': True})


# ─────────────────────────────────────────────────────────────────────────────
#  IN-SITE ADOPTION CHAT & TELEGRAM NOTIFICATIONS
# ─────────────────────────────────────────────────────────────────────────────

@csrf_exempt
@require_POST
def kitten_chat_send(request, slug='mais'):
    """
    Receives an adoption inquiry / chat message from the public site.
    Sends an instant notification to Telegram.
    """
    profile = get_object_or_404(KittenProfile, slug=slug)

    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request.POST
    except Exception:
        data = request.POST

    token = str(data.get('token', '')).strip()
    name = str(data.get('name', '')).strip()[:120]
    contact = str(data.get('contact', '')).strip()[:150]
    message_text = str(data.get('message', '')).strip()

    if not message_text:
        return JsonResponse({'success': False, 'error': 'Inserisci un messaggio.'}, status=400)

    # If an existing inquiry token is provided, continue that thread
    inquiry = None
    if token:
        inquiry = KittenInquiry.objects.filter(inquiry_token=token, kitten=profile).first()

    # Otherwise create a new inquiry thread
    if not inquiry:
        if not name:
            name = 'Visitatore del sito'
        if not contact:
            contact = 'Non specificato'
        inquiry = KittenInquiry.objects.create(
            kitten=profile,
            inquiry_token=uuid.uuid4().hex[:24],
            name=name,
            contact=contact,
            status='new'
        )
    else:
        # Update name/contact if newly provided
        if name and inquiry.name == 'Visitatore del sito':
            inquiry.name = name
        if contact and inquiry.contact == 'Non specificato':
            inquiry.contact = contact
        inquiry.status = 'new'
        inquiry.save(update_fields=['name', 'contact', 'status', 'updated_at'])

    # Create message
    msg = KittenInquiryMessage.objects.create(
        inquiry=inquiry,
        sender='visitor',
        text=message_text
    )

    # Dispatch Telegram notification
    try:
        notify_new_inquiry(profile, inquiry, message_text)
    except Exception:
        pass

    # Return full message history for this conversation
    messages_list = [
        {
            'id': m.id,
            'sender': m.sender,
            'text': m.text,
            'time': m.created_at.strftime('%H:%M'),
            'date': m.created_at.strftime('%d/%m/%Y'),
        }
        for m in inquiry.messages.all()
    ]

    return JsonResponse({
        'success': True,
        'token': inquiry.inquiry_token,
        'name': inquiry.name,
        'contact': inquiry.contact,
        'messages': messages_list,
    })


@require_GET
def kitten_chat_messages(request, slug='mais'):
    """
    Polls messages for an existing inquiry token so the visitor sees admin replies in real time.
    """
    profile = get_object_or_404(KittenProfile, slug=slug)
    token = request.GET.get('token', '').strip()

    if not token:
        return JsonResponse({'success': False, 'messages': []})

    inquiry = KittenInquiry.objects.filter(inquiry_token=token, kitten=profile).first()
    if not inquiry:
        return JsonResponse({'success': False, 'messages': []})

    messages_list = [
        {
            'id': m.id,
            'sender': m.sender,
            'text': m.text,
            'time': m.created_at.strftime('%H:%M'),
            'date': m.created_at.strftime('%d/%m/%Y'),
        }
        for m in inquiry.messages.all()
    ]

    return JsonResponse({
        'success': True,
        'status': inquiry.status,
        'messages': messages_list,
    })


# ─────────────────────────────────────────────────────────────────────────────
#  ADMIN AREA & TELEGRAM BOT MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────

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
                messages.success(request, 'Dati di Mais e impostazioni aggiornati con successo!')
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

    # ── ANALYTICS DATA ──
    now = timezone.now()
    today_start = timezone.localdate()

    all_sessions = profile.visitor_sessions.all()
    total_visitors = all_sessions.count()
    today_visitors = all_sessions.filter(created_at__date=today_start).count()

    # Engaged sessions (> 3s)
    engaged_sessions = all_sessions.filter(total_seconds__gte=3)
    avg_sec = engaged_sessions.aggregate(Avg('total_seconds'))['total_seconds__avg'] or 0
    avg_scroll = all_sessions.aggregate(Avg('max_scroll_percent'))['max_scroll_percent__avg'] or 0

    # Conversions
    feed_reached = all_sessions.filter(reached_feed=True).count()
    adoption_reached = all_sessions.filter(reached_adoption=True).count()
    whatsapp_clicks = all_sessions.filter(clicked_whatsapp=True).count()
    call_clicks = all_sessions.filter(clicked_call=True).count()
    chat_opens = all_sessions.filter(clicked_chat=True).count()

    # Devices
    mobile_count = all_sessions.filter(device_type='mobile').count()
    desktop_count = all_sessions.filter(device_type='desktop').count()
    tablet_count = all_sessions.filter(device_type='tablet').count()

    # Post Leaderboard (Impressions & Likes)
    posts_stats = []
    for p in posts:
        imp_count = KittenPostImpression.objects.filter(post=p).count()
        posts_stats.append({
            'post': p,
            'impressions': imp_count,
            'likes': p.likes,
        })

    # Recent 30 Visitor Sessions
    recent_sessions = all_sessions.prefetch_related('impressions__post')[:30]

    # Inquiries & Chat Threads
    inquiries = profile.inquiries.prefetch_related('messages').all()
    new_inquiries_count = inquiries.filter(status='new').count()

    return render(request, 'kitten/admin.html', {
        'kitten': profile,
        'posts': posts,
        'profile_form': profile_form,
        'post_form': post_form,
        # Analytics
        'total_visitors': total_visitors,
        'today_visitors': today_visitors,
        'avg_seconds': int(avg_sec),
        'avg_seconds_formatted': f"{int(avg_sec // 60)}m {int(avg_sec % 60)}s" if avg_sec >= 60 else f"{int(avg_sec)}s",
        'avg_scroll': int(avg_scroll),
        'feed_reached': feed_reached,
        'adoption_reached': adoption_reached,
        'whatsapp_clicks': whatsapp_clicks,
        'call_clicks': call_clicks,
        'chat_opens': chat_opens,
        'mobile_count': mobile_count,
        'desktop_count': desktop_count,
        'tablet_count': tablet_count,
        'posts_stats': posts_stats,
        'recent_sessions': recent_sessions,
        # Chat & Inquiries
        'inquiries': inquiries,
        'new_inquiries_count': new_inquiries_count,
    })


@_staff_required
@require_POST
def kitten_admin_reply_chat(request, inquiry_id):
    """
    Allows the admin to reply to an in-site chat inquiry directly from /mais/gestione/.
    """
    inquiry = get_object_or_404(KittenInquiry, id=inquiry_id)
    reply_text = request.POST.get('reply_text', '').strip()

    if reply_text:
        KittenInquiryMessage.objects.create(
            inquiry=inquiry,
            sender='admin',
            text=reply_text
        )
        inquiry.status = 'replied'
        inquiry.save(update_fields=['status', 'updated_at'])
        messages.success(request, f"Risposta inviata con successo a {inquiry.name}!")
    else:
        messages.error(request, "Il testo della risposta non può essere vuoto.")

    return redirect(f"{reverse('kitten_admin')}#inquiries")


@_staff_required
@require_POST
def kitten_telegram_test(request, slug='mais'):
    """
    Sends a test Telegram message to verify that the bot token and chat ID are working.
    """
    profile = get_object_or_404(KittenProfile, slug=slug)
    bot_token = request.POST.get('telegram_bot_token') or profile.telegram_bot_token or getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    chat_id = request.POST.get('telegram_chat_id') or profile.telegram_chat_id or getattr(settings, 'TELEGRAM_CHAT_ID', '')

    if not bot_token or not chat_id:
        messages.error(request, "Inserisci sia il Token del Bot che il Chat ID per eseguire il test.")
        return redirect(f"{reverse('kitten_admin')}#telegram")

    test_msg = (
        "🐾 <b>TEST NOTIFICA TELEGRAM PER MAIS RIUSCITO!</b> 🐾\n\n"
        "Il bot è configurato correttamente su <b>labustagialla.it</b> e riceverà "
        "immediatamente ogni nuova richiesta di adozione o messaggio inviato dal sito!"
    )
    ok, err = send_telegram_message(bot_token, chat_id, test_msg)
    if ok:
        messages.success(request, "🎉 Notifica Telegram di test inviata con successo! Controlla la tua chat su Telegram.")
    else:
        messages.error(request, f"❌ Errore Telegram: {err}")

    return redirect(f"{reverse('kitten_admin')}#telegram")


@_staff_required
@require_POST
def kitten_delete_post(request, post_id):
    post = get_object_or_404(KittenPost, id=post_id)
    post.delete()
    messages.success(request, 'Post eliminato con successo.')
    return redirect('kitten_admin')

