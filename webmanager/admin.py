from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Place, Person, ConnectedPlace


class ConnectedPlaceInline(admin.TabularInline):
    model = ConnectedPlace
    fk_name = 'connected_place'


class PersonInline(admin.StackedInline):
	model = Person
	can_delete = False
	verbose_name_plural = 'profiles'

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'person',)
    inlines = (PersonInline,)


class InlinePersonAdmin(admin.TabularInline):
    model = Person
    ordering = ['name']


class PlaceAdmin(admin.ModelAdmin):
    ordering = ['name']
    list_display = ('name', 'zip_code')
    inlines = [InlinePersonAdmin, ConnectedPlaceInline]

class PersonAdmin(admin.ModelAdmin):
	model = Person

class ConnectedPlaceAdmin(admin.ModelAdmin):
    model = ConnectedPlace

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Place, PlaceAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(ConnectedPlace, ConnectedPlaceAdmin)
