from mainapp.models import AboutUser, Comment, Follow, Post, PostCategory, Like, Save, CommentLike
from django.contrib.auth import login
from django.http.response import HttpResponseRedirect
from django.views.generic import TemplateView, DetailView, UpdateView, DeleteView, ListView, CreateView
from mainapp.forms import ChangePasswordForm, EditAboutUserForm, EditCommentForm, EditPostCategoryForm, EditPostForm, EditProfileForm, PostCategoryForm, PostForm, SignUpForm, LoginForm
from django.shortcuts import render, redirect
from django.contrib.auth.views import FormView, LogoutView, PasswordChangeView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime

# Create your views here.


class SignUpFormView(FormView):
    template_name = 'mainapp/signup.html'
    success_url = reverse_lazy('login')
    model = User
    form_class = SignUpForm

    def form_valid(self, form):
        form.save()
        data = self.request.POST
        new_user = User.objects.filter(username = data.get('username'))[0]

        if data.get('age') == '':
            age = 0
        else:
            age = int(data.get('age'))

        if data.get('contact_number') == '':
            contact_number = None
        else:
            contact_number = int(data.get('contact_number'))


        AboutUser.objects.get_or_create(
            user = new_user,
            gender = data.get('gender'),
            age = age,
            contact_number = contact_number,
            description = data.get('description')
        )

        return super().form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('home')
        return super().get(*args, **kwargs)



class LoginFormView(FormView):
    template_name = 'mainapp/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        return super().form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('home')
        return super().get(*args, **kwargs)


class HomeView(LoginRequiredMixin, ListView):
    template_name = 'mainapp/home.html'
    model = Post
    context_object_name = 'posts'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        ################################
        # Search Filter
        post_categories = []
        for cat in PostCategory.objects.all():
            post_categories.append(cat.category_name)
        context['post_categories'] = post_categories

        current_year = datetime.now().year
        context['years'] = [str(x) for x in range(current_year, current_year - 5, -1)]

        data = self.request.GET
        post_name_input = data.get('post-name') or ''
        post_category_input = data.get('post-category') or ''
        if (data.get('post-month') == '') | (data.get('post-month') is None):
            post_month_input = 13
        else:
            post_month_input = int(data.get('post-month'))
        post_year_input = data.get('post-year') or '' 

        context['post_name_input'] = post_name_input
        context['post_category_input'] = post_category_input
        context['post_month_input'] = post_month_input
        context['post_year_input'] = post_year_input


        # month name
        # datetime.strptime(str(datetime.now().month), "%m").strftime('%B')

        if (data.get('post-month') == '') & (data.get('post-year') == ''):
            context['posts'] = context['posts'].filter(
                post_title__istartswith = post_name_input,
                post_category__category_name__istartswith = post_category_input,
            )

        elif (data.get('post-month') == '') & (data.get('post-year') != ''):
            context['posts'] = context['posts'].filter(
                post_title__istartswith = post_name_input,
                post_category__category_name__istartswith = post_category_input,
                post_created__year = post_year_input
            )

        elif (data.get('post-month') != '') & (data.get('post-year') == ''):
            context['posts'] = context['posts'].filter(
                post_title__istartswith = post_name_input,
                post_category__category_name__istartswith = post_category_input,
                post_created__month = post_month_input
            )

        elif (data.get('post-month') != '') & (data.get('post-year') != '') &\
             (data.get('post-month') is not None) & (data.get('post-year') is not None):
            context['posts'] = context['posts'].filter(
                post_title__istartswith = post_name_input,
                post_category__category_name__istartswith = post_category_input,
                post_created__month = post_month_input,
                post_created__year = post_year_input
            )

        ################################

        ################################
        # Showing only followings posts
        follower = User.objects.get(id = self.request.user.id)
        posts = context['posts'].filter(posted_by__id = self.request.user.id)
        for usr in Follow.objects.filter(follower = follower):
            following_usr = User.objects.get(id = usr.following.id)
            q = context['posts'].filter(posted_by__id = following_usr.id)
            posts = posts | q

        # showing likes/saves

        all_posts = {}
        for post in posts:
            all_posts[post] = {}

            num_like = Like.objects.filter(liked_by = User.objects.get(id = self.request.user.id), post = post).count()
            tot_like = Like.objects.filter(post = post).count()
            num_save = Save.objects.filter(saved_by = User.objects.get(id = self.request.user.id), post = post).count()

            all_posts[post]['comments'] = {}
            for cmt in Comment.objects.filter(post = post):
                usr_cmt_like = CommentLike.objects.filter(
                    liked_by = User.objects.get(id = self.request.user.id),
                    comment = cmt).count()
                tot_cmt_like_num = CommentLike.objects.filter(comment = cmt).count()

                all_posts[post]['comments'][cmt] = {}

                all_posts[post]['comments'][cmt]['comment_like'] = tot_cmt_like_num
                if usr_cmt_like == 1:
                    all_posts[post]['comments'][cmt]['comment_status'] =  False
                elif usr_cmt_like == 0:
                    all_posts[post]['comments'][cmt]['comment_status'] =  True



            # comments = Comment.objects.filter(post = post)

            all_posts[post]['total_likes'] = tot_like
            
            if num_like == 1:
                all_posts[post]['like_status'] = False
            elif num_like == 0:
                all_posts[post]['like_status'] = True

            if num_save == 1:
                all_posts[post]['save_status'] = False
            elif num_save == 0:
                all_posts[post]['save_status'] = True

            # all_posts[post]['comments'] = comments

            

        context['all_posts'] = all_posts


        ################################

        return context


    def post(self, *args, **kwargs):
        data = self.request.POST

        post_like = data.get('post-like')
        post_save = data.get('post-save')

        post_comment_id = data.get('post-comment-id')
        post_comment = data.get('post-comment')

        delete_comment = data.get('delete-comment')

        comment_like = data.get('comment-like')

        if post_like is not None:
            if post_like.split('-')[0] == 'like':
                Like.objects.get_or_create(
                    liked_by = User.objects.get(id = self.request.user.id),
                    post = Post.objects.get(id = int(post_like.split('-')[1])),
                )
            elif post_like.split('-')[0] == 'unlike':
                Like.objects.get(
                    liked_by = User.objects.get(id = self.request.user.id),
                    post = Post.objects.get(id = int(post_like.split('-')[1])),
                    ).delete()

        elif post_save is not None:
            if post_save.split('-')[0] == 'save':
                Save.objects.get_or_create(
                    saved_by = User.objects.get(id = self.request.user.id),
                    post = Post.objects.get(id = int(post_save.split('-')[1]))
                )

            elif post_save.split('-')[0] == 'unsave':
                Save.objects.get(
                    saved_by = User.objects.get(id = self.request.user.id),
                    post = Post.objects.get(id = int(post_save.split('-')[1]))
                ).delete()

        elif post_comment_id is not None:
            if post_comment.strip() != '':
                Comment.objects.create(
                    comment_by = User.objects.get(id = self.request.user.id),
                    post = Post.objects.get(id = post_comment_id),
                    comment = post_comment
                )
        
        elif delete_comment is not None:
            Comment.objects.get(id = int(delete_comment)).delete()

        elif comment_like is not None:
            if comment_like.split('-')[0] == 'like':
                CommentLike.objects.get_or_create(
                    liked_by = User.objects.get(id = self.request.user.id),
                    comment = Comment.objects.get(id = int(comment_like.split('-')[1]))
                )
            elif comment_like.split('-')[0] == 'unlike':
                CommentLike.objects.get(
                    liked_by = User.objects.get(id = self.request.user.id),
                    comment = Comment.objects.get(id = int(comment_like.split('-')[1]))
                ).delete()



        return redirect('home')



class Logout(LoginRequiredMixin, LogoutView):
    next_page = 'login'


