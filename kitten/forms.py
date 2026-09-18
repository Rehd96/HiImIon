import os
from django import forms
from django.core.exceptions import ValidationError
from .models import KittenProfile, KittenPost

ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.mov', '.webm', '.m4v'}
MAX_IMAGE_SIZE_MB = 15
MAX_VIDEO_SIZE_MB = 60


class KittenProfileForm(forms.ModelForm):
    class Meta:
        model = KittenProfile
        fields = [
            # Contatti & Stato
            'phone_number', 'whatsapp_number', 'contact_email', 'location',
            'is_adopted', 'adopted_banner_text', 'whatsapp_message',
            
            # Intestazione & Hero
            'name', 'hero_title', 'tagline', 'hero_badge', 'hero_location_badge',
            'spec_gender', 'spec_age', 'spec_color', 'spec_location', 'cover_image',

            # Storia & Bio
            'story_title', 'bio_intro', 'story_quote',

            # Carattere & Punti Elenco
            'personality_title', 'personality',
            'bullet_1', 'bullet_2', 'bullet_3', 'bullet_4',

            # Stato di Salute & 4 Tappe
            'health_title', 'health_subtitle',
            'health_step1_badge', 'health_step1_title', 'health_step1_desc', 'health_step1_done',
            'health_step2_badge', 'health_step2_title', 'health_step2_desc', 'health_step2_done',
            'health_step3_badge', 'health_step3_title', 'health_step3_desc', 'health_step3_done',
            'health_step4_badge', 'health_step4_title', 'health_step4_desc', 'health_step4_done',

            # Diario & Feed
            'feed_title', 'feed_subtitle', 'feed_empty_title', 'feed_empty_desc',

            # Requisiti Adozione & Call To Action
            'adoption_badge', 'adoption_title', 'adoption_intro', 'adoption_requirements',
            'adoption_cta_title', 'adoption_cta_desc',

            # Volantini
            'flyer_header_badge', 'flyer_title', 'flyer_subtitle',
            'flyer_cta_text', 'flyer_cta_sub', 'flyer_contact_label',

            # Notifiche Telegram
            'telegram_bot_token', 'telegram_chat_id', 'telegram_notifications_enabled',
        ]
        widgets = {
            'telegram_bot_token': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'es. 123456789:ABCdefGhIJKlmNoPQRstuVWXyz'}),
            'telegram_chat_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'es. 123456789 o @mio_canale'}),

            # Text inputs
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Es. 340 1234567'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Lascia vuoto se uguale al telefono'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'tua.email@esempio.it'}),
            'location': forms.TextInput(attrs={'class': 'form-input'}),
            'whatsapp_message': forms.TextInput(attrs={'class': 'form-input'}),
            'hero_title': forms.TextInput(attrs={'class': 'form-input'}),
            'tagline': forms.TextInput(attrs={'class': 'form-input'}),
            'hero_badge': forms.TextInput(attrs={'class': 'form-input'}),
            'hero_location_badge': forms.TextInput(attrs={'class': 'form-input'}),
            'spec_gender': forms.TextInput(attrs={'class': 'form-input'}),
            'spec_age': forms.TextInput(attrs={'class': 'form-input'}),
            'spec_color': forms.TextInput(attrs={'class': 'form-input'}),
            'spec_location': forms.TextInput(attrs={'class': 'form-input'}),
            'story_title': forms.TextInput(attrs={'class': 'form-input'}),
            'personality_title': forms.TextInput(attrs={'class': 'form-input'}),
            'bullet_1': forms.TextInput(attrs={'class': 'form-input'}),
            'bullet_2': forms.TextInput(attrs={'class': 'form-input'}),
            'bullet_3': forms.TextInput(attrs={'class': 'form-input'}),
            'bullet_4': forms.TextInput(attrs={'class': 'form-input'}),
            'health_title': forms.TextInput(attrs={'class': 'form-input'}),
            'health_subtitle': forms.TextInput(attrs={'class': 'form-input'}),
            'health_step1_badge': forms.TextInput(attrs={'class': 'form-input'}),
            'health_step1_title': forms.TextInput(attrs={'class': 'form-input'}),
            'health_step2_badge': forms.TextInput(attrs={'class': 'form-input'}),
            'health_step2_title': forms.TextInput(attrs={'class': 'form-input'}),
            'health_step3_badge': forms.TextInput(attrs={'class': 'form-input'}),
            'health_step3_title': forms.TextInput(attrs={'class': 'form-input'}),
            'health_step4_badge': forms.TextInput(attrs={'class': 'form-input'}),
            'health_step4_title': forms.TextInput(attrs={'class': 'form-input'}),
            'feed_title': forms.TextInput(attrs={'class': 'form-input'}),
            'feed_subtitle': forms.TextInput(attrs={'class': 'form-input'}),
            'feed_empty_title': forms.TextInput(attrs={'class': 'form-input'}),
            'adoption_badge': forms.TextInput(attrs={'class': 'form-input'}),
            'adoption_title': forms.TextInput(attrs={'class': 'form-input'}),
            'adoption_cta_title': forms.TextInput(attrs={'class': 'form-input'}),
            'flyer_header_badge': forms.TextInput(attrs={'class': 'form-input'}),
            'flyer_title': forms.TextInput(attrs={'class': 'form-input'}),
            'flyer_subtitle': forms.TextInput(attrs={'class': 'form-input'}),
            'flyer_cta_text': forms.TextInput(attrs={'class': 'form-input'}),
            'flyer_cta_sub': forms.TextInput(attrs={'class': 'form-input'}),
            'flyer_contact_label': forms.TextInput(attrs={'class': 'form-input'}),
            'adopted_banner_text': forms.TextInput(attrs={'class': 'form-input'}),

            # Textareas
            'bio_intro': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
            'story_quote': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
            'personality': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'health_step1_desc': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
            'health_step2_desc': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
            'health_step3_desc': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
            'health_step4_desc': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
            'feed_empty_desc': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
            'adoption_intro': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
            'adoption_requirements': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
            'adoption_cta_desc': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
        }

    def clean_cover_image(self):
        cover = self.cleaned_data.get('cover_image')
        if cover and hasattr(cover, 'size'):
            ext = os.path.splitext(cover.name)[1].lower()
            if ext not in ALLOWED_IMAGE_EXTENSIONS:
                raise ValidationError(f"Formato non supportato ({ext}). Usa JPG, PNG o WEBP.")
            if cover.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
                raise ValidationError(f"L'immagine supera i {MAX_IMAGE_SIZE_MB}MB.")
        return cover


