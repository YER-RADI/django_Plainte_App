from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.login_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('inscription/', views.inscription_view, name='inscription'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Plaintes
    path('plaintes/', views.liste_plaintes, name='liste_plaintes'),
    path('plaintes/soumettre/', views.soumettre_plainte, name='soumettre_plainte'),
    path('plaintes/<int:pk>/', views.detail_plainte, name='detail_plainte'),
    path('plaintes/<int:pk>/supprimer/', views.supprimer_plainte, name='supprimer_plainte'),

    # Catégories
    path('categories/', views.liste_categories, name='liste_categories'),
    path('categories/creer/', views.creer_categorie, name='creer_categorie'),
    path('categories/<int:pk>/modifier/', views.modifier_categorie, name='modifier_categorie'),

    # Utilisateurs
    path('utilisateurs/', views.liste_utilisateurs, name='liste_utilisateurs'),
    path('utilisateurs/<int:user_id>/role/', views.changer_role, name='changer_role'),

    # Notifications
    path('notifications/', views.notifications, name='notifications'),

    # Profil
    path('profil/', views.mon_profil, name='mon_profil'),

    # Historique
    path('historique/', views.historique, name='historique'),
]
