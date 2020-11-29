from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return str(self.title)


class Post(models.Model):
    text = models.TextField(
        verbose_name='Введите текст', help_text='Чем хотите поделиться?'
        )
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts"
        )
    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL,
        blank=True, null=True, related_name="posts",
        verbose_name='Выберите тему', help_text='Любую из списка'
    )
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    def __str__(self):
        text_part = self.text[:30]
        date = self.pub_date
        author = self.author
        return f'{author}.{date}.{text_part}'

    class Meta:
        ordering = ("-pub_date",)


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments',
        verbose_name='Публикация'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments',
        verbose_name='Автор'
    )
    text = models.TextField(
        max_length=200,
        verbose_name='Текст комментария',
        help_text='Ваше мнение важно для автора'
        )
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name='Время написания')

    class Meta:
        ordering = ("-created",)


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(
                User,
                on_delete=models.CASCADE,
                related_name='following'
    )

    class Meta:
        unique_together = ['user', 'author']
