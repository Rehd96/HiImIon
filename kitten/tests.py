from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from .models import KittenProfile, KittenPost


class KittenAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.profile = KittenProfile.objects.create(
            name='Mais',
            slug='mais',
            gender='Femmina',
            age_text='7 settimane circa',
            color='Completamente nera',
            location='Pescara (zona Aeroporto)',
            phone_number='340 1234567',
        )
        self.staff_user = User.objects.create_user(
            username='staff',
            password='staffpassword123',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='regular',
            password='regularpassword123',
            is_staff=False
        )

    def test_kitten_detail_page(self):
        response = self.client.get(reverse('kitten_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mais')
        self.assertContains(response, '7 settimane')
        self.assertContains(response, 'Pescara')
        self.assertContains(response, '340 1234567')

    def test_redirects(self):
        r1 = self.client.get(reverse('kitten_adotta'))
        self.assertRedirects(r1, reverse('kitten_detail'), fetch_redirect_response=False)

        r2 = self.client.get(reverse('kitten_gattino'))
        self.assertRedirects(r2, reverse('kitten_detail'), fetch_redirect_response=False)

    def test_qr_code_generation(self):
        response = self.client.get(reverse('kitten_qr'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertTrue(len(response.content) > 100)

    def test_flyers(self):
        r_a4 = self.client.get(reverse('kitten_flyer_a4'))
        self.assertEqual(r_a4.status_code, 200)
        self.assertContains(r_a4, 'MAIS')
        self.assertContains(r_a4, 'CERCASI FAMIGLIA PER SEMPRE')

        r_a5 = self.client.get(reverse('kitten_flyer_a5'))
        self.assertEqual(r_a5.status_code, 200)
        self.assertContains(r_a5, 'Mais')

    def test_kitten_like_ajax(self):
        initial_likes = self.profile.likes_count
        response = self.client.post(reverse('kitten_like'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['likes'], initial_likes + 1)

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.likes_count, initial_likes + 1)

    def test_kitten_admin_permissions(self):
        # Anonymous user must be redirected to login
        res_anon = self.client.get(reverse('kitten_admin'))
        self.assertEqual(res_anon.status_code, 302)

        # Regular non-staff user must be redirected
        self.client.login(username='regular', password='regularpassword123')
        res_reg = self.client.get(reverse('kitten_admin'))
        self.assertEqual(res_reg.status_code, 302)

        # Staff user can access
        self.client.login(username='staff', password='staffpassword123')
        res_staff = self.client.get(reverse('kitten_admin'))
        self.assertEqual(res_staff.status_code, 200)
        self.assertContains(res_staff, 'Gestione & Editor Contenuti: Mais')

    def test_admin_update_all_descriptions(self):
        self.client.login(username='staff', password='staffpassword123')
        response = self.client.post(reverse('kitten_admin'), {
            'action': 'update_profile',
            'name': 'Mais',
            'hero_title': 'Ecco a voi la fantastica Mais! 🐱',
            'phone_number': '333 9876543',
            'whatsapp_number': '',
            'contact_email': 'test@example.com',
            'location': 'Pescara Aeroporto',
            'tagline': 'Femmina · 7 settimane · Dolcezza pura',
            'age_text': '7 settimane',
            'bio_intro': 'Questa è la nuova bio personalizzata di Mais!',
            'story_title': 'Come è arrivata da noi?',
            'story_quote': 'Una citazione speciale per Mais.',
            'personality_title': 'Il suo carattere unico',
            'personality': 'Vivace, intelligente e affettuosa.',
            'bullet_1': 'Ama arrampicarsi sui tiragraffi',
            'bullet_2': 'Fa la pasta sulle coperte',
            'bullet_3': 'Usa sempre la lettiera',
            'bullet_4': 'Super fusa ogni volta che la tocchi',
            'health_title': 'Visite e Vaccinazioni',
            'health_subtitle': 'Tutti i dettagli sanitari',
            'health_step1_title': 'Checkup generale',
            'health_step1_badge': 'OK ✓',
            'health_step1_desc': 'Visita perfetta',
            'health_step1_done': 'on',
            'health_step2_title': 'Sverminazione 1',
            'health_step2_badge': 'Eseguita',
            'health_step2_desc': 'Tutto a posto',
            'health_step2_done': 'on',
            'health_step3_title': 'Vaccinazione trivalente',
            'health_step3_badge': 'In programma',
            'health_step3_desc': 'A breve',
            'health_step4_title': 'Sterilizzazione futura',
            'health_step4_badge': 'A 6 mesi',
            'health_step4_desc': 'Obbligatoria',
            'feed_title': 'Il Diario Fotografico',
            'feed_subtitle': 'Aggiornamenti dal vivo',
            'adoption_title': 'Come Adottare Mais',
            'adoption_intro': 'Istruzioni e requisiti per la famiglia:',
            'adoption_requirements': 'Solo amanti dei gatti con casa sicura',
            'adoption_cta_title': 'Contattaci per una visita',
            'adoption_cta_desc': 'Ti aspettiamo a braccia aperte!',
            'flyer_title': 'ADOTTA QUESTA MERAVIGLIA!',
            'flyer_header_badge': 'APPELLO DEL CUORE',
        })
        self.assertRedirects(response, reverse('kitten_admin'))
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.phone_number, '333 9876543')
        self.assertEqual(self.profile.hero_title, 'Ecco a voi la fantastica Mais! 🐱')
        self.assertEqual(self.profile.story_title, 'Come è arrivata da noi?')
        self.assertEqual(self.profile.bullet_1, 'Ama arrampicarsi sui tiragraffi')

        # Check public page reflects new descriptions
        res_detail = self.client.get(reverse('kitten_detail'))
        self.assertContains(res_detail, 'Ecco a voi la fantastica Mais! 🐱')
        self.assertContains(res_detail, 'Questa è la nuova bio personalizzata di Mais!')
        self.assertContains(res_detail, 'Ama arrampicarsi sui tiragraffi')
        self.assertContains(res_detail, 'Come è arrivata da noi?')

        # Check flyer reflects new custom title
        res_flyer = self.client.get(reverse('kitten_flyer_a4'))
        self.assertContains(res_flyer, 'ADOTTA QUESTA MERAVIGLIA!')
        self.assertContains(res_flyer, 'APPELLO DEL CUORE')

    def test_mobile_sticky_bar_present(self):
        res = self.client.get(reverse('kitten_detail'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'k-mobile-sticky-bar')
        self.assertContains(res, 'btnPurrMobile')
        self.assertContains(res, 'purrCounterMobile')

    def test_non_staff_redirects_to_mais(self):
        # Create non-staff user
        non_staff = User.objects.create_user(username='regularuser', password='password123')
        self.client.login(username='regularuser', password='password123')
        response = self.client.get(reverse('kitten_admin'))
        self.assertRedirects(response, reverse('kitten_detail'))

    def test_panel_logout_redirects_to_mais_when_specified(self):
        self.client.login(username='staffuser', password='password123')
        response = self.client.post(reverse('panel_logout'), {'next': reverse('kitten_detail')})
        self.assertRedirects(response, reverse('kitten_detail'))
