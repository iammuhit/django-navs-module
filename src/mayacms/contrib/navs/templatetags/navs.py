from django import template

from mayacms.contrib.navs.models import Menu

register = template.Library()


@register.inclusion_tag('navs/menu.html', takes_context=True)
def nav_menu(context, slug):
    try:
        menu  = Menu.objects.get(slug=slug, is_active=True)
        links = menu.links.filter(parent__isnull=True, is_active=True)
    except Menu.DoesNotExist:
        return {'links': []}
    
    return {'links': links, 'request': context.get('request')}


@register.inclusion_tag('navs/links.html', takes_context=True)
def nav_links(context, links):
    return {'links': links, 'request': context.get('request')}