class UserProfileView(LoginRequiredMixin, DetailView):
    template_name = 'mainapp/user-profile.html'
    model = User
    context_object_name = 'user'

    def get(self, *args, **kwargs):
        try:
            User.objects.get(id = kwargs['pk'])
        except:
            return HttpResponseRedirect(f'/user-profile/{self.request.user.id}/')
        return super().get(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        ###############
        # About User
        user_id = kwargs.get('object').id
        user_info = User.objects.get(id = user_id)
        user_abt = AboutUser.objects.get(user = user_info)

        context['user_abt'] = user_abt
        ###############

        ###############
        # Showing Posts
        posts = Post.objects.filter(posted_by = User.objects.get(id = user_id))
        context['posts'] = posts

        all_posts = {}
        for post in posts:
            all_posts[post] = {}

            total_like = Like.objects.filter(post = post).count()
            num_like = Like.objects.filter(post = post, liked_by = User.objects.get(id = self.request.user.id)).count()
            num_save = Save.objects.filter(post = post, saved_by = User.objects.get(id = self.request.user.id)).count()
            # comments = Comment.objects.filter(post = post)


            all_posts[post]['comments'] = {}
            for cmt in Comment.objects.filter(post = post):
                tot_cmt_like = CommentLike.objects.filter(comment = cmt).count()
                usr_cmt_like = CommentLike.objects.filter(
                    liked_by = User.objects.get(id = self.request.user.id), 
                    comment = cmt).count()

                all_posts[post]['comments'][cmt] = {}

                all_posts[post]['comments'][cmt]['comment_like'] = tot_cmt_like
                if usr_cmt_like == 1:
                    all_posts[post]['comments'][cmt]['comment_status'] = False
                elif usr_cmt_like == 0:
                    all_posts[post]['comments'][cmt]['comment_status'] = True



            all_posts[post]['total_likes'] = total_like 
            if num_like == 1:
                all_posts[post]['like_status'] = False
            elif num_like == 0:
                all_posts[post]['like_status'] = True

            if num_save == 1:
                all_posts[post]['save_status'] = False
            elif num_save == 0:
                all_posts[post]['save_status'] = True

            # all_posts[post]['comments'] = comments

        context['all_posts'] = all_posts

        ###############

        ###############
        # Showing Follow/UnFollow
        follower = User.objects.get(id = self.request.user.id)
        following = User.objects.get(id = user_id)
        rel_cnt = Follow.objects.filter(follower = follower, following = following).count()
        if rel_cnt == 1:
            context['avail_follow'] = False
        elif rel_cnt == 0:
            context['avail_follow'] = True
        ###############

        ###############
        # Showing number of followers/followings
        context['num_followers'] = Follow.objects.filter(following = user_id).count() # Others are following to me
        context['num_followings'] = Follow.objects.filter(follower = user_id).count() # I am following to others
        ###############

        return context

    def post(self, *args, **kwargs):
        data = self.request.POST

        follow_status = data.get('follow-status')
        like_post = data.get('like-post-status')
        save_post = data.get('save-post')

        post_comment_id = data.get('post-comment-id')
        post_comment = data.get('post-comment')

        delete_comment = data.get('delete-comment')

        comment_like = data.get('comment-like')


        user_id = kwargs['pk']
        follower = User.objects.get(id = self.request.user.id)
        following = User.objects.get(id = user_id)

        if (user_id != self.request.user.id) & (follow_status is not None):
            if follow_status == 'follow':
                Follow.objects.get_or_create(
                    follower = follower,
                    following = following
                )
            elif follow_status == 'unfollow':
                Follow.objects.get(
                    follower = follower,
                    following = following
                ).delete()

        elif like_post is not None:
            lk_num = Like.objects.filter(post = Post.objects.get(id = like_post), liked_by = User.objects.get(id = self.request.user.id)).count()
            if lk_num == 0:
                Like.objects.get_or_create(
                    post =Post.objects.get(id = like_post),
                    liked_by = User.objects.get(id = self.request.user.id)
                )
            elif lk_num == 1:
                Like.objects.get(
                    post =Post.objects.get(id = like_post),
                    liked_by = User.objects.get(id = self.request.user.id)
                ).delete()

        elif save_post is not None:
            if save_post.split('-')[0] == 'save':
                Save.objects.get_or_create(
                    post = Post.objects.get(id = int(save_post.split('-')[1])),
                    saved_by = User.objects.get(id = self.request.user.id)
                )
            elif save_post.split('-')[0] == 'unsave':
                Save.objects.get(
                    post = Post.objects.get(id = int(save_post.split('-')[1])),
                    saved_by = User.objects.get(id = self.request.user.id)
                ).delete()

        elif post_comment_id is not None:
            if post_comment.strip() != '':
                Comment.objects.create(
                    comment_by = User.objects.get(id = self.request.user.id),
                    comment = post_comment,
                    post = Post.objects.get(id = post_comment_id)
                )

        elif delete_comment is not None:
            Comment.objects.get(id = int(delete_comment)).delete()

        elif comment_like is not None:
            if comment_like.split('-')[0] == 'like':
                CommentLike.objects.get_or_create(
                    liked_by = User.objects.get(id = self.request.user.id),
                    comment = Comment.objects.get(id = int(comment_like.split('-')[1]))
                )
            elif comment_like.split('-')[0] == 'unlike':
                CommentLike.objects.get(
                    liked_by = User.objects.get(id = self.request.user.id),
                    comment = Comment.objects.get(id = int(comment_like.split('-')[1]))
                ).delete()
            
        return HttpResponseRedirect(f'/user-profile/{user_id}/')



class ChangePasswordFormView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'mainapp/change-password.html'
    form_class = ChangePasswordForm

    def get(self, *args, **kwargs):
        if self.request.user.id != kwargs['pk']:
            return HttpResponseRedirect(f'/change-password/{self.request.user.id}/')
        return super().get(*args, **kwargs)

    def get_success_url(self, *args, **kwargs):
        return '{}'.format(reverse_lazy('user-profile', kwargs={'pk': self.request.user.id}))

class EditProfileFormView(LoginRequiredMixin, UpdateView):
    template_name = 'mainapp/edit-profile.html'
    model = User
    form_class = EditProfileForm
    context_object_name = 'user'

    def get_success_url(self, *args, **kwargs):
        return '{}'.format(reverse_lazy('user-profile', kwargs={'pk': self.request.user.id}))

    def get(self, *args, **kwargs):
        if self.request.user.id != kwargs['pk']:
            return HttpResponseRedirect(f'/edit-profile/{self.request.user.id}/')
        return super().get(*args, **kwargs)


class DeleteUserView(LoginRequiredMixin, DeleteView):
    template_name = 'mainapp/delete-user.html'
    success_url = reverse_lazy('login')
    model = User
    context_object_name = 'user'

    def get(self, *args, **kwargs):
        if self.request.user.id != kwargs['pk']:
            return HttpResponseRedirect(f'/delete-user/{self.request.user.id}/')
        return super().get(*args, **kwargs)


#####################################################################################################




class AboutUserView(LoginRequiredMixin, TemplateView):
    template_name = 'mainapp/about-user.html'
    
    def get_context_data(self, *args, **kwargs):
        context =  super().get_context_data(*args, **kwargs)
        context['about'] = AboutUser.objects.filter(user = User.objects.get(id = self.request.user.id))[0]
        return context



class EditAboutUserFormView(LoginRequiredMixin, UpdateView):
    template_name = 'mainapp/edit-about-user.html'
    model = AboutUser
    form_class = EditAboutUserForm
    context_object_name = 'about'
    success_url = reverse_lazy('about-user')

    def get(self, *args, **kwargs):
        log_abt_usr = AboutUser.objects.get(user = self.request.user).id
        if kwargs['pk'] != log_abt_usr:
            return HttpResponseRedirect(f'/edit-about-user/{AboutUser.objects.get(user = self.request.user).id}/')
        return super().get(*args, **kwargs)





######################################################################################################

class PostCategoryView(LoginRequiredMixin, ListView):
    template_name = 'mainapp/post-categories.html'
    model = PostCategory
    context_object_name = 'categories'


class PostCategoryFormView(LoginRequiredMixin, CreateView):
    template_name = 'mainapp/create-post-category.html'
    model = PostCategory
    form_class = PostCategoryForm
    success_url = reverse_lazy('post-categories')

    def get(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            return redirect('post-categories')
        return super().get(*args, **kwargs)

class EditPostCategoryFormView(LoginRequiredMixin, UpdateView):
    template_name = 'mainapp/edit-post-category.html'
    model = PostCategory
    form_class = EditPostCategoryForm
    context_object_name = 'category'
    success_url = reverse_lazy('post-categories')

    def get(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            return redirect('post-categories')
        return super().get(*args, **kwargs)


class DeletePostCategoryView(LoginRequiredMixin, DeleteView):
    template_name = 'mainapp/delete-post-category.html'
    success_url = reverse_lazy('post-categories')
    model = PostCategory
    context_object_name = 'category'

    def get(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            return redirect('post-categories')
        return super().get(*args, **kwargs)


##############################################################################################################


class PostFormView(LoginRequiredMixin, CreateView):
    template_name = 'mainapp/create-post.html'
    model = Post
    form_class = PostForm
    context_object_name = 'post'
    
    def get_success_url(self, *args, **kwargs):
        return '{}'.format(reverse_lazy('user-profile', kwargs={'pk': self.request.user.id}))

    def form_valid(self, form):
        form.instance.posted_by = User.objects.get(id = self.request.user.id)
        return super().form_valid(form)


class PostDetailView(LoginRequiredMixin, DetailView):
    template_name = 'mainapp/post-detail.html'
    model = Post
    context_object_name = 'post'

    def get_context_data(self, *args, **kwargs):
        post_id = kwargs['object'].id
        context = super().get_context_data(*args, **kwargs)

        like_num = Like.objects.filter(
            liked_by = User.objects.get(id = self.request.user.id),
            post = Post.objects.get(id = post_id)
        ).count()

        save_num = Save.objects.filter(
            saved_by = User.objects.get(id = self.request.user.id),
            post = Post.objects.get(id = post_id)
        ).count()

        total_likes = Like.objects.filter(post = Post.objects.get(id = post_id)).count()

        # context['comments'] = Comment.objects.filter(post = Post.objects.get(id = post_id))

        context['comments'] = {}
        for cmt in Comment.objects.filter(post = Post.objects.get(id = post_id)):
            tot_cmt_like = CommentLike.objects.filter(comment = cmt).count()
            usr_cmt_like = CommentLike.objects.filter(
                liked_by = User.objects.get(id = self.request.user.id), 
                comment = cmt).count()
            context['comments'][cmt] = {}
            
            context['comments'][cmt]['comment_like'] = tot_cmt_like
            if usr_cmt_like == 1:
                context['comments'][cmt]['comment_status'] = False
            elif usr_cmt_like == 0:
                context['comments'][cmt]['comment_status'] = True

        context['total_likes'] = total_likes

        if like_num == 1:
            context['like_status'] = False
        elif like_num == 0:
            context['like_status'] = True

        if save_num == 1:
            context['save_status'] = False
        elif save_num == 0:
            context['save_status'] = True 

        return context

    def get(self, *args, **kwargs):
        for i in Post.objects.all():
            if kwargs['pk'] == i.id:
                return super().get(*args, **kwargs)

        return redirect('home')

    def post(self, *args, **kwargs):
        post_id = kwargs['pk']
        data = self.request.POST

        like_status = data.get('post-like')
        save_status = data.get('post-save')

        post_comment_id = data.get('post-comment-id')
        post_comment = data.get('post-comment')

        delete_comment = data.get('delete-comment')

        comment_like = data.get('comment-like')


        if like_status is not None:
            if like_status == 'like':
                Like.objects.get_or_create(
                    liked_by = User.objects.get(id = self.request.user.id),
                    post = Post.objects.get(id = post_id)
                    )
            elif like_status == 'undo-like':
                Like.objects.get(
                    liked_by = User.objects.get(id = self.request.user.id),
                    post = Post.objects.get(id = post_id)
                    ).delete()

        elif save_status is not None:
            if save_status == 'save':
                Save.objects.get_or_create(
                    post = Post.objects.get(id = post_id),
                    saved_by = User.objects.get(id = self.request.user.id)
                ) 
            elif save_status == 'unsave':
                Save.objects.get(
                    saved_by = User.objects.get(id = self.request.user.id),
                    post = Post.objects.get(id = post_id)
                ).delete()

        elif post_comment_id is not None:
            if post_comment.strip() != '':
                Comment.objects.create(
                    comment_by = User.objects.get(id = self.request.user.id),
                    comment = post_comment,
                    post = Post.objects.get(id = post_id)    
                )

        elif delete_comment is not None:
            Comment.objects.get(id = int(delete_comment)).delete()


        elif comment_like is not None:
            if comment_like.split('-')[0] == 'like':
                CommentLike.objects.get_or_create(
                    liked_by = User.objects.get(id = self.request.user.id),
                    comment = Comment.objects.get(id = int(comment_like.split('-')[1]))
                )
            elif comment_like.split('-')[0] == 'unlike':
                CommentLike.objects.get(
                    liked_by = User.objects.get(id = self.request.user.id),
                    comment = Comment.objects.get(id = int(comment_like.split('-')[1]))
                ).delete()

        return HttpResponseRedirect(f'/post-detail/{post_id}/')
        

class EditPostFormView(LoginRequiredMixin, UpdateView):
    template_name = 'mainapp/edit-post.html'
    model = Post
    context_object_name = 'post'
    form_class = EditPostForm

    def get_success_url(self, *args, **kwargs):
        return '{}'.format(reverse_lazy('user-profile', kwargs={'pk': self.request.user.id}))

    def get(self, *args, **kwargs):
        try:
            if Post.objects.get(id = kwargs['pk']).posted_by.id != self.request.user.id:
                return HttpResponseRedirect(f'/user-profile/{self.request.user.id}/')
        except:
            return HttpResponseRedirect(f'/user-profile/{self.request.user.id}/')
        return super().get(*args, **kwargs)
    

class DeletePostView(LoginRequiredMixin, DeleteView):
    template_name = 'mainapp/delete-post.html'
    model = Post
    context_object_name = 'post'
    
    def get_success_url(self, *args, **kwargs):
        return '{}'.format(reverse_lazy('user-profile', kwargs={'pk': self.request.user.id}))

    def get(self, *args, **kwargs):
        try:
            if Post.objects.get(id = kwargs['pk']).posted_by.id != self.request.user.id:
                return HttpResponseRedirect(f'/user-profile/{self.request.user.id}/')
        except:
            return HttpResponseRedirect(f'/user-profile/{self.request.user.id}/')
        return super().get(*args, **kwargs)


##################################################################################################################


class SearchView(LoginRequiredMixin, TemplateView):
    template_name = 'mainapp/search.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        data = self.request.GET

        search_input = data.get('search') or ''
        context['search_input'] = search_input

        search_for = data.get('search-for')

        if search_for == 'post-category':
            context['active_post_category'] = True
            if search_input != '':
                context['posts'] = Post.objects.filter(post_category__category_name__istartswith = search_input)

        elif search_for == 'post':
            context['active_post'] = True
            if search_input != '':
                context['posts'] = Post.objects.filter(post_title__icontains = search_input)


        else:
            context['active_user'] = True
            if search_input != '':
                context['users'] = {}
                for usr in User.objects.filter(username__icontains = search_input):
                    abt_usr = AboutUser.objects.get(user = usr.id)
                    context['users'][usr] = abt_usr


        return context

#########################################################################################################################


class UserFollowView(LoginRequiredMixin, TemplateView):
    template_name = 'mainapp/user-follow.html'
    # model = Follow

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context['followings'] = Follow.objects.filter(follower = kwargs['pk']) # I am following others
        context['followers'] = Follow.objects.filter(following = kwargs['pk']) # Others are following me
        return context

    def get(self, *args, **kwargs):
        all_usr = []
        for usr in User.objects.all():
            all_usr.append(usr.id)
        if kwargs['pk'] not in all_usr:
            return HttpResponseRedirect(f'/user-follow/{self.request.user.id}/')
        return super().get(*args, **kwargs)


##########################################################################################################################

class SavedPostView(LoginRequiredMixin, TemplateView):
    template_name = 'mainapp/saved-posts.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['saves'] = Save.objects.filter(saved_by = User.objects.get(id = kwargs['pk']))
        context['saver_id'] = kwargs['pk']

        all_posts = []
        for post in context['saves']:
            all_posts.append(Post.objects.get(id = post.post.id))

        all_saves = {}
        for post in all_posts:
            all_saves[post] = {}

            num_like = Like.objects.filter(liked_by = User.objects.get(id = self.request.user.id), post = post).count()
            num_save = Save.objects.filter(saved_by = User.objects.get(id = self.request.user.id), post = post).count()
            total_likes = Like.objects.filter(post = post).count()
            # comments = Comment.objects.filter(post = post)

            all_saves[post]['comments'] = {}
            for cmt in Comment.objects.filter(post = post):
                tot_cmt_like = CommentLike.objects.filter(comment = cmt).count()
                usr_cmt_like = CommentLike.objects.filter(
                    liked_by = User.objects.get(id = self.request.user.id), 
                    comment = cmt).count()

                all_saves[post]['comments'][cmt] = {}

                all_saves[post]['comments'][cmt]['comment_like'] = tot_cmt_like
                if usr_cmt_like == 1:
                    all_saves[post]['comments'][cmt]['comment_status'] = False
                elif usr_cmt_like == 0:
                    all_saves[post]['comments'][cmt]['comment_status'] = True


            all_saves[post]['total_likes'] = total_likes

            if num_like == 1:
                all_saves[post]['like_status'] = False
            elif num_like == 0:
                all_saves[post]['like_status'] = True
            
            if num_save == 1:
                all_saves[post]['save_status'] = False
            elif num_save == 0:
                all_saves[post]['save_status'] = True

            # all_saves[post]['comments'] = comments

        context['all_saves'] = all_saves


        return context

    def get(self, *args, **kwargs):
        user_id = kwargs['pk']
        if user_id != self.request.user.id:
            return HttpResponseRedirect(f'/saved-posts/{self.request.user.id}/')
        return super().get(*args, **kwargs)


    def post(self, *args, **kwargs):
        data = self.request.POST

        post_like = data.get('post-like')
        post_save = data.get('post-save')

        post_comment_id = data.get('post-comment-id')
        post_comment = data.get('post-comment')

        delete_comment = data.get('delete-comment')

        comment_like = data.get('comment-like')

        if post_like is not None:
            if post_like.split('-')[0] == 'like':
                Like.objects.get_or_create(
                    liked_by = User.objects.get(id = self.request.user.id),
                    post = Post.objects.get(id = int(post_like.split('-')[1]))
                )
            elif post_like.split('-')[0] == 'unlike':
                Like.objects.get(
                    liked_by = User.objects.get(id = self.request.user.id),
                    post = Post.objects.get(id = int(post_like.split('-')[1]))
                ).delete()

        elif post_save is not None:
            if post_save.split('-')[0] == 'save':
                Save.objects.get_or_create(
                    saved_by = User.objects.get(id = self.request.user.id),
                    post = Post.objects.get(id = int(post_save.split('-')[1]))
                )

            elif post_save.split('-')[0] == 'unsave':
                Save.objects.get(
                    saved_by = User.objects.get(id = self.request.user.id),
                    post = Post.objects.get(id = int(post_save.split('-')[1]))
                ).delete()

        elif post_comment_id is not None:
            if post_comment.strip() != '':
                Comment.objects.create(
                    post = Post.objects.get(id = post_comment_id),
                    comment = post_comment,
                    comment_by = User.objects.get(id = self.request.user.id) 
                )

        elif delete_comment is not None:
            Comment.objects.get(id = int(delete_comment)).delete()

        elif comment_like is not None:
            if comment_like.split('-')[0] == 'like':
                CommentLike.objects.get_or_create(
                    liked_by = User.objects.get(id = self.request.user.id),
                    comment = Comment.objects.get(id = int(comment_like.split('-')[1]))
                )

            elif comment_like.split('-')[0] == 'unlike':
                CommentLike.objects.get(
                    liked_by = User.objects.get(id = self.request.user.id),
                    comment = Comment.objects.get(id = int(comment_like.split('-')[1]))
                ).delete()


        return HttpResponseRedirect(f'/saved-posts/{self.request.user.id}/')


####################################################################################################################

class PostLikersView(LoginRequiredMixin, TemplateView):
    template_name = 'mainapp/post-likers.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['users'] = Like.objects.filter(post = Post.objects.get(id = kwargs['pk']))
        context['post'] = Post.objects.get(id = kwargs['pk'])
        return context

####################################################################################################################


class EditCommentFormView(LoginRequiredMixin, UpdateView):
    template_name = 'mainapp/edit-comment.html'
    model = Comment
    form_class = EditCommentForm
    context_object_name = 'comment'

    def get_success_url(self, *args, **kwargs):
        comment_id = self.request.get_full_path().split('/')[-2]
        post_id = Comment.objects.get(id = comment_id).post.id
        # print(self.request.build_absolute_uri())
        return '{}'.format(reverse_lazy('post-detail', kwargs={'pk': post_id}))


    def get(self, *args, **kwargs):
        comment = Comment.objects.get(id = kwargs['pk'])
        if comment.comment_by.id != self.request.user.id:
            return HttpResponseRedirect(f'/post-detail/{comment.post.id}/')
        return super().get(*args, **kwargs)

#######################################################################################################

class CommentLikersView(LoginRequiredMixin, TemplateView):
    template_name = 'mainapp/comment-likers.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        comment = Comment.objects.get(id = kwargs['pk'])
        context['comment_likers'] = CommentLike.objects.filter(comment = comment)

        return context
    