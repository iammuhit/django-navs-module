import json

from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from django.views.decorators.http import require_POST

from app.modules.navs.models import Link, Menu


class LinkInline(admin.TabularInline):
    model = Link
    extra = 1

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    prepopulated_fields = {'slug': ['name']}
    inlines = [LinkInline]

@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'menu', 'parent', 'url', 'is_active')
    list_filter = ('menu', 'is_active')
    list_editable = []
    ordering = ('order',)
    search_fields = ('title',)

    class Media:
        css = {'all': [
            'admin/css/vendor/jquery-ui.min.css',
            'admin/css/sortable.css',
        ]}
        js = [
            'admin/js/vendor/jquery-ui.min.js',
            'admin/js/sortable.js',
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
