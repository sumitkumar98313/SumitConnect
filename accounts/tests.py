from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Profile, Post, Like, Comment, Follow


class ProfileModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='sumit', password='test1234')

    def test_profile_auto_created(self):
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_profile_str(self):
        self.assertEqual(str(self.user.profile), 'sumit')

    def test_profile_bio_blank_by_default(self):
        self.assertEqual(self.user.profile.bio, '')

    def test_profile_picture_null_by_default(self):
        self.assertIsNone(self.user.profile.profile_picture.name or None)

    def test_followers_count_zero(self):
        self.assertEqual(self.user.profile.followers_count, 0)

    def test_following_count_zero(self):
        self.assertEqual(self.user.profile.following_count, 0)


class PostModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='sumit', password='test1234')
        self.post = Post.objects.create(author=self.user, content='Hello SumitConnect!')

    def test_post_str(self):
        self.assertIn('sumit', str(self.post))

    def test_likes_count_zero(self):
        self.assertEqual(self.post.likes_count, 0)

    def test_comments_count_zero(self):
        self.assertEqual(self.post.comments_count, 0)

    def test_not_liked_by_default(self):
        self.assertFalse(self.post.is_liked_by(self.user))

    def test_ordering_newest_first(self):
        post2 = Post.objects.create(author=self.user, content='Second post')
        posts = Post.objects.all()
        self.assertEqual(posts[0], post2)
        self.assertEqual(posts[1], self.post)


class LikeModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='sumit', password='test1234')
        self.post = Post.objects.create(author=self.user, content='Test post')

    def test_like_post(self):
        Like.objects.create(user=self.user, post=self.post)
        self.assertEqual(self.post.likes_count, 1)
        self.assertTrue(self.post.is_liked_by(self.user))

    def test_like_str(self):
        like = Like.objects.create(user=self.user, post=self.post)
        self.assertIn('sumit', str(like))

    def test_no_duplicate_likes(self):
        from django.db import IntegrityError
        Like.objects.create(user=self.user, post=self.post)
        with self.assertRaises(IntegrityError):
            Like.objects.create(user=self.user, post=self.post)


class CommentModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='sumit', password='test1234')
        self.post = Post.objects.create(author=self.user, content='Test post')

    def test_add_comment(self):
        Comment.objects.create(user=self.user, post=self.post, content='Nice post!')
        self.assertEqual(self.post.comments_count, 1)

    def test_comment_str(self):
        comment = Comment.objects.create(user=self.user, post=self.post, content='Great!')
        self.assertIn('sumit', str(comment))
        self.assertIn(str(self.post.id), str(comment))

    def test_ordering_oldest_first(self):
        c1 = Comment.objects.create(user=self.user, post=self.post, content='First')
        c2 = Comment.objects.create(user=self.user, post=self.post, content='Second')
        comments = Comment.objects.all()
        self.assertEqual(comments[0], c1)
        self.assertEqual(comments[1], c2)


class FollowModelTest(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='sumit', password='test1234')
        self.user2 = User.objects.create_user(username='shubham', password='test1234')

    def test_follow(self):
        Follow.objects.create(follower=self.user1, following=self.user2)
        self.assertEqual(self.user2.profile.followers_count, 1)
        self.assertEqual(self.user1.profile.following_count, 1)

    def test_follow_str(self):
        follow = Follow.objects.create(follower=self.user1, following=self.user2)
        self.assertEqual(str(follow), 'sumit follows shubham')

    def test_no_duplicate_follow(self):
        from django.db import IntegrityError
        Follow.objects.create(follower=self.user1, following=self.user2)
        with self.assertRaises(IntegrityError):
            Follow.objects.create(follower=self.user1, following=self.user2)

    def test_unfollow(self):
        Follow.objects.create(follower=self.user1, following=self.user2)
        Follow.objects.filter(follower=self.user1, following=self.user2).delete()
        self.assertEqual(self.user2.profile.followers_count, 0)


class ViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='sumit', password='test1234')
        self.post = Post.objects.create(author=self.user, content='Test post')

    def test_signup_page(self):
        self.assertEqual(self.client.get(reverse('signup')).status_code, 200)

    def test_login_page(self):
        self.assertEqual(self.client.get(reverse('login')).status_code, 200)

    def test_signup_creates_user(self):
        self.client.post(reverse('signup'), {
            'username': 'newuser',
            'password': 'pass1234',
            'confirm_password': 'pass1234'
        })
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_works(self):
        response = self.client.post(reverse('login'), {
            'username': 'sumit',
            'password': 'test1234'
        })
        self.assertIn(response.status_code, [200, 302])

    def test_login_wrong_password(self):
        response = self.client.post(reverse('login'), {
            'username': 'sumit',
            'password': 'wrongpass'
        })
        self.assertNotEqual(response.status_code, 302)

    def test_feed_redirects_logged_out(self):
        response = self.client.get(reverse('feed'))
        self.assertRedirects(response, f"/accounts/login/?next={reverse('feed')}")

    def test_dashboard_redirects_logged_out(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f"/accounts/login/?next={reverse('dashboard')}")

    def test_profile_redirects_logged_out(self):
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, f"/accounts/login/?next={reverse('profile')}")

    def test_feed_loads(self):
        self.client.login(username='sumit', password='test1234')
        self.assertEqual(self.client.get(reverse('feed')).status_code, 200)

    def test_dashboard_loads(self):
        self.client.login(username='sumit', password='test1234')
        self.assertEqual(self.client.get(reverse('dashboard')).status_code, 200)

    def test_profile_loads(self):
        self.client.login(username='sumit', password='test1234')
        self.assertEqual(self.client.get(reverse('profile')).status_code, 200)

    def test_post_detail_loads(self):
        self.client.login(username='sumit', password='test1234')
        self.assertEqual(self.client.get(reverse('post_detail', args=[self.post.id])).status_code, 200)

    def test_user_profile_loads(self):
        self.client.login(username='sumit', password='test1234')
        self.assertEqual(self.client.get(reverse('user_profile', args=['sumit'])).status_code, 200)

    def test_create_post(self):
        self.client.login(username='sumit', password='test1234')
        self.client.post(reverse('create_post'), {'content': 'A brand new post!'})
        self.assertTrue(Post.objects.filter(content='A brand new post!').exists())

    def test_like_post(self):
        self.client.login(username='sumit', password='test1234')
        self.client.post(reverse('like_post', args=[self.post.id]))
        self.assertTrue(Like.objects.filter(user=self.user, post=self.post).exists())

    def test_add_comment(self):
        self.client.login(username='sumit', password='test1234')
        self.client.post(reverse('post_detail', args=[self.post.id]), {'content': 'Great post!'})
        self.assertTrue(Comment.objects.filter(content='Great post!').exists())

    def test_delete_post(self):
        self.client.login(username='sumit', password='test1234')
        self.client.post(reverse('delete_post', args=[self.post.id]))
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

    def test_follow_user(self):
        other = User.objects.create_user(username='shubham', password='test1234')
        self.client.login(username='sumit', password='test1234')
        self.client.post(reverse('follow_user', args=['shubham']))
        self.assertTrue(Follow.objects.filter(follower=self.user, following=other).exists())