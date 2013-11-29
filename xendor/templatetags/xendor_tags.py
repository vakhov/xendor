# -*- coding: utf-8 -*-
"""Все универсальные темплейттеги и утилиты копировать сюда, нах"""

from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter

from xendor.models import Page, Fragment
from xendor.settings import XendorSettings
from xendor.structure import Structure
from xendor.menu import Menu, _render_pars
from xendor.thumbnail import thumbnail

register = template.Library()

@register.inclusion_tag('tags/fragment.html')
def fragment (fragment_name):
    """Вывод чанка (куска текста из модуля текстовые блоки)"""

    try:
        fragment = Fragment.objects.get(name=fragment_name)
    except Fragment.DoesNotExist:
        fragment = ''
        
    return {'fragmaent': fragment}

@register.inclusion_tag('dummy.html', takes_context=True)
def menu(context, params="", template='menu/menu.html'):
    """Рендер меню"""

    #проверка наличия контекста
    try:
        request = context['request']
    except KeyError:
        return {'template': 'empty.html'}

    #инстанцирование класса меню
    try:
        current_url = XendorSettings().get('activated_node') or request.get_full_path().split('?')[0]
        menu = Menu(current_url, parameters=_render_pars(params))
    except Menu.MenuException:
        if settings.DEBUG:
            raise

        menu = None
        template = 'empty.html'

    context.update({'template': template, 'menu': menu, })
    return context


@register.inclusion_tag('dummy.html', takes_context=True)
def level_menu(context, nodes=[], template='menu/level.html'):
    """Рендер уровня меню, вспомогательный тег, с помощью него реализуется многообразие отображений уровней"""

    context.update({'template': template, 'nodes': nodes})
    return context


@register.inclusion_tag('dummy.html', takes_context=True)
def breadcrumbs(context, start_level=0, template='menu/breadcrumbs.html'):
    """Рендер крошки, start_level - уровень, с которого следует начинать"""
    
    try:
        request = context['request']
    except KeyError:
        return {'template': 'empty.html'}

    current_url = XendorSettings().get('activated_node') or request.get_full_path().split('?')[0]

    path = list(Structure().tree.get_path_from_url(current_url, start_level))

    if XendorSettings().get('breadcrumbs_tail'):
        if isinstance(XendorSettings().get('breadcrumbs_tail'), (list, tuple)):
            path += XendorSettings().get('breadcrumbs_tail')
        elif isinstance(XendorSettings().get('breadcrumbs_tail'), dict):
            path.append(XendorSettings().get('breadcrumbs_tail'))

    context.update({
        'template': template,
        'path': path
    })

    return context


@register.inclusion_tag('dummy.html', takes_context=True)
def metatitle(context, template='menu/metatitle.html'):
    """вывод метатега title
        Логика проста: выбираем метатег из
        - промежуточного хранилища в сеттингах
        - текущего элемента структуры (meta_title or title)
        - из главной страницы (которая должна хранить метатеги по-умолчанию)
    """

    try:
        request = context['request']
    except KeyError:
        return {'template': 'empty.html'}

    title = XendorSettings().get('meta_title')

    if not title:
        current_url = XendorSettings().get('activated_node') or request.get_full_path().split('?')[0]
        current_node = Structure().tree.get_element_by_url(current_url)
        if current_node:
            title = current_node.meta_title or current_node.title
        else:
            title = Structure().tree.meta_title or Structure().tree.title
    if not title:
        try:
            main = Page.objects.get(is_main=True)
            title = main.meta_title or main.title
        except Page.DoesNotExist:
            return {'template': 'empty.html'}

    context.update({
        'template': template,
        'title': title
    })

    return context


@register.inclusion_tag('dummy.html', takes_context=True)
def metadescription(context, template='menu/metadescription.html'):
    """Вывод метатега description
        Логика проста: выбираем метатег из
        - промежуточного хранилища в сеттингах
        - текущего элемента структуры
        - из главной страницы (которая должна хранить метатеги по-умолчанию)
    """

    try:
        request = context['request']
    except KeyError:
        return {'template': 'empty.html'}

    description = XendorSettings().get('meta_description')

    if not description:
        current_url = XendorSettings().get('activated_node') or request.get_full_path().split('?')[0]
        current_node = Structure().tree.get_element_by_url(current_url)
        if current_node:
            description = current_node.meta_description or current_node.title
        else:
            description = Structure().tree.meta_description
    if not description:
        try:
            main = Page.objects.get(is_main=True)
            description = main.meta_description
        except Page.DoesNotExist:
            return {'template': 'empty.html'}

    context.update({
        'template': template,
        'description': description
    })

    return context

@register.inclusion_tag('dummy.html', takes_context=True)
def keywords(context, template='menu/metakeywords.html'):
    """Вывод метатега keywords
        Логика проста: выбираем метатег из
        - промежуточного хранилища в сеттингах
        - текущего элемента структуры
        - из главной страницы (которая должна хранить метатеги по-умолчанию)
    """

    try:
        request = context['request']
    except KeyError:
        return {'template': 'empty.html'}

    keywords = XendorSettings().get('meta_keywords')

    if not keywords:
        current_url = XendorSettings().get('activated_node') or request.get_full_path().split('?')[0]
        current_node = Structure().tree.get_element_by_url(current_url)
        if current_node:
            keywords = current_node.meta_keywords
        else:
            keywords = Structure().tree.meta_keywords
    if not keywords:
        try:
            main = Page.objects.get(is_main=True)
            keywords = main.meta_keywords
        except Page.DoesNotExist:
            return {'template': 'empty.html'}

    context.update({
        'template': template,
        'keywords': keywords
    })

    return context


@register.filter
@stringfilter
def xthumbnail(value, arg):
    """Делает тумбочку вписываемую в параметры
        использование {{ item.image|xdp_thumbnail:'200x300' }}"""
    
    return thumbnail(value, arg)

    try:
        return thumbnail(value, arg)
    except: return ''

@register.inclusion_tag('tags/insert-get-parameter.html', takes_context=True)
def insert_get_parameter(context, value, name_get_parameter='page', exclude_vars=''):
    """мегаполезная шняга: формирует ссцыль для постранички, не трогает остальные get-параметры если они есть"""

    exclude_vars = exclude_vars.split(',')
    context.update({
        'page_string': '?' + '&'.join(reduce(lambda q, h: h[0] not in exclude_vars and q.append(unicode(h[0]) + '=' + unicode(h[1])) or q,
                (lambda d, p:
                    d.update({name_get_parameter: p}) or d
                )(dict(context['request'].GET.items()), value).items(), []))
    })
    return context



@register.simple_tag
def admin_image_upload_js():
    return """
<!-- The template to display files available for upload -->
<script id="template-upload" type="text/x-tmpl">
{% for (var i=0, file; file=o.files[i]; i++) { %}
    <tr class="template-upload fade">
        <td class="preview"><span class="fade"></span></td>
        <td class="name"><span>{%=file.name%}</span></td>
        <td class="size"><span>{%=o.formatFileSize(file.size)%}</span></td>
        {% if (file.error) { %}
            <td class="error" colspan="2"><span class="label label-important">{%=locale.fileupload.error%}</span> {%=locale.fileupload.errors[file.error] || file.error%}</td>
        {% } else if (o.files.valid && !i) { %}
            <td>
                <div class="progress progress-success progress-striped active"><div class="bar" style="width:0%;"></div></div>
            </td>
            <td class="start">{% if (!o.options.autoUpload) { %}
                <button class="btn btn-success">
                    <i class="icon-upload icon-white"></i>
                    <span>{%=locale.fileupload.start%}</span>
                </button>
            {% } %}</td>
        {% } else { %}
            <td colspan="2"></td>
        {% } %}
        <td class="cancel">{% if (!i) { %}
            <button class="btn btn-warning">
                <i class="icon-ban-circle icon-white"></i>
                <span>{%=locale.fileupload.cancel%}</span>
            </button>
        {% } %}</td>
    </tr>
{% } %}
</script>
<!-- The template to display files available for download -->
<script id="template-download" type="text/x-tmpl">
{% for (var i=0, file; file=o.files[i]; i++) { %}
    <tr class="template-download fade">
        {% if (file.error) { %}
            <td></td>
            <td class="name"><span>{%=file.name%}</span></td>
            <td class="size"><span>{%=o.formatFileSize(file.size)%}</span></td>
            <td class="error" colspan="2"><span class="label label-important">{%=locale.fileupload.error%}</span> {%=locale.fileupload.errors[file.error] || file.error%}</td>
        {% } else { %}
            <td class="preview">{% if (file.thumbnail_url) { %}
                <a href="{%=file.url%}" title="{%=file.name%}" rel="gallery" download="{%=file.name%}"><img src="{%=file.thumbnail_url%}"></a>
            {% } %}</td>
            <td class="name">
                <a href="{%=file.url%}" title="{%=file.name%}" rel="{%=file.thumbnail_url&&'gallery'%}" download="{%=file.name%}">{%=file.name%}</a>
            </td>
            <td class="size"><span>{%=o.formatFileSize(file.size)%}</span></td>
            <td colspan="2"></td>
        {% } %}
        <td class="delete">
            <button class="btn btn-danger" data-type="{%=file.delete_type%}" data-url="{%=file.delete_url%}">
                <i class="icon-trash icon-white"></i>
                <span>{%=locale.fileupload.destroy%}</span>
            </button>
            <input type="checkbox" name="delete" value="1">
        </td>
    </tr>
{% } %}
</script>
"""

@register.inclusion_tag('tags/setting.html')
def get_setting(name):
    """Получает переменную из настроек сайта и выводит аз ис в шаблон"""

    value = XendorSettings().get(name)

    if value:
        return {'value': value}

    return {'value': ''}

@register.filter
@stringfilter
def get_2_page_link_by_id(id):
    try:
        return Page.objects.get(pk=id).get_absolute_url()
    except Page.DoesNotExist:
        return '#'

@register.inclusion_tag('tags/page_content.html')
def get_page_content_by_id(id):
    try:
        return {'page' : Page.objects.get(pk=int(id))}
    except Page.DoesNotExist:
        return {}

def _formater_1000(value):
    """Форматирование больших чисел в более читабельный вид"""

    try:
        return (lambda h, q:
                (lambda s:
                 ''.join(reversed([' ' * int(not((i + 1) % 3) and i != 0) + s[len(s) - i - 1] for i in xrange(len(s))]))
                    )(h) + ('.' + str(round(float('.' + q), 2)).split('.')[1]) * int(bool(int(q)))
            )(*str(value).split('.'))
    except:
        return value

@register.filter
@stringfilter
def x1000_filter(value):
    """Форматирует число добавляя пробелы для лучшей читабельности"""

    return _formater_1000(value)