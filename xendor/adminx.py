# -*- coding: utf-8 -*-
from django.contrib import admin
from django.conf import settings

import xadmin

from xendor.forms import PageAdminForm
from xendor.tree_admin import XDP17TreeModelAdmin
from xendor.models import Page, Fragment, Setting


class PageAdmin(object):
    admin_label = u'Управление контентом'

    fieldsets = (
        ('', {
            'classes': ('closed',),
            'fields': ('title', 'menu_title', 'content', 'in_menu'),
        }),
        ('Метаданные', {
            'classes': ('collapse closed',),
            'description': 'Используются поисковиками для лучшей индексации страницы',
            'fields' : ('meta_title', 'meta_description', 'meta_keywords'),
        }),
        ('Настройки', {
            'classes': ('collapse closed',),
            'description': 'Без четкой уверенности сюда лучше не лезть',
            'fields': ('slug', 'visible', 'parameters', 'template', 'app_extension', 'menu_url', 'is_main'),  # 'template',
        }),
        ('В структуре сайта..', {
            'classes': ('hidden',),
            'fields': ('parent',),
        })
    )

    list_display = ['__unicode__', 'app_extension']
    list_filter = ('visible', )

    form = PageAdminForm


class ChunkAdmin(object):
    """Текстовые блоки (чанки)"""
    admin_label = u'Управление контентом'
    
    list_display = ['__unicode__', 'is_html', 'content']
    list_editable = 'is_html',
    
    def get_form(self, request, obj=None, **kwargs):
        if hasattr(obj, 'id'):
            self.exclude = ['title']
        else:
            self.exclude = []
              
        return super(ChunkAdmin, self).get_form(request, obj, **kwargs)

    
xadmin.site.register(Page, PageAdmin)

xadmin.site.register(Fragment)


class SettingAdmin(object):
    admin_label = u'Управление контентом'
    list_display = ('__unicode__', 'value', )
    list_editable = ('value', )
    list_resolve_foreign_keys = ['setting']

xadmin.site.register(Setting, SettingAdmin)