import json

from django.contrib import admin
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import path
from django.utils.translation import gettext_lazy as _

from app.modules.navs.forms import (
    LinkForm,
    PageLinkForm,
    RouteLinkForm,
    URLLinkForm
)
from app.modules.navs.models import Link, Menu


class LinkInline(admin.TabularInline):
    model  = Link
    extra  = 1
    fields = ['title', 'menu', 'parent', 'url', 'url_name']


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display  = ['name', 'slug', 'description', 'action_buttons']
    sortable_by   = ['name', 'slug']
    search_fields = ['name', 'slug', 'description']
    actions       = ['active_selected', 'delete_selected']

    prepopulated_fields = {'slug': ['name']}
    inlines   = [LinkInline]
    fieldsets = [
        (_('General'), {'fields': ['name', 'slug', 'description']}),
        (_('Options'), {'fields': ['is_active'], 'classes': ['collapse']}),
    ]

    class Media:
        css = {'all': [
            'admin/css/vendor/jquery-ui/jquery-ui.min.css',
            'admin/navs/css/navs.css',
        ]}
        js = [
            'admin/js/vendor/jquery-ui/jquery-ui.min.js',
            'admin/js/jquery.init.js',
            'admin/navs/js/navs.js',
        ]

    def changelist_view(self, request, extra_context = None):
        self._http_request = request
        return super().changelist_view(request, extra_context)
    
    def get_action(self, action):
        action = super().get_action(action)
        if 'delete_selected' in action:
            action    = list(action)
            action[2] = f'Delete {self.opts.verbose_name_plural.capitalize()}'

        return action if type(action) is tuple else tuple(action)
    
    @admin.action(permissions=['change'], description=_('Mark as Active'))
    def active_selected(self, request, queryset):
        queryset.update(is_active=True)

    @admin.display(description=_('Actions'))
    def action_buttons(self, object):
        request = getattr(self, '_http_request', None)
        perms   = self.get_model_perms(request)
        
        return render_to_string('admin/navs/menu/actions_field.html', {
            'opts'  : self.opts,
            'object': object,
            'perms' : {
                'has_add_permission'   : perms.get('add'),
                'has_view_permission'  : perms.get('view'),
                'has_change_permission': perms.get('change'),
                'has_delete_permission': perms.get('delete'),
            },
        })


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display  = ['title', 'menu', 'parent', 'link_type', 'is_active']
    list_editable = ['menu', 'parent', 'is_active']
    list_filter   = ['menu__slug', 'is_active']
    search_fields = ['title', 'menu__name']
    sortable_by   = ['title', 'menu__name']
    ordering      = ['order']

    class Media:
        css = {'all': [
            'admin/css/vendor/jquery-ui/jquery-ui.min.css',
            'admin/navs/css/navs.css',
            'admin/navs/css/sortable.css',
            'admin/navs/css/link-form.css',
            'admin/navs/css/link-modal.css',
        ]}
        js = [
            'admin/js/vendor/jquery-ui/jquery-ui.min.js',
            'admin/js/jquery.init.js',
            'admin/navs/js/navs.js',
            'admin/navs/js/sortable.js',
            'admin/navs/js/link-form.js',
            'admin/navs/js/link-modal.js',
        ]

    def get_urls(self):
        urls = super().get_urls()
        return [
            path('order/', self.change_order_view, name='navs_link_order'),
        ] + urls
    
    @classmethod
    def get_preserved_params(self, request):
        params  = {}
        filters = request.GET.get('_changelist_filters')
        if filters:
            for pair in filters.split('&'):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    key = key.replace('__', '_')
                    params[key] = value
        return params

    def changelist_view(self, request, extra_context = {}):
        params = self.get_preserved_params(request)
        menu_slug = params.get('menu_slug') or request.GET.get('menu__slug')

        if menu_slug:
            extra_context['menu_slug'] = menu_slug
            extra_context['title'] = f'Links for {menu_slug.capitalize()}'
        
        return super().changelist_view(request, extra_context)
    
    def get_form(self, request, obj=None, **kwargs):
        params = self.get_preserved_params(request)
        menu_slug = params.get('menu_slug') or request.GET.get('menu__slug')
        link_type = params.get('link_type') or request.GET.get('link_type')
        
        # If editing an existing link, detect type from object
        if obj and not link_type:
            if obj.page:
                link_type = 'page'
            elif obj.url_name:
                link_type = 'url_name'
            else:
                link_type = 'url'
        
       # Select appropriate form based on link type
        if link_type == 'page':
            self.form = PageLinkForm
        elif link_type == 'url_name':
            self.form = RouteLinkForm
        elif link_type == 'url':
            self.form = URLLinkForm
        else:
            self.form = LinkForm

        # Pre-populate and hide menu field when adding via slug
        form = super().get_form(request, obj, **kwargs)

        if menu_slug and not obj:
            try:
                menu = Menu.objects.get(slug=menu_slug)
                form.base_fields['menu'].initial = menu.pk
                # form.base_fields['menu'].widget = forms.HiddenInput()
                form.base_fields['menu'].widget.attrs['readonly'] = True
                form.base_fields['menu'].disabled = True
            except Menu.DoesNotExist:
                pass
        
        return form

    def get_fieldsets(self, request, obj=None):
        params = self.get_preserved_params(request)
        link_type = params.get('link_type') or request.GET.get('link_type')
        
        if obj and not link_type:
            if obj.page:
                link_type = 'page'
            elif obj.url_name:
                link_type = 'url_name'
            else:
                link_type = 'url'
        
        if link_type == 'page':
            return [
                (_('General'), {'fields': ['menu', 'title', 'page']}),
                (_('Options'), {'fields': ['parent', 'target', 'icon', 'classes', 'permission', 'is_active'], 'classes': ['collapse']}),
            ]
        elif link_type == 'url_name':
            return [
                (_('General'), {'fields': ['menu', 'title', 'url_name']}),
                (_('Options'), {'fields': ['parent', 'target', 'icon', 'classes', 'permission', 'is_active'], 'classes': ['collapse']}),
            ]
        elif link_type == 'url':
            return [
                (_('General'), {'fields': ['menu', 'title', 'url']}),
                (_('Options'), {'fields': ['parent', 'target', 'icon', 'classes', 'permission', 'is_active'], 'classes': ['collapse']}),
            ]
        else:
            return [
                (_('General'), {'fields': ['menu', 'title', 'link_type', 'page', 'url_name', 'url']}),
                (_('Options'), {'fields': ['parent', 'target', 'icon', 'classes', 'permission', 'is_active'], 'classes': ['collapse']}),
            ]
    
    @admin.display(description=_('Type'))
    def link_type(self, obj):
        if obj.page:
            return f'Page: {obj.page.title}'
        elif obj.url_name:
            return f'Route: {obj.url_name}'
        elif obj.url:
            return f'URL: {obj.url}'
        return '—'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        params   = self.get_preserved_params(request)
        slug     = params.get('menu_slug') or request.GET.get('menu__slug')
        
        if slug:
            queryset = queryset.filter(menu__slug=slug)
        
        return queryset

    def change_order_view(self, request):
        if request.method != 'POST':
            return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
        
        try:
            data  = json.loads(request.body)
            items = data.get('items', [])
            
            if not items:
                return JsonResponse({'status': 'error', 'message': 'No items provided'}, status=400)
            
            for item in items:
                Link.objects.filter(pk=item.get('id')).update(order=item.get('order'))
            
            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': f'Invalid JSON: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
