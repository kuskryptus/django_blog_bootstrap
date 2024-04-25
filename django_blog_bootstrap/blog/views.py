from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import Http404, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View, generic
from django.views.generic.edit import FormMixin, UpdateView

from .forms import CommentForm, PostForm, UserCreateForm
from .models import Comment, Post


class HomePageView(generic.TemplateView):
    template_name = 'blog/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            latest_post = Post.objects.latest()
            context['latest_post'] = latest_post
        except Post.DoesNotExist:
            context['latest_post'] = None
            context['error_message'] = "No posts found."
        except Exception as e:
            context['error_message'] = f"There was an error rendering template: {str(e)}"
        return context


# Displays all articles
class PostListView(generic.ListView):
    queryset = Post.objects.order_by('-published_date')
    template_name = 'post_list.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        try:
            queryset = super().get_queryset()
            if not queryset.exists():
                raise Http404("No posts found.")
            return queryset
        except Exception as e:
            raise Http404(f"An error occurred: {str(e)}")


# Displaying article that you want to read
class PostDetailView(FormMixin, generic.DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    form_class = CommentForm
    raise_exception = True

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        context['comments'] = self.object.comments.filter(parent__isnull=True)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.post = self.object
        form.instance.user = self.request.user
        form.save()
        return super().form_valid(form)


# Form for creating new article
class PostCreateView(LoginRequiredMixin, generic.CreateView):
    model = Post
    template_name = 'blog/post_create.html'
    fields = ['title', 'body', 'image']
    success_url = reverse_lazy('home')
    raise_exception = True

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


# Post editing
class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'blog/post_edit.html'
    fields = ['title', 'body', 'image']
    success_url = reverse_lazy('home')
    raise_exception = True

    def test_func(self):
        return self.request.user == self.get_object().author

    def get_initial(self):
        # Retrieve the instance to be updated
        instance = self.get_object()
        # Populate initial data from the instance
        initial = super().get_initial()
        initial['title'] = instance.title
        initial['body'] = instance.body
        # Add more fields as needed
        return initial


class CommentActionsView(LoginRequiredMixin, View):
    def post(self, request, action, pk):
        comment = get_object_or_404(Comment, pk=pk)
        post_pk = comment.post.pk

        if action == 'delete' and comment.user == request.user:
            comment.delete()
        elif action == 'like':
            comment.likes.add(request.user)
        elif action == 'unlike':
            comment.likes.remove(request.user)
        elif action == 'comment':
            content = request.POST.get('content')
            new_comment = Comment.objects.create(post=comment.post,
                                                 user=request.user,
                                                 content=content,
                                                 parent=comment)
        else:
            return HttpResponseBadRequest("Unsupported action")

        return HttpResponseRedirect(reverse('post_detail', kwargs={'pk': post_pk}))


class PostDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Post
    success_url = reverse_lazy('home')

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


# Like/Unlike post
class PostLikeView(LoginRequiredMixin, View):
    raise_exception = True

    def post(self, request, action, pk):
        post = get_object_or_404(Post, pk=pk)
        if action == "post_like":
            post.likes.add(request.user)
            return HttpResponseRedirect(reverse('post_detail', kwargs={'pk': post.pk}))
        elif action == "post_unlike":
            post.likes.remove(request.user)
            return HttpResponseRedirect(reverse('post_detail', kwargs={'pk': post.pk}))


class CommentDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Comment
    success_url = reverse_lazy('')

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.object.pk})


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = AuthenticationForm

    def get_success_url(self):
        return reverse_lazy('home')


class RegisterView(generic.CreateView):
    form_class = UserCreateForm
    template_name = 'accounts/register.html'

    def get_success_url(self):
        return reverse_lazy('home')


class CustomLogoutView(LogoutView):

    def get_success_url(self):
        return reverse_lazy('login')


