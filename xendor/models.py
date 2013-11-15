# -*- coding: utf-8 -*-
import mptt
from mptt.models import TreeForeignKey, MPTTModel
from tinymce.models import HTMLField
from django.db import models

from xendor.utils import generate_slug

class Page(MPTTModel):

    parent = TreeForeignKey(u'self', verbose_name=u'Родитель', null=True, blank=True, related_name=u'children')

    title = models.CharField(verbose_name=u"Заголовок", max_length=255, null=False, blank=False)
    menu_title = models.CharField(u'Заголовок пункта меню', max_length = 255, blank = True, default='')
    
    content = HTMLField(u'Текст матетериала', blank=True, null=True)
    visible = models.BooleanField(default=True)
    in_menu = models.BooleanField(default=True)
    is_main = models.BooleanField(default=False)
    app_extension = models.CharField(max_length=255, null=False, blank=True, default='')
    slug = models.SlugField(u'Синоним страницы', max_length = 255, null=True, unique=True, blank = True)
    template = models.CharField(u'Заданный шаблон', max_length = 255, blank = True, null=True)
    
    menu_url = models.CharField(u'URL пункта меню',
        max_length = 255, blank = True, null=True, default='',
        help_text = u'Переопределяет урл страницы, при непустом значении генерирует 301 редирект')

    #метатеги
    meta_title = models.CharField(u'meta-title', max_length = 255, blank = True, null=True, default='')
    meta_description = models.TextField(u'meta-description', blank = True, null=True, default='')
    meta_keywords = models.TextField(u'meta-keywords', blank = True, null=True, default='')

    parameters = models.CharField(u'Дополнительные параметры', max_length = 255, blank = True, default='')

    class MPTTMeta:
        pass

    class Meta:
        verbose_name = u'страница'
        verbose_name_plural = u'Страницы сайта'


    @models.permalink
    def get_absolute_url(self):
        return ('xendor-page', [self.slug])


    def __unicode__(self):
        return self.menu_title or self.title


    def save(self, force_insert=False, force_update=False, using=None):

        #обрезаем длинный тайтл (втихую при работе не через админку)
        if len(self.title) > 250:
            self.title = self.title[:250]

        #генерируем слаг
        slug = self.slug or self.title

        if slug and len(slug) > 240:
            slug = slug[:240]

        slug = generate_slug(self, slug)

        if not self.pk or not self.slug:
            try:
                if not self.parent.is_main and self.parent.visible:
                    if self.parent.in_menu:
                        slug = self.parent.slug + '/' + slug
                    else:
                        ancestors = self.parent.get_ancestors(ascending=True).filter(in_menu=True)
                        if ancestors:
                            slug = ancestors[0].slug + '/' + slug

            except AttributeError:
                pass

        self.slug = slug

        #обеспечиваем невозможность задания двум страницам одного и того же модуля
        if self.app_extension:
            try:
                page = Page.objects.exclude(pk=self.pk).get(app_extension=self.app_extension)
                self.app_extension = ''
            except Page.DoesNotExist:
                pass

        #если главная уже задана, то все попытки сделать две главные - втихую побоку
        if self.is_main:
            try:
                main = Page.objects.get(is_main=True)
                if main != self:
                    self.is_main = False
            except Page.DoesNotExist:
                pass

        #у первой созданной страницы прописываем флаг главной
        if not self.pk:
            count_pages = Page.objects.all().count()
            if count_pages == 0:
                self.is_main = True

        super(Page, self).save(force_insert=False, force_update=False, using=None)


class Fragment(models.Model):
    """Чанки для вывода небольших моментов"""

    name = models.CharField(u'Название', max_length = 255)
    content = models.TextField(u'Content')
    is_html = models.BooleanField(u'Использует html?', default=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'фрагмент сайта'
        verbose_name_plural = u'Фрагменты сайта'


class Setting (models.Model):
    """Настройки сайта"""

    name = models.CharField (u'Параметр', max_length = 255)
    value = models.CharField (u'Значение', max_length = 2000)

    class Meta:
        verbose_name = u'параметр'
        verbose_name_plural = u'Настройки сайта'

    def __unicode__(self):
        return self.name
