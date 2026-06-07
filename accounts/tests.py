from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Profile, Post, Like, Comment, Follow


# =============================================
# Profile Model Tests
# =============================================

class ProfileModelTest(TestCase):

    def setUp(self):
        # create a test user before each test
        self.user = User.objects.create_user(username='sumit', password='test1234')

    def test_profile_auto_created(self):
        # profile should be created automatically via signals when user is created
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_profile_str(self):
        # __str__ should return the username
        self.assertEqual(str(self.user.profile), 'sumit')

    def test_profile_bio_blank_by_default(self):
        # bio should be empty string by default
        self.assertEqual(self.user.profile.bio, '')

    def test_profile_picture_null_by_default(self):
        # no profile picture by default
        self.assertIsNone(self.user.profile.profile_picture.name or None)

    def test_followers_count_zero(self):
        # new user should have 0 followers
        self.assertEqual(self.user.profile.followers_count, 0)

    def test_following_count_zero(self):
        # new user should be following 0 people
        self.assertEqual(self.user.profile.following_count, 0)


# =============================================
# Post Model Tests
# =============================================

class PostModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='sumit', password='test1234')
        self.post = Post.objects.create(author=self.user, content='Hello SumitConnect!')

    def test_post_str(self):
        # str should contain the author username
        self.assertIn('sumit', str(self.post))

    def test_likes_count_zero(self):
        # new post should have 0 likes
        self.assertEqual(self.post.likes_count, 0)

    def test_comments_count_zero(self):
        # new post should have 0 comments
        self.assertEqual(self.post.comments_count, 0)

    def test_not_liked_by_default(self):
        # post should not be liked by anyone by default
        self.assertFalse(self.post.is_liked_by(self.user))

    def test_ordering_newest_first(self):
        # posts should be ordered newest first
        post2 = Post.objects.create(author=self.user, content='Second post')
        posts = Post.objects.all()
        self.assertEqual(posts[0], post2)
        self.assertEqual(posts[1], self.post)


# =============================================
# Like Model Tests
# =============================================

class LikeModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='sumit', password='test1234')
        self.post = Post.objects.create(author=self.user, content='Test post')

    def test_like_post(self):
        # liking a post should increase likes count
        Like.objects.create(user=self.user, post=self.post)
        self.assertEqual(self.post.likes_count, 1)
        self.assertTrue(self.post.is_liked_by(self.user))

    def test_like_str(self):
        like = Like.objects.create(user=self.user, post=self.post)
        # str should contain the username
        self.assertIn('sumit', str(like))

    def test_no_duplicate_likes(self):
        # same user can't like same post twice - should raise IntegrityError
        from django.db import IntegrityError
        Like.objects.create(user=self.user, post=self.post)
        with self.assertRaises(IntegrityError):
            Like.objects.create(user=self.user, post=self.post)


# =============================================
# Comment Model Tests
# =============================================

class CommentModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='sumit', password='test1234')
        self.post = Post.objects.create(author=self.user, content='Test post')

    def test_add_comment(self):
        # adding a comment should increase comments count
        Comment.objects.create(user=self.user, post=self.post, content='Nice post!')
        self.assertEqual(self.post.comments_count, 1)

    def test_comment_str(self):
        comment = Comment.objects.create(user=self.user, post=self.post, content='Great!')
        # str should contain username and post id
        self.assertIn('sumit', str(comment))
        self.assertIn(str(self.post.id), str(comment))

    def test_ordering_oldest_first(self):
        # comments should be ordered oldest first (like real comment sections)
        c1 = Comment.objects.create(user=self.user, post=self.post, content='First')
        c2 = Comment.objects.create(user=self.user, post=self.post, content='Second')
        comments = Comment.objects.all()
        self.assertEqual(comments[0], c1)
        self.assertEqual(comments[1], c2)


# =============================================
# Follow Model Tests
# =============================================

class FollowModelTest(TestCase):

    def setUp(self):
        # create two users for follow tests
        self.user1 = User.objects.create_user(username='sumit', password='test1234')
        self.user2 = User.objects.create_user(username='rahul', password='test1234')

    def test_follow(self):
        # following should update both users counts
        Follow.objects.create(follower=self.user1, following=self.user2)
        self.assertEqual(self.user2.profile.followers_count, 1)
        self.assertEqual(self.user1.profile.following_count, 1)

    def test_follow_str(self):
        follow = Follow.objects.create(follower=self.user1, following=self.user2)
        self.assertEqual(str(follow), 'sumit follows rahul')

    def test_no_duplicate_follow(self):
        # can't follow same person twice
        from django.db import IntegrityError
        Follow.objects.create(follower=self.user1, following=self.user2)
        with self.assertRaises(IntegrityError):
            Follow.objects.create(follower=self.user1, following=self.user2)

    def test_unfollow(self):
        # deleting the follow object should reduce followers count back to 0
        Follow.objects.create(follower=self.user1, following=self.user2)
        Follow.objects.filter(follower=self.user1, following=self.user2).delete()
        self.assertEqual(self.user2.profile.followers_count, 0)


# =============================================
# View Tests
# =============================================

class ViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='sumit', password='test1234')
        self.post = Post.objects.create(author=self.user, content='Test post')

    # --- page load tests ---

    def test_signup_page(self):
        # signup page should load for everyone
        self.assertEqual(self.client.get(reverse('signup')).status_code, 200)

    def test_login_page(self):
        # login page should load for everyone
        self.assertEqual(self.client.get(reverse('login')).status_code, 200)

    # --- auth tests ---

    def test_signup_creates_user(self):
        # posting to signup should create a new user
        self.client.post(reverse('signup'), {
            'username': 'newuser',
            'password': 'pass1234',
            'confirm_password': 'pass1234'
        })
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_works(self):
        # correct credentials should log in
        response = self.client.post(reverse('login'), {
            'username': 'sumit',
            'password': 'test1234'
        })
        self.assertIn(response.status_code, [200, 302])

    def test_login_wrong_password(self):
        # wrong password should not redirect (should stay on login page)
        response = self.client.post(reverse('login'), {
            'username': 'sumit',
            'password': 'wrongpass'
        })
        self.assertNotEqual(response.status_code, 302)

    # --- redirect tests for logged out users ---

    def test_feed_redirects_logged_out(self):
        response = self.client.get(reverse('feed'))
        self.assertRedirects(response, f"/accounts/login/?next={reverse('feed')}")

    def test_dashboard_redirects_logged_out(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f"/accounts/login/?next={reverse('dashboard')}")

    def test_profile_redirects_logged_out(self):
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, f"/accounts/login/?next={reverse('profile')}")

    # --- page load tests for logged in users ---

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

    # --- feature tests ---

    def test_create_post(self):
        # logged in user should be able to create a post
        self.client.login(username='sumit', password='test1234')
        self.client.post(reverse('create_post'), {'content': 'A brand new post!'})
        self.assertTrue(Post.objects.filter(content='A brand new post!').exists())

    def test_like_post(self):
        # liking a post should create a Like object
        self.client.login(username='sumit', password='test1234')
        self.client.post(reverse('like_post', args=[self.post.id]))
        self.assertTrue(Like.objects.filter(user=self.user, post=self.post).exists())

    def test_add_comment(self):
        # posting a comment should create a Comment object
        self.client.login(username='sumit', password='test1234')
        self.client.post(reverse('post_detail', args=[self.post.id]), {'content': 'Great post!'})
        self.assertTrue(Comment.objects.filter(content='Great post!').exists())

    def test_delete_post(self):
        # deleting a post should remove it from the database
        self.client.login(username='sumit', password='test1234')
        self.client.post(reverse('delete_post', args=[self.post.id]))
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

    def test_follow_user(self):
        # following a user should create a Follow object
        other = User.objects.create_user(username='rahul', password='test1234')
        self.client.login(username='sumit', password='test1234')
        self.client.post(reverse('follow_user', args=['rahul']))
        self.assertTrue(Follow.objects.filter(follower=self.user, following=other).exists())