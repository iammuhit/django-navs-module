from django.db import models
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext_lazy as _

from app.modules.navs import DB_TABLE_PREFIX


class Menu(models.Model):
    name        = models.CharField(max_length=150, unique=True)
    slug        = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = DB_TABLE_PREFIX + 'menus'
        verbose_name = _('menu')
        verbose_name_plural = _('menus')
        ordering = ['name']

    def __str__(self):
        return self.name


class Link(models.Model):
    TARGET_CHOICES = (
        ('_self', 'Open in the Same Tab'),
        ('_blank', 'Open in a New Tab'),
    )

    menu       = models.ForeignKey(Menu, related_name='links', on_delete=models.CASCADE)
    parent     = models.ForeignKey('self', related_name='children', null=True, blank=True, on_delete=models.CASCADE)
    title      = models.CharField(max_length=150)
    url        = models.CharField(max_length=255, blank=True)
    url_name   = models.CharField(max_length=255, blank=True)
    icon       = models.CharField(max_length=150, blank=True)
    order      = models.PositiveIntegerField(default=0)
    target     = models.CharField(max_length=25, choices=TARGET_CHOICES, blank=True)
    classes    = models.CharField(max_length=255, blank=True)
    permission = models.CharField(max_length=150, blank=True)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = DB_TABLE_PREFIX + 'links'
        verbose_name = _('link')
        verbose_name_plural = _('links')
        ordering = ['order']

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        if self.url_name:
            try:
                return reverse(self.url_name)
            except NoReverseMatch:
                return '#'
        return self.url
