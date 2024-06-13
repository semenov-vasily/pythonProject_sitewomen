from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

class PublishedModel(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=Women.Status.PUBLISHED)


class Women(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'

    title = models.CharField(max_length=255, verbose_name="Заголовок")
    slug = models.SlugField(max_length=255, db_index=True, unique=True)
    content = models.TextField(blank=True, verbose_name="Текст статьи")
    photo = models.ImageField(upload_to="photos/%Y/%m/%d/", default=None, blank=True, null=True, verbose_name="Фото")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время изменения")
    is_published = models.BooleanField(choices=tuple(map(lambda x: (bool(x[0]), x[1]), Status.choices)),
                                       default=Status.DRAFT, verbose_name="Статус")
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, related_name='posts', verbose_name="Категории")
    tags = models.ManyToManyField('TagPost', related_name='tags', verbose_name="Тэги")
    husband = models.OneToOneField('Husband', on_delete=models.SET_NULL, null=True, blank=True, related_name='woman',
                                   verbose_name="Муж")
    author = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name='posts', null=True,
                               default=None)

    objects = models.Manager()
    published = PublishedModel()

    def get_absolute_url(self):
        return reverse('post', kwargs={'post_slug':self.slug})

    class Meta:
        ordering = ['-time_create']
        verbose_name = 'Известные женщины'
        verbose_name_plural = 'Известные женщины'


    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name="Категория")
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})

    def __str__(self):
        return self.name


class TagPost(models.Model):
    tag = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    def get_absolute_url(self):
        return reverse('tag', kwargs={'tag_slug': self.slug})


    def __str__(self):
        return self.tag


class Husband(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя')
    age = models.IntegerField(null=True, verbose_name='Возраст')
    m_count = models.IntegerField(blank=True, default=0, verbose_name='Количество браков')

    class Meta:
        verbose_name = 'Муж'
        verbose_name_plural = 'Мужья'

    def __str__(self):
        return self.name


class UploadFiles(models.Model):
    file = models.FileField(upload_to='uploads_model')


