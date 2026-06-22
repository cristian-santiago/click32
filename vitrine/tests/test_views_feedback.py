# vitrine/tests/test_views_feedback.py

import json
from unittest.mock import patch
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.utils import timezone
from vitrine.models import Feedback, ActiveSession


@override_settings(
    RATELIMIT_ENABLE=False,
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
)
class FeedbackModelTest(TestCase):
    """Testes para o model Feedback"""

    def setUp(self):
        self.session = ActiveSession.objects.create()
        self.feedback = Feedback.objects.create(
            rating=5,
            category='praise',
            message='Excelente app!',
            session=self.session,
            user_agent='Mozilla/5.0 (Test)'
        )

    def test_feedback_creation(self):
        self.assertEqual(self.feedback.rating, 5)
        self.assertEqual(self.feedback.category, 'praise')
        self.assertEqual(self.feedback.message, 'Excelente app!')
        self.assertEqual(self.feedback.session, self.session)
        self.assertFalse(self.feedback.is_spam)
        self.assertIsNotNone(self.feedback.created_at)

    def test_feedback_str_method(self):
        expected = f"Elogio - 5★ - {self.feedback.created_at.strftime('%d/%m/%Y')}"
        self.assertEqual(str(self.feedback), expected)

    def test_feedback_is_spam_default(self):
        self.assertFalse(self.feedback.is_spam)

    def test_feedback_choices(self):
        for cat, label in Feedback.CATEGORY_CHOICES:
            fb = Feedback.objects.create(
                rating=3,
                category=cat,
                message=f'Teste {cat}',
                session=self.session
            )
            self.assertEqual(fb.get_category_display(), label)
        
        for rating in [1, 2, 3, 4, 5]:
            fb = Feedback.objects.create(
                rating=rating,
                category='praise',
                message=f'Teste rating {rating}',
                session=self.session
            )
            self.assertEqual(fb.rating, rating)


@override_settings(
    RATELIMIT_ENABLE=False,
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
)
class FeedbackAdminTest(TestCase):
    """Testes para views do admin"""

    def setUp(self):
        from django.contrib.auth.models import User
        self.client = Client()
        
        self.superuser = User.objects.create_superuser(
            username='admin',
            password='admin-test-2026',  # ← CORRIGIDO
            email='admin@test.com'
        )
        
        self.user = User.objects.create_user(
            username='user',
            password='user-test-2026',  # ← CORRIGIDO
            email='user@test.com'
        )
        
        self.session = ActiveSession.objects.create()
        self.feedback = Feedback.objects.create(
            rating=5,
            category='praise',
            message='Teste admin',
            session=self.session
        )

    def test_feedback_list_requires_superuser(self):
        response = self.client.get(reverse('click32_admin:feedback_list'))
        self.assertRedirects(response, '/admin/login/?next=/admin/feedback/')
        
        self.client.login(username='user', password='user-test-2026')  # ← CORRIGIDO
        response = self.client.get(reverse('click32_admin:feedback_list'))
        self.assertEqual(response.status_code, 403)
        
        self.client.login(username='admin', password='admin-test-2026')  # ← CORRIGIDO
        response = self.client.get(reverse('click32_admin:feedback_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'click32_admin/feedback_list.html')

    def test_feedback_detail_requires_superuser(self):
        url = reverse('click32_admin:feedback_detail', args=[self.feedback.id])
        
        response = self.client.get(url)
        self.assertRedirects(response, f'/admin/login/?next={url}')
        
        self.client.login(username='user', password='user-test-2026')  # ← CORRIGIDO
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        
        self.client.login(username='admin', password='admin-test-2026')  # ← CORRIGIDO
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'click32_admin/feedback_detail.html')
        self.assertEqual(response.context['feedback'].id, self.feedback.id)

    def test_feedback_detail_not_found(self):
        self.client.login(username='admin', password='admin-test-2026')  # ← CORRIGIDO
        response = self.client.get(reverse('click32_admin:feedback_detail', args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_feedback_list_context(self):
        self.client.login(username='admin', password='admin-test-2026')  # ← CORRIGIDO
        response = self.client.get(reverse('click32_admin:feedback_list'))
        
        self.assertIn('feedbacks', response.context)
        self.assertIn('total', response.context)
        self.assertIn('avg_rating', response.context)
        self.assertIn('categories', response.context)
        
        self.assertEqual(response.context['total'], 1)
        self.assertEqual(response.context['avg_rating'], 5.0)


@override_settings(
    RATELIMIT_ENABLE=False,
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
)
class FeedbackExtraTest(TestCase):
    """Testes extras para feedback"""

    def setUp(self):
        self.client = Client()
        self.url = reverse('submit_feedback')
        self.session1 = ActiveSession.objects.create()
        self.session2 = ActiveSession.objects.create()

    def test_submit_feedback_without_session_creates_session(self):
        data = {
            'rating': 5,
            'category': 'praise',
            'message': 'Teste sem session'
        }
        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        feedback = Feedback.objects.first()
        self.assertIsNotNone(feedback.session)
        self.assertIsNotNone(feedback.session.session_id)

    def test_anti_spam_different_sessions(self):
        data = {
            'rating': 5,
            'category': 'praise',
            'message': 'Primeiro feedback'
        }
        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_X_SESSION_ID=str(self.session1.session_id)
        )
        self.assertEqual(response.status_code, 201)
        
        data = {
            'rating': 5,
            'category': 'praise',
            'message': 'Segundo feedback (outra sessão)'
        }
        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_X_SESSION_ID=str(self.session2.session_id)
        )
        self.assertEqual(response.status_code, 201)

    def test_submit_feedback_all_categories(self):
        """Testa envio com todas as categorias"""
        categories = ['suggestion', 'praise', 'problem', 'other']
        
        for category in categories:
            session = ActiveSession.objects.create()
            
            data = {
                'rating': 4,
                'category': category,
                'message': f'Teste categoria {category}'
            }
            response = self.client.post(
                self.url,
                data=json.dumps(data),
                content_type='application/json',
                HTTP_X_SESSION_ID=str(session.session_id)
            )
            self.assertEqual(response.status_code, 201)
            
            feedback = Feedback.objects.filter(category=category).first()
            self.assertIsNotNone(feedback)
            self.assertEqual(feedback.category, category)

    def test_submit_feedback_all_ratings(self):
        """Testa envio com todos os ratings"""
        for rating in [1, 2, 3, 4, 5]:
            session = ActiveSession.objects.create()
            
            data = {
                'rating': rating,
                'category': 'praise',
                'message': f'Teste rating {rating}'
            }
            response = self.client.post(
                self.url,
                data=json.dumps(data),
                content_type='application/json',
                HTTP_X_SESSION_ID=str(session.session_id)
            )
            self.assertEqual(response.status_code, 201)
            
            feedback = Feedback.objects.filter(rating=rating).first()
            self.assertIsNotNone(feedback)
            self.assertEqual(feedback.rating, rating)

    def test_submit_feedback_invalid_rating(self):
        data = {
            'rating': 0,
            'category': 'praise',
            'message': 'Teste rating inválido'
        }
        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_X_SESSION_ID=str(self.session1.session_id)
        )
        self.assertEqual(response.status_code, 400)
        
        data['rating'] = 6
        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_X_SESSION_ID=str(self.session1.session_id)
        )
        self.assertEqual(response.status_code, 400)