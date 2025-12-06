from .models import Comment, Post
from django.utils import timezone
from django import forms


class CreateCommentForm(forms.ModelForm):
    # Указываем поля с какой модели брать и какие сделать видными, запятая
    # - для создания кортежа
    class Meta:
        model = Comment
        fields = ("text",)


class CreatePostForm(forms.ModelForm):
    pub_date = forms.DateTimeField(
        initial=timezone.now,
        required=True,
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
            },
            format='%Y-%m-%dT%H:%M',
        ),
    )

    class Meta:
        model = Post
        fields = (
            'title',
            'image',
            'text',
            'pub_date',
            'location',
            'category',
            'is_published',
        )
