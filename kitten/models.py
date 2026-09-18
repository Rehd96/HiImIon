import re
import urllib.parse
from django.db import models
from django.utils import timezone


class KittenProfile(models.Model):
    # Core Identity
    name = models.CharField(max_length=100, default='Mais')
    slug = models.SlugField(max_length=100, default='mais', unique=True)
    tagline = models.CharField(
        max_length=200,
        default='Femmina · 7 settimane · Piccola panterina nera',
        blank=True
    )
    age_text = models.CharField(max_length=50, default='7 settimane circa', blank=True)
    gender = models.CharField(
        max_length=20,
        choices=[('Femmina', 'Femmina ♀'), ('Maschio', 'Maschio ♂')],
        default='Femmina'
    )
    color = models.CharField(max_length=100, default='Completamente nera', blank=True)
    location = models.CharField(max_length=150, default='Pescara (zona Aeroporto) e dintorni', blank=True)

    # Hero & Badges
    hero_badge = models.CharField(
        max_length=150,
        default='🐾 In cerca di una famiglia d\'amore',
        blank=True
    )
    hero_location_badge = models.CharField(
        max_length=150,
        default='Zona Aeroporto · Pescara',
        blank=True
    )
    hero_title = models.CharField(
        max_length=200,
        default='Ciao, mi chiamo Mais! 🐾',
        blank=True
    )

    # Quick Specs on Hero
    spec_gender = models.CharField(max_length=50, default='Femmina', blank=True)
    spec_age = models.CharField(max_length=50, default='7 settimane circa', blank=True)
    spec_color = models.CharField(max_length=100, default='Nero splendente', blank=True)
    spec_location = models.CharField(max_length=150, default='Pescara (Aeroporto)', blank=True)

    # Contact fields (editable by user)
    phone_number = models.CharField(
        max_length=50,
        blank=True,
        help_text='Numero di telefono per chiamate e WhatsApp (es. 340 1234567)'
    )
    whatsapp_number = models.CharField(
        max_length=50,
        blank=True,
        help_text='Opzionale: lascialo vuoto se è uguale al numero sopra'
    )
    contact_email = models.EmailField(blank=True)
    contact_notes = models.CharField(
        max_length=250,
        default='Contattami via WhatsApp o chiamata per conoscerla di persona!',
        blank=True
    )
    whatsapp_message = models.CharField(
        max_length=250,
        default='Ciao! Ho visto Mais su labustagialla.it e vorrei avere informazioni per conoscerla e adottarla! 🐾',
        blank=True
    )

    # Story & Bio
    story_title = models.CharField(max_length=150, default='Perché mi chiamo Mais?', blank=True)
    story_icon = models.CharField(max_length=20, default='🌽', blank=True)
    bio_intro = models.TextField(
        default=(
            "Mi chiamo Mais! Da dove viene il mio nome? Da mice(tto) ➔ mice (topolino in inglese) "
            "➔ pronunciato all'italiana: MAIS! 🌽\n"
            "Sono una gattina completamente nera di circa 7 settimane, una vera panterina in miniatura. "
            "Sono curiosa del mondo, dolcissima e con una gran voglia di trovare la mia famiglia per sempre."
        ),
        blank=True
    )
    story_quote = models.TextField(
        default='«Non lasciatevi ingannare dal mantello scuro: non porto sfortuna, porto solo una quantità infinita di amore, risate e fusa calde!»',
        blank=True
    )

    # Personality & Bullets
    personality_title = models.CharField(max_length=150, default='Carattere e Superpoteri', blank=True)
    personality_icon = models.CharField(max_length=20, default='⚡', blank=True)
    personality = models.TextField(
        default=(
            "Sono un vulcano di allegria e affetto: adoro inseguire palline, fare agguati giocosi "
            "e appena mi prendi in braccio accendo il motore delle fusa a tutto volume! "
            "Amo stare con le persone e condividere ogni momento."
        ),
        blank=True
    )
    bullet_1 = models.CharField(
        max_length=250,
        default='Super Giocherellona: adora rincorrere palline, cordini e fare piccoli agguati comici',
        blank=True
    )
    bullet_2 = models.CharField(
        max_length=250,
        default='Buongustaia: mangia con grande gioia la sua pappa umida 🐟',
        blank=True
    )
    bullet_3 = models.CharField(
        max_length=250,
        default='Educatissima: usa già la lettiera in modo impeccabile 🚽',
        blank=True
    )
    bullet_4 = models.CharField(
        max_length=250,
        default='Regina delle Fusa: basta una carezza sotto il mento per sentirla vibrare!',
        blank=True
    )

    # Health Section & Steps
    health_title = models.CharField(max_length=150, default='Stato di Salute & Visite', blank=True)
    health_subtitle = models.CharField(
        max_length=250,
        default='Trasparenza totale per chi deciderà di accoglierla',
        blank=True
    )
    health_info = models.TextField(
        default=(
            "• Prima visita veterinaria eseguita con successo 🩺\n"
            "• Prima sverminazione effettuata\n"
            "• Da completare: piano vaccinale, sverminazione totale e futura sterilizzazione (requisito per l'adozione)\n"
            "• Mangia con appetito la pappa umida 🐟\n"
            "• È bravissima ed educata: usa regolarmente la lettiera! 🚽"
        ),
        blank=True
    )

    health_step1_badge = models.CharField(max_length=50, default='Fatto ✓', blank=True)
    health_step1_title = models.CharField(max_length=150, default='Prima Visita Veterinaria', blank=True)
    health_step1_desc = models.TextField(
        default='Visita generale superata a pieni voti: vispa, reattiva e in ottima salute generale.',
        blank=True
    )
    health_step1_done = models.BooleanField(default=True)

    health_step2_badge = models.CharField(max_length=50, default='Fatto ✓', blank=True)
    health_step2_title = models.CharField(max_length=150, default='Prima Sverminazione', blank=True)
    health_step2_desc = models.TextField(
        default='Trattamento parassitario iniziale effettuato regolarmente.',
        blank=True
    )
    health_step2_done = models.BooleanField(default=True)

    health_step3_badge = models.CharField(max_length=50, default='Da completare', blank=True)
    health_step3_title = models.CharField(max_length=150, default='Vaccini & Sverminazione Completa', blank=True)
    health_step3_desc = models.TextField(
        default='Da effettuare a breve dal veterinario di fiducia della nuova famiglia.',
        blank=True
    )
    health_step3_done = models.BooleanField(default=False)

    health_step4_badge = models.CharField(max_length=50, default='Futuro (obbligo)', blank=True)
    health_step4_title = models.CharField(max_length=150, default='Sterilizzazione', blank=True)
    health_step4_desc = models.TextField(
        default="Da effettuare al raggiungimento dell'età idonea (circa 6 mesi) per il suo benessere.",
        blank=True
    )
    health_step4_done = models.BooleanField(default=False)

    # Feed Section Texts
    feed_title = models.CharField(max_length=150, default='Il Diario di Mais 📸', blank=True)
    feed_subtitle = models.CharField(
        max_length=250,
        default='Scatti spontanei, video buffi e momenti quotidiani',
        blank=True
    )
    feed_empty_title = models.CharField(max_length=150, default='Il diario fotografico è in arrivo!', blank=True)
    feed_empty_desc = models.TextField(
        default='Mais sta facendo un sonnellino dopo aver mangiato la pappa umida. I primi video e le foto delle sue avventure verranno caricati a breve!',
        blank=True
    )

    # Adoption Section Texts
    adoption_badge = models.CharField(max_length=100, default='🏡 Amore Consapevole', blank=True)
    adoption_title = models.CharField(max_length=150, default='Requisiti per l\'adozione', blank=True)
    adoption_intro = models.TextField(
        default='Mais è un esserino vivace che merita una vita serena e protetta. Cerchiamo persone speciali che la amino come una di famiglia:',
        blank=True
    )
    adoption_requirements = models.TextField(
        default=(
            "Cerchiamo per Mais un'adozione d'amore e consapevole:\n"
            "• Casa sicura (protezione a finestre e balconi)\n"
            "• Impegno a completare vaccini e sterilizzazione in età opportuna\n"
            "• Disponibilità a breve colloquio conoscitivo pre-affido (Pescara e province limitrofe)\n"
            "• Mais è una compagna per la vita, non un giocattolo!"
        ),
        blank=True
    )
    adoption_cta_title = models.CharField(
        max_length=150,
        default='Vuoi venire a conoscere Mais di persona?',
        blank=True
    )
    adoption_cta_desc = models.TextField(
        default='Siamo a Pescara (zona Aeroporto). Scrivici su WhatsApp o chiamaci per fare due chiacchiere senza impegno e organizzare un incontro!',
        blank=True
    )

    # Flyer Specific Texts
    flyer_header_badge = models.CharField(max_length=100, default='❤️ ADOZIONE DEL CUORE ❤️', blank=True)
    flyer_title = models.CharField(max_length=150, default='CERCASI FAMIGLIA PER SEMPRE! 🐾', blank=True)
    flyer_subtitle = models.CharField(
        max_length=200,
        default='Piccola panterina nera in cerca di una casa felice',
        blank=True
    )
    flyer_cta_text = models.CharField(max_length=200, default='📲 Inquadra il QR con il telefono!', blank=True)
    flyer_cta_sub = models.CharField(
        max_length=250,
        default='Guarda i video mentre gioca, tutte le foto e la sua storia completa su:',
        blank=True
    )
    flyer_contact_label = models.CharField(max_length=150, default='Per informazioni e per conoscerla:', blank=True)

    # General Media & Status
    cover_image = models.ImageField(upload_to='kitten/covers/', blank=True, null=True)
    is_adopted = models.BooleanField(default=False, verbose_name='Gattina adottata! 🎉')
    adopted_banner_text = models.CharField(
        max_length=250,
        default='🎉 MERAVIGLIOSA NOTIZIA! Mais ha trovato la sua famiglia per sempre! Grazie a tutti per l\'affetto! ❤️',
        blank=True
    )
    likes_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Profilo Gattino'
        verbose_name_plural = 'Profili Gattini'

    def __str__(self):
        return f'{self.name} ({self.age_text})'

    @property
    def clean_whatsapp_number(self):
        num = self.whatsapp_number.strip() or self.phone_number.strip()
        if not num:
            return ''
        digits = re.sub(r'[^\d+]', '', num)
        if digits.startswith('+'):
            return digits[1:]
        if digits.startswith('00'):
            return digits[2:]
        if len(digits) == 10 and digits.startswith('3'):
            return f'39{digits}'
        return digits

    @property
    def whatsapp_url(self):
        clean_num = self.clean_whatsapp_number
        if not clean_num:
            return ''
        text = self.whatsapp_message or (
            f"Ciao! Ho visto {self.name} su labustagialla.it e vorrei avere "
            f"informazioni per conoscerla e adottarla! 🐾"
        )
        return f"https://wa.me/{clean_num}?text={urllib.parse.quote(text)}"

    @property
    def cover_url(self):
        if self.cover_image:
            return self.cover_image.url
        return '/static/img/mais_placeholder.jpg'


