import json

from django.contrib import admin
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import path

from app.modules.navs.models import Link, Menu


class LinkInline(admin.TabularInline):
    model = Link
    extra = 1

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'action_buttons']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ['name']}
    inlines = [LinkInline]

    @admin.display(description='Actions')
    def action_buttons(self, object):
        return render_to_string('admin/partials/buttons.html', {'object': object, 'opts': self.opts})

@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ['title', 'menu', 'parent', 'url', 'is_active']
    list_filter = ['menu__name', 'is_active']
    search_fields = ['title']
    ordering = ['order']

    class Media:
        css = {'all': [
            'admin/navs/css/vendor/jquery-ui.min.css',
            'admin/navs/css/sortable.css',
        ]}
        js = [
            'admin/navs/js/vendor/jquery-ui.min.js',
            'admin/navs/js/sortable.js',
        ]

    def get_urls(self):
        urls = super().get_urls()
        return [
            path('order/', self.update_order, name='app.modules.navs:links.order'),
        ] + urls
    
    def update_order(self, request):
        if request.method != 'POST':
            return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
        
        try:
            data = json.loads(request.body)
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