class KittenPostForm(forms.ModelForm):
    class Meta:
        model = KittenPost
        fields = ['tag', 'title', 'caption', 'image', 'video']
        widgets = {
            'tag': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Titolo o momento (opzionale, es. Nuova pallina!)'
            }),
            'caption': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Scrivi un aneddoto, cosa ha fatto oggi o una frase carina...'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-file-input',
                'accept': 'image/*'
            }),
            'video': forms.FileInput(attrs={
                'class': 'form-file-input',
                'accept': 'video/mp4,video/quicktime,video/webm,video/*'
            }),
        }

    def clean_image(self):
        img = self.cleaned_data.get('image')
        if img and hasattr(img, 'size'):
            ext = os.path.splitext(img.name)[1].lower()
            if ext not in ALLOWED_IMAGE_EXTENSIONS:
                raise ValidationError(f"Formato immagine non valido ({ext}). Usa JPG, PNG, WEBP o GIF.")
            if img.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
                raise ValidationError(f"L'immagine supera i {MAX_IMAGE_SIZE_MB}MB massimi consentiti.")
        return img

    def clean_video(self):
        vid = self.cleaned_data.get('video')
        if vid and hasattr(vid, 'size'):
            ext = os.path.splitext(vid.name)[1].lower()
            if ext not in ALLOWED_VIDEO_EXTENSIONS:
                raise ValidationError(f"Formato video non valido ({ext}). Usa MP4, MOV o WEBM.")
            if vid.size > MAX_VIDEO_SIZE_MB * 1024 * 1024:
                raise ValidationError(f"Il video supera i {MAX_VIDEO_SIZE_MB}MB massimi consentiti.")
        return vid

    def clean(self):
        cleaned_data = super().clean()
        img = cleaned_data.get('image')
        vid = cleaned_data.get('video')
        caption = cleaned_data.get('caption')
        title = cleaned_data.get('title')
        if not img and not vid and not caption and not title:
            raise ValidationError("Inserisci almeno un'immagine, un video o un testo per il post.")
        return cleaned_data
