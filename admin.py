import json

from django.contrib import admin
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import path
from django.utils.translation import gettext_lazy as _

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
            'admin/navs/css/vendor/jquery-ui.min.css',
            'admin/navs/css/navs.css',
        ]}
        js = [
            'admin/navs/js/vendor/jquery-ui.min.js',
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
    list_display  = ['title', 'menu', 'parent', 'url', 'is_active']
    list_editable = ['menu', 'parent', 'url', 'is_active']
    list_filter   = ['menu__slug', 'is_active']
    search_fields = ['title', 'menu__name']
    sortable_by   = ['title', 'menu__name']
    ordering      = ['order']

    fieldsets = [
        (_('General'), {'fields': ['menu', 'title', 'url', 'url_name']}),
        (_('Options'), {'fields': ['parent', 'target', 'icon', 'classes', 'permission', 'is_active'], 'classes': ['collapse']}),
    ]

    class Media:
        css = {'all': [
            'admin/navs/css/vendor/jquery-ui.min.css',
            'admin/navs/css/navs.css',
            'admin/navs/css/sortable.css',
        ]}
        js = [
            'admin/navs/js/vendor/jquery-ui.min.js',
            'admin/js/jquery.init.js',
            'admin/navs/js/navs.js',
            'admin/navs/js/sortable.js',
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
        slug   = params.get('menu_slug')

        if slug:
            extra_context['menu_slug'] = slug
            extra_context['title'] = f'Links for {slug}'
        
        return super().changelist_view(request, extra_context)
    
    def get_form(self, request, obj=None, **kwargs):
        form   = super().get_form(request, obj, **kwargs)
        params = self.get_preserved_params(request)
        slug   = params.get('menu_slug')

        # Pre-populate and hide menu field when adding via slug
        if slug and not obj:
            try:
                from django import forms

                menu = Menu.objects.get(slug=slug)
                form.base_fields['menu'].initial = menu.pk
                # form.base_fields['menu'].widget = forms.HiddenInput()
                form.base_fields['menu'].widget.attrs['readonly'] = True
                form.base_fields['menu'].disabled = True
            except Menu.DoesNotExist:
                pass
        
        return form
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        params   = self.get_preserved_params(request)
        slug     = params.get('menu_slug')
        
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
