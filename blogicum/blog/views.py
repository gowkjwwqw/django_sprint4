from django.shortcuts import (
    get_object_or_404,
    redirect
)

from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    ListView
)

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.urls import reverse, reverse_lazy

from .forms import CreateCommentForm, CreatePostForm
from blog.models import Category, Comment, Post
from .utils import (filter_published_posts)


User = get_user_model()
PAGINATED_BY = 10


# Главная страница
class IndexListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    # Имя переменной в шаблоне
    context_object_name = 'post_list'
    paginate_by = PAGINATED_BY
    # Кастомная выборка объектов
    queryset = filter_published_posts(Post.objects)


# Категории
class CategoryListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = PAGINATED_BY

    # Фильтрование объектов
    def get_queryset(self):
        # self.kwargs содержит именованные параметры из URL-паттерна
        # /category/django-tutorial/ в category_slug = "django-tutorial"
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(
            Category, slug=category_slug,
            is_published=True
        )
        posts = filter_published_posts(category.posts.all())
        return posts


# Детали поста
class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    # Как называется параметр
    pk_url_kwarg = 'post_id'

    # Функция для формирования контекста (словарь)
    def get_context_data(self, **kwargs):
        # Получаем базовый контекст
        context = super().get_context_data(**kwargs)
        # Форма создания комментариев
        context['form'] = CreateCommentForm()
        # Вывод всех комментариев
        # prefetch_related - предзагрузка
        context['comments'] = (
            self.get_object().comments.prefetch_related('author').all()
        )
        return context

    # Получаем объект по id
    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs.get(self.pk_url_kwarg))
        # Если юзер автор поста, показываем
        if self.request.user == post.author:
            return post
        # Иначе только отфильтрованные
        return get_object_or_404(
            filter_published_posts(Post.objects.all()),
            pk=self.kwargs.get(self.pk_url_kwarg)
        )


# Профиль автора
class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = PAGINATED_BY

    def get_queryset(self):
        author = get_object_or_404(User, username=self.kwargs['username'])
        posts = author.posts.all()
        if self.request.user != author:
            posts = filter_published_posts(posts)
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User, username=self.kwargs['username']
        )
        return context


# Создание поста
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = CreatePostForm
    template_name = 'blog/create.html'

    # Функия обработки формы, которая прошла валидацию
    def form_valid(self, form):
        # Присваиваем полю автор значению пользователя
        form.instance.author = self.request.user
        # Родительный класс для сохранения формы в БД и редирект на success_url
        return super().form_valid(form)

    # Возвращаемся в профиль автора
    def get_success_url(self):
        return reverse(
            'blog:profile',
            args=[self.request.user.username]
        )


# Обновление поста
class PostUpdateView(LoginRequiredMixin, UpdateView):
    form_class = CreatePostForm
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    # Первая функция для обработки запроса
    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])
        # Если пользователь не автор, то показываем просто пост
        if self.request.user != post.author:
            return redirect('blog:post_detail',
                            post_id=self.kwargs[self.pk_url_kwarg])
        # Иначе перенаправляем на редактирование
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       args=[self.kwargs[self.pk_url_kwarg]])


# Удаление поста
class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def delete(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])
        if self.request.user != post.author:
            return redirect('blog:index')

        return super().delete(request, *args, **kwargs)


# Создание комментария
class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CreateCommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])


# Удаление комментария
class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def delete(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=self.kwargs[self.pk_url_kwarg])
        if self.request.user != comment.author:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])


# Обновление комментария
class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CreateCommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=self.kwargs[self.pk_url_kwarg])
        if self.request.user != comment.author:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])
