"""Модель."""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db import models

User = get_user_model()


class PublishedModel(models.Model):
    """База"""

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.',
    )
    created_at = models.DateTimeField(
        verbose_name="Добавлено", auto_now_add=True, auto_now=False
    )

    class Meta:
        abstract = True


class ModelTitle(models.Model):
    """Заголовок"""

    title = models.CharField(max_length=256, verbose_name='Заголовок')

    class Meta:
        abstract = True


class Location(PublishedModel):
    """Место"""

    name = models.CharField(
        max_length=256,
        blank=False,
        verbose_name='Название места'
    )

    class Meta:
        """Модель."""

        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Category(PublishedModel, ModelTitle):
    """Модель"""

    description = models.TextField(
        blank=False,
        verbose_name='Описание'
    )

    slug = models.SlugField(
        unique=True,
        blank=False,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        """Модель."""

        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title

    # Получение полного адреса объекта
    def get_absolute_url(self):
        return reverse(
            "blog:category_posts", kwargs={"category_slug": self.slug}
        )


class Post(PublishedModel, ModelTitle):
    """Модель."""

    text = models.TextField(
        blank=False,
        verbose_name='Текст'
    )

    pub_date = models.DateTimeField(
        blank=False,
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        )
    )

    author = models.ForeignKey(
        User,
        blank=False,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )

    location = models.ForeignKey(
        Location,
        blank=True,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Местоположение'
    )

    category = models.ForeignKey(
        Category,
        blank=False,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )

    image = models.ImageField(
        'Изображение',
        blank=True,
        upload_to='img/'
    )

    class Meta:
        """Модель."""

        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)
        default_related_name = 'posts'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:post_detail", kwargs={"post_id": self.pk})


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='comments',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Пост',
        related_name='comments',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
    )
    created_at = models.DateTimeField(
        verbose_name='Дата',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)

    def __str__(self):
        return self.text[:20]
