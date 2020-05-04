from django.test import TestCase, Client

from .models import User, Post


class Home_work_test(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_user = User.objects.create_user(username='Vasya', email='Vasya@pivko.ru', password='12345678')
        self.client.login(username='Vasya', password='12345678')


    def test_profile(self): 
        response = self.client.get('/Vasya/')
        self.assertEqual(response.status_code, 200)


    def test_user_create_post(self):
        response = self.client.get('/new')
        self.assertEqual(response.status_code, 200)
        post = Post.objects.create(author=self.test_user, text='какой-то текст')
        counter = Post.objects.count()
        self.assertEqual(counter, 1)
     
        
    def test_anonim_user(self):
        self.client.logout()
        response = self.client.get('/new')
        self.assertRedirects(response, '/auth/login/?next=/new', status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)


    def test_pages_with_post(self):
        self.client.login(username='Vasya', password='12345678')
        text = 'еще какой то текст'
        post = Post.objects.create(author=self.test_user, text=text)
        response = self.client.get('')
        self.assertContains(response, post)
        response = self.client.get('/Vasya/1/')
        self.assertContains(response, post)

    
    def test_edit_post(self):
        text = 'хочу на море'
        post = Post.objects.create(author=self.test_user, text=text)
        new_text = 'все еще хочу на море'
        response = self.client.post('/Vasya/1/edit', {'text': new_text})
        self.assertRedirects(response, '/Vasya/1/', status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
        response = self.client.get('')
        self.assertContains(response, new_text)
        response = self.client.get('/Vasya/')
        self.assertContains(response, new_text)
        response = self.client.get('/Vasya/1/')
        self.assertContains(response, new_text)