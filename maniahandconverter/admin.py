from django.contrib import admin

from .models import (
    HHManager,
    HH,
    HHJson,
    Player,
    Game,
    HHJson_Player,
    HHJson_Player_Game,
    HHNew,
    HHManager
)

class HHJson_Player_GameInline(admin.TabularInline):
    model = HHJson_Player_Game

class HHJson_PlayerInline(admin.TabularInline):
    model = HHJson_Player

# Register your models here.
@admin.register(HH)
class HHAdmin(admin.ModelAdmin):
    list_display = ('uploaded_at','name','path','active')
    readonly_fields = ('path','size','uploaded','uploaded_at','file_type')
    list_filter = ('active',)
    fieldsets = [
        (None, {
            'fields': ('uploaded_at','name','uploaded')
        }),
        ('File Details', {
            'fields': ('path',('size','file_type'),)
        }),
        ('Active', {
            'fields': ('active',)
        })
    ]

    def get_queryset(self, request):
        return self.model._base_manager.get_queryset()

@admin.register(HHJson)
class HHJsonAdmin(admin.ModelAdmin):
    list_display = ('uploaded_at','file','hh')
    inlines = [HHJson_PlayerInline]

@admin.register(HHNew)
class HHNewAdmin(admin.ModelAdmin):
    list_display = ('uploaded_at','hero','file','hh_json')
    list_filter = ('hero',)

@admin.register(HHJson_Player)
class HHJson_PlayerAdmin(admin.ModelAdmin):
    inlines = [HHJson_Player_GameInline]
    list_filter = ('player','hh_json')
