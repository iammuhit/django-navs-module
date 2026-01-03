from django.contrib import admin

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
    list_display = ('title', 'menu', 'parent', 'order', 'is_active')
    list_filter = ('menu', 'is_active')
    search_fields = ('title',)
