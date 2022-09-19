from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.SignUpFormView.as_view(), name='signup'),
    path('login/', views.LoginFormView.as_view(), name='login'),

    path('', views.HomeView.as_view(), name='home'),

    path('user-profile/<int:pk>/', views.UserProfileView.as_view(), name='user-profile'),
    path('change-password/<int:pk>/', views.ChangePasswordFormView.as_view(), name='change-password'),
    path('edit-profile/<int:pk>/', views.EditProfileFormView.as_view(), name='edit-profile'),
    path('delete-user/<int:pk>/', views.DeleteUserView.as_view(), name='delete-user'),

    path('about-user/', views.AboutUserView.as_view(), name='about-user'),
    path('edit-about-user/<int:pk>/', views.EditAboutUserFormView.as_view(), name='edit-about-user'),

    path('post-categories/', views.PostCategoryView.as_view(), name='post-categories'),
    path('create-post-category/', views.PostCategoryFormView.as_view(), name='create-post-category'),
    path('edit-post-category/<int:pk>/', views.EditPostCategoryFormView.as_view(), name='edit-post-category'),
    path('delete-post-category/<int:pk>/', views.DeletePostCategoryView.as_view(), name='delete-post-category'),

    path('create-post/', views.PostFormView.as_view(), name='create-post'),
    path('post-detail/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('edit-post/<int:pk>/', views.EditPostFormView.as_view(), name='edit-post'),
    path('delete-post/<int:pk>/', views.DeletePostView.as_view(), name='delete-post'),

    path('search/', views.SearchView.as_view(), name='search'),

    path('user-follow/<int:pk>/', views.UserFollowView.as_view(), name='user-follow'),

    path('saved-posts/<int:pk>/', views.SavedPostView.as_view(), name='saved-posts'),

    path('post-likers/<int:pk>/', views.PostLikersView.as_view(), name='post-likers'),

    path('edit-comment/<int:pk>/', views.EditCommentFormView.as_view(), name='edit-comment'),

    path('comment-likers/<int:pk>/', views.CommentLikersView.as_view(), name='comment-likers'),

    path('logout/', views.Logout.as_view(), name='logout')
]
