from django.contrib import admin
from .models import Plainte, Categorie, Action, Notification, ProfilUtilisateur


@admin.register(ProfilUtilisateur)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'telephone']
    list_filter = ['role']


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'description']
    search_fields = ['nom']


class ActionInline(admin.TabularInline):
    model = Action
    extra = 0
    readonly_fields = ['auteur', 'date']


@admin.register(Plainte)
class PlainteAdmin(admin.ModelAdmin):
    list_display = ['pk', 'titre', 'citoyen', 'categorie', 'statut', 'priorite', 'date_soumission']
    list_filter = ['statut', 'priorite', 'categorie']
    search_fields = ['titre', 'description', 'citoyen__username']
    inlines = [ActionInline]
    readonly_fields = ['date_soumission', 'date_mise_a_jour']


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ['plainte', 'auteur', 'date']
    readonly_fields = ['date']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['destinataire', 'plainte', 'lue', 'date']
    list_filter = ['lue']
