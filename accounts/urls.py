from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/delete/', views.delete_account, name='delete_account'),
    path('users/', views.users_list, name='users_list'),
    path('users/<str:username>/', views.user_profile, name='user_profile'),
    path('users/<str:username>/follow/', views.follow_user, name='follow_user'),
    path('feed/', views.feed, name='feed'),
    path('feed/create/', views.create_post, name='create_post'),
    path('feed/post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('feed/post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('feed/post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('feed/comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
]

handler404 = 'accounts.views.error_404'
handler500 = 'accounts.views.error_500'~