from django import forms
from django.utils.translation import gettext_lazy as _

from app.modules.navs.models import Link, Menu
from app.modules.pages.models import Page


class BaseLinkForm(forms.ModelForm):

    class Meta:
        model   = Link
        fields  = ['menu', 'title', 'parent', 'target', 'icon', 'classes', 'permission', 'is_active']
        widgets = {
            'menu'      : forms.Select(attrs={'class': 'form-control vTextField'}),
            'title'     : forms.TextInput(attrs={'class': 'form-control vTextField', 'maxlength': 150, 'placeholder': _('Title')}),
            'parent'    : forms.Select(attrs={'class': 'form-control vTextField'}),
            'target'    : forms.Select(attrs={'class': 'form-control vTextField'}),
            'icon'      : forms.TextInput(attrs={'class': 'form-control vTextField', 'maxlength': 150, 'placeholder': 'Example: fa fa-link'}),
            'classes'   : forms.TextInput(attrs={'class': 'form-control vTextField', 'maxlength': 255, 'placeholder': _('Example: form-control')}),
            'permission': forms.TextInput(attrs={'class': 'form-control vTextField', 'maxlength': 150, 'placeholder': _('Permission Name')}),
            'is_active' : forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['permission'].required = False
        self.fields['icon'].required = False
        self.fields['classes'].required = False
        self.fields['parent'].required = False
        self.fields['is_active'].label = _('Mark as Active')


class PageLinkForm(BaseLinkForm):

    class Meta(BaseLinkForm.Meta):
        fields  = ['menu', 'title', 'page', 'parent', 'target', 'icon', 'classes', 'permission', 'is_active']
        widgets = {
            **BaseLinkForm.Meta.widgets,
            'page': forms.Select(attrs={'class': 'form-control vTextField', 'required': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['page'].required = True
        self.fields['page'].label = _('Page')
        self.fields['page'].queryset = Page.objects.filter(is_enabled=True) # Filter only active pages

    def clean(self):
        cleaned_data = super().clean()
        page = cleaned_data.get('page')
        
        if not page:
            raise forms.ValidationError(_('Please select a page.'))
        
        return cleaned_data

    def save(self, commit=True):
        link = super().save(commit=False)
        link.url_name = ''
        link.url = ''
        
        if commit:
            link.save()
        return link


class RouteLinkForm(BaseLinkForm):

    class Meta(BaseLinkForm.Meta):
        fields  = ['menu', 'title', 'url_name', 'parent', 'target', 'icon', 'classes', 'permission', 'is_active']
        widgets = {
            **BaseLinkForm.Meta.widgets,
            'url_name': forms.TextInput(attrs={
                'class': 'form-control vTextField',
                'maxlength': 255,
                'placeholder': 'Example: app.modules.pages:pages.home',
                'required': True
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['url_name'].required = True
        self.fields['url_name'].label = _('Route')
        self.fields['url_name'].help_text = _('The name of a route pattern.')

    def clean(self):
        cleaned_data = super().clean()
        url_name = cleaned_data.get('url_name')
        
        if not url_name:
            raise forms.ValidationError(_('Please enter a route name.'))
        
        return cleaned_data

    def save(self, commit=True):
        link = super().save(commit=False)
        link.page = None
        link.url = ''
        
        if commit:
            link.save()
        return link


class URLLinkForm(BaseLinkForm):
    
    class Meta(BaseLinkForm.Meta):
        fields  = ['menu', 'title', 'url', 'parent', 'target', 'icon', 'classes', 'permission', 'is_active']
        widgets = {
            **BaseLinkForm.Meta.widgets,
            'url': forms.URLInput(attrs={
                'class': 'form-control vTextField',
                'maxlength': 255,
                'placeholder': 'Example: about/company',
                'required': True
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['url'].required = True
        self.fields['url'].label = _('URL')
        self.fields['url'].help_text = _('Enter a URL. If you enter a URI path, the site domain will be prepended automatically.')

    def clean(self):
        cleaned_data = super().clean()
        url = cleaned_data.get('url')
        
        if not url:
            raise forms.ValidationError(_('Please enter a custom URL.'))
        
        return cleaned_data

    def save(self, commit=True):
        link = super().save(commit=False)
        link.page = None
        link.url_name = ''
        
        if commit:
            link.save()
        return link


class LinkForm(forms.ModelForm):
    """Legacy form for backward compatibility - auto-detects type"""
    
    link_type = forms.ChoiceField(
        choices=[
            ('page', _('Page')),
            ('url_name', _('Route')),
            ('url', _('URL')),
        ],
        required=True,
        widget=forms.RadioSelect,
        label=_('Link Type'),
    )

    class Meta:
        model   = Link
        fields  = ['menu', 'title', 'link_type', 'page', 'url_name', 'url', 'parent', 'target', 'icon', 'classes', 'permission', 'is_active']
        widgets = {
            'menu'      : forms.Select(attrs={'class': 'form-control vTextField'}),
            'title'     : forms.TextInput(attrs={'class': 'form-control vTextField', 'maxlength': 150, 'placeholder': _('Title')}),
            'page'      : forms.Select(attrs={'class': 'form-control vTextField'}),
            'url_name'  : forms.TextInput(attrs={'class': 'form-control vTextField', 'maxlength': 255, 'placeholder': 'Example: app.modules.pages:pages.home'}),
            'url'       : forms.TextInput(attrs={'class': 'form-control vTextField', 'maxlength': 255, 'placeholder': 'Example: about/company'}),
            'parent'    : forms.Select(attrs={'class': 'form-control vTextField'}),
            'target'    : forms.Select(attrs={'class': 'form-control vTextField'}),
            'icon'      : forms.TextInput(attrs={'class': 'form-control vTextField', 'maxlength': 150, 'placeholder': 'Example: fa fa-link'}),
            'classes'   : forms.TextInput(attrs={'class': 'form-control vTextField', 'maxlength': 255, 'placeholder': _('Example: form-control')}),
            'permission': forms.TextInput(attrs={'class': 'form-control vTextField', 'maxlength': 150, 'placeholder': _('Permission Name')}),
            'is_active' : forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_active'].label = _('Mark as Active')
        
        if self.instance and self.instance.pk:
            if self.instance.page:
                self.fields['link_type'].initial = 'page'
            elif self.instance.url_name:
                self.fields['link_type'].initial = 'url_name'
            else:
                self.fields['link_type'].initial = 'url'
        else:
            self.fields['link_type'].initial = 'url'

    def clean(self):
        cleaned_data = super().clean()
        link_type = cleaned_data.get('link_type')
        page = cleaned_data.get('page')
        url_name = cleaned_data.get('url_name')
        url = cleaned_data.get('url')

        if link_type == 'page' and not page:
            raise forms.ValidationError(_('Please select a page.'))
        elif link_type == 'url_name' and not url_name:
            raise forms.ValidationError(_('Please enter a route name.'))
        elif link_type == 'url' and not url:
            raise forms.ValidationError(_('Please enter a custom URL.'))

        return cleaned_data

    def save(self, commit=True):
        link = super().save(commit=False)
        link_type = self.cleaned_data.get('link_type')

        if link_type == 'page':
            link.url_name = ''
            link.url = ''

        if link_type == 'url_name':
            link.page = None
            link.url = ''

        if link_type == 'url':
            link.page = None
            link.url_name = ''

        if commit:
            link.save()
        return link
