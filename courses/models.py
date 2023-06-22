# python manage.py makemigrations
# python manage.py migrate


from django.db import models
from django.contrib.auth.models import User  # Пользователи Джанго
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .fields import OrderField  # Добавление упорядочивания

'''
Структура обучения: Предмет - Курс - Модуль - Контунт 
Subject 1
    Course 1
    Module 1
        Content 1 (image)
        Content 2 (text)
    Module 2
        Content 3 (text)
        Content 4 (file)
        Content 5 (video)
'''

''' предмет '''


class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


''' курс '''


class Course(models.Model):
    owner = models.ForeignKey(User,
                              related_name='courses_created',
                              on_delete=models.CASCADE)  # преподаватель, создавший этот курс
    subject = models.ForeignKey(Subject,
                                related_name='courses',
                                on_delete=models.CASCADE)  # предмет, к которому относится данный курс
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()  # краткого обзора курса
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title


''' модуль '''


class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=['course'])

    def __str__(self):
        return f'{self.order}. {self.title}'

    class Meta:
        ordering = ['order']


''' контент '''

class Content(models.Model):
    module = models.ForeignKey(Module, related_name='contents', on_delete=models.CASCADE)
    # поле ForeignKey для модели ContentType
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     limit_choices_to={'model__in':('text','video','image','file')})
    # поле PositiveIntegerField для хранения первичного ключа связанного объекта;
    object_id = models.PositiveIntegerField()
    # поле GenericForeignKey для связанного объекта, объединяющее два предыдущих поля
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])

    class Meta:
        ordering = ['order']

''' типы контента, 4 таблицы '''
class ItemBase(models.Model):
    # Поле owner позволяет хранить создавшего контент пользователя
    owner = models.ForeignKey(User, related_name='%(class)s_related', on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class Text(ItemBase):
    content = models.TextField()


class File(ItemBase):
    file = models.FileField(upload_to='files')


class Image(ItemBase):
    file = models.FileField(upload_to='images')


class Video(ItemBase):
    url = models.URLField()