class KittenPost(models.Model):
    TAG_CHOICES = [
        ('gioco', 'Attacco Giocherellone 🎾'),
        ('pappa', 'Momento Pappa 🐟'),
        ('coccole', 'Fusa e Coccole 💖'),
        ('nanna', 'Pisolo Strategico 💤'),
        ('scoperte', 'Piccole Scoperte 🐾'),
        ('visita', 'Visita Veterinaria 🩺'),
        ('altro', 'Momento Dolce ✨'),
    ]

    MEDIA_TYPE_CHOICES = [
        ('photo', 'Foto'),
        ('video', 'Video'),
        ('text', 'Solo Testo'),
    ]

    kitten = models.ForeignKey(
        KittenProfile,
        related_name='posts',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=150, blank=True)
    caption = models.TextField(blank=True)
    tag = models.CharField(max_length=30, choices=TAG_CHOICES, default='gioco')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='photo')

    image = models.ImageField(upload_to='kitten/posts/images/', blank=True, null=True)
    video = models.FileField(upload_to='kitten/posts/videos/', blank=True, null=True)
    video_poster = models.ImageField(upload_to='kitten/posts/posters/', blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    is_featured = models.BooleanField(default=False)
    likes = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Post del Feed'
        verbose_name_plural = 'Post del Feed'
        ordering = ['-created_at']

    def __str__(self):
        label = self.title or self.get_tag_display() or f'Post #{self.pk}'
        return f'{self.created_at:%d/%m/%Y} - {label}'

    def save(self, *args, **kwargs):
        if self.video and not self.image:
            self.media_type = 'video'
        elif self.image and not self.video:
            self.media_type = 'photo'
        elif not self.image and not self.video:
            self.media_type = 'text'
        super().save(*args, **kwargs)
