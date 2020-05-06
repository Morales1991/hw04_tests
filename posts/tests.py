from django.test import TestCase, Client

from .models import User, Post


class HomeWorkTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_user = User.objects.create_user(username='Vasya', email='Vasya@pivko.ru', password='12345678')
        self.client.login(username='Vasya', password='12345678')

    def testProfile(self): 
        response = self.client.get(f'/{self.test_user.username}/')
        self.assertEqual(response.status_code, 200)

    def testUserCreatePost(self):
        response = self.client.post('/new', {'text': 'test'})
        self.assertTrue(Post.objects.filter(text='test', author=self.test_user).exists())

    def testAnonimUser(self):
        self.client.logout()
        response = self.client.get('/new')
        self.assertRedirects(response, '/auth/login/?next=/new', status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)

    def testPagesWithPost(self):
        self.client.login(username='Vasya', password='12345678')
        post = Post.objects.create(author=self.test_user, text='еще какой то текст')
        response = self.client.get('')
        self.assertContains(response, post)
        response = self.client.get(f'/{self.test_user.username}/{post.id}/')
        self.assertContains(response, post)

    def testEditPost(self):
        new_text = 'все еще хочу на море' 
        post = Post.objects.create(author=self.test_user, text='хочу на море')

        response = self.client.post(f'/{self.test_user.username}/{post.id}/edit/', {'text': new_text})
        self.assertRedirects(response, f'/{self.test_user.username}/{post.id}/', status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
        
        response = self.client.get('')
        self.assertContains(response, new_text)
        
        response = self.client.get(f'/{self.test_user.username}/')
        self.assertContains(response, new_text)
       
        response = self.client.get(f'/{self.test_user.username}/{post.id}/')
        self.assertContains(response, new_text)

    def test404(self):
        response = self.client.get('default_page')
        self.assertEqual(response.status_code, 404)