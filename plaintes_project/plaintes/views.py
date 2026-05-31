from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone

from .models import Plainte, Categorie, Action, Notification, ProfilUtilisateur
from .forms import (
    InscriptionForm, PlainteForm, PlainteUpdateForm,
    ActionForm, CategorieForm, ProfilForm, UserUpdateForm
)


def get_user_role(user):
    try:
        return user.profil.role
    except ProfilUtilisateur.DoesNotExist:
        return 'citoyen'


def is_staff_user(user):
    return get_user_role(user) in ['employe', 'responsable', 'administrateur']


def is_responsable(user):
    return get_user_role(user) in ['responsable', 'administrateur']


def is_admin(user):
    return get_user_role(user) == 'administrateur'


# ─── Auth ────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = AuthenticationForm(data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('dashboard')
    return render(request, 'plaintes/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def inscription_view(request):
    form = InscriptionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Compte créé avec succès ! Bienvenue.")
        return redirect('dashboard')
    return render(request, 'plaintes/inscription.html', {'form': form})


# ─── Dashboard ───────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    role = get_user_role(request.user)
    notifs = Notification.objects.filter(destinataire=request.user, lue=False)

    if role == 'citoyen':
        plaintes = Plainte.objects.filter(citoyen=request.user)
        stats = {
            'total': plaintes.count(),
            'en_cours': plaintes.filter(statut='en_cours').count(),
            'resolues': plaintes.filter(statut='resolue').count(),
            'fermees': plaintes.filter(statut='fermee').count(),
        }
        return render(request, 'plaintes/dashboard_citoyen.html', {
            'plaintes': plaintes[:5], 'stats': stats, 'notifs': notifs
        })

    # Staff / Responsable / Admin
    all_plaintes = Plainte.objects.all()
    stats = {
        'total': all_plaintes.count(),
        'en_cours': all_plaintes.filter(statut='en_cours').count(),
        'resolues': all_plaintes.filter(statut='resolue').count(),
        'fermees': all_plaintes.filter(statut='fermee').count(),
        'urgentes': all_plaintes.filter(priorite='urgente').count(),
    }
    recentes = all_plaintes[:10]
    par_categorie = Categorie.objects.annotate(nb=Count('plainte')).order_by('-nb')

    return render(request, 'plaintes/dashboard_staff.html', {
        'plaintes': recentes, 'stats': stats,
        'par_categorie': par_categorie, 'notifs': notifs, 'role': role
    })


# ─── Plaintes ────────────────────────────────────────────────────────────────

@login_required
def liste_plaintes(request):
    role = get_user_role(request.user)
    if role == 'citoyen':
        qs = Plainte.objects.filter(citoyen=request.user)
    else:
        qs = Plainte.objects.all()

    # Filtres
    statut = request.GET.get('statut')
    priorite = request.GET.get('priorite')
    categorie = request.GET.get('categorie')
    q = request.GET.get('q')

    if statut:
        qs = qs.filter(statut=statut)
    if priorite:
        qs = qs.filter(priorite=priorite)
    if categorie:
        qs = qs.filter(categorie_id=categorie)
    if q:
        qs = qs.filter(Q(titre__icontains=q) | Q(description__icontains=q))

    categories = Categorie.objects.all()
    return render(request, 'plaintes/liste_plaintes.html', {
        'plaintes': qs,
        'categories': categories,
        'statut_choices': Plainte.STATUT_CHOICES,
        'priorite_choices': Plainte.PRIORITE_CHOICES,
        'role': role,
    })


@login_required
def soumettre_plainte(request):
    form = PlainteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        plainte = form.save(commit=False)
        plainte.citoyen = request.user
        plainte.save()
        messages.success(request, "Votre plainte a été soumise avec succès.")
        return redirect('detail_plainte', pk=plainte.pk)
    return render(request, 'plaintes/soumettre_plainte.html', {'form': form})


@login_required
def detail_plainte(request, pk):
    plainte = get_object_or_404(Plainte, pk=pk)
    role = get_user_role(request.user)

    # Marquer les notifs comme lues
    Notification.objects.filter(destinataire=request.user, plainte=plainte, lue=False).update(lue=True)

    can_edit = is_staff_user(request.user)
    can_add_action = is_staff_user(request.user)

    action_form = ActionForm()
    update_form = None

    if can_edit:
        update_form = PlainteUpdateForm(instance=plainte)

    if request.method == 'POST':
        if 'add_action' in request.POST and can_add_action:
            action_form = ActionForm(request.POST)
            if action_form.is_valid():
                action = action_form.save(commit=False)
                action.plainte = plainte
                action.auteur = request.user
                action.save()
                # Notifier le citoyen
                Notification.objects.create(
                    destinataire=plainte.citoyen,
                    plainte=plainte,
                    message=f"Une action a été ajoutée à votre plainte #{plainte.pk}: {action.description[:80]}"
                )
                messages.success(request, "Action ajoutée.")
                return redirect('detail_plainte', pk=pk)

        elif 'update_plainte' in request.POST and can_edit:
            update_form = PlainteUpdateForm(request.POST, instance=plainte)
            if update_form.is_valid():
                old_statut = plainte.statut
                plainte = update_form.save()
                if old_statut != plainte.statut:
                    Notification.objects.create(
                        destinataire=plainte.citoyen,
                        plainte=plainte,
                        message=f"Le statut de votre plainte #{plainte.pk} a changé : {plainte.get_statut_display()}"
                    )
                messages.success(request, "Plainte mise à jour.")
                return redirect('detail_plainte', pk=pk)

    return render(request, 'plaintes/detail_plainte.html', {
        'plainte': plainte,
        'actions': plainte.actions.all(),
        'action_form': action_form,
        'update_form': update_form,
        'can_edit': can_edit,
        'can_add_action': can_add_action,
        'role': role,
    })


@login_required
def supprimer_plainte(request, pk):
    plainte = get_object_or_404(Plainte, pk=pk)
    role = get_user_role(request.user)
    if plainte.citoyen != request.user and not is_admin(request.user):
        messages.error(request, "Accès refusé.")
        return redirect('liste_plaintes')
    if request.method == 'POST':
        plainte.delete()
        messages.success(request, "Plainte supprimée.")
        return redirect('liste_plaintes')
    return render(request, 'plaintes/confirmer_suppression.html', {'plainte': plainte})


# ─── Catégories ──────────────────────────────────────────────────────────────

@login_required
def liste_categories(request):
    if not is_admin(request.user):
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('dashboard')
    categories = Categorie.objects.annotate(nb=Count('plainte')).order_by('nom')
    return render(request, 'plaintes/categories.html', {'categories': categories})


@login_required
def creer_categorie(request):
    if not is_admin(request.user):
        return redirect('dashboard')
    form = CategorieForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Catégorie créée.")
        return redirect('liste_categories')
    return render(request, 'plaintes/form_categorie.html', {'form': form, 'titre': 'Nouvelle catégorie'})


@login_required
def modifier_categorie(request, pk):
    if not is_admin(request.user):
        return redirect('dashboard')
    cat = get_object_or_404(Categorie, pk=pk)
    form = CategorieForm(request.POST or None, instance=cat)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Catégorie modifiée.")
        return redirect('liste_categories')
    return render(request, 'plaintes/form_categorie.html', {'form': form, 'titre': 'Modifier la catégorie'})


# ─── Utilisateurs ────────────────────────────────────────────────────────────

@login_required
def liste_utilisateurs(request):
    if not is_admin(request.user):
        return redirect('dashboard')
    users = User.objects.select_related('profil').all()
    return render(request, 'plaintes/utilisateurs.html', {'users': users})


@login_required
def changer_role(request, user_id):
    if not is_admin(request.user):
        return redirect('dashboard')
    target = get_object_or_404(User, pk=user_id)
    profil, _ = ProfilUtilisateur.objects.get_or_create(user=target)
    if request.method == 'POST':
        role = request.POST.get('role')
        if role in dict(ProfilUtilisateur.ROLE_CHOICES):
            profil.role = role
            profil.save()
            messages.success(request, f"Rôle de {target.username} mis à jour.")
    return redirect('liste_utilisateurs')


# ─── Notifications ───────────────────────────────────────────────────────────

@login_required
def notifications(request):
    notifs = Notification.objects.filter(destinataire=request.user)
    notifs.filter(lue=False).update(lue=True)
    return render(request, 'plaintes/notifications.html', {'notifs': notifs})


# ─── Profil ──────────────────────────────────────────────────────────────────

@login_required
def mon_profil(request):
    profil, _ = ProfilUtilisateur.objects.get_or_create(user=request.user, defaults={'role': 'citoyen'})
    user_form = UserUpdateForm(instance=request.user)
    profil_form = ProfilForm(instance=profil)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profil_form = ProfilForm(request.POST, instance=profil)
        if user_form.is_valid() and profil_form.is_valid():
            user_form.save()
            profil_form.save()
            messages.success(request, "Profil mis à jour.")
            return redirect('mon_profil')

    return render(request, 'plaintes/profil.html', {
        'user_form': user_form, 'profil_form': profil_form, 'profil': profil
    })


# ─── Historique ──────────────────────────────────────────────────────────────

@login_required
def historique(request):
    role = get_user_role(request.user)
    if role == 'citoyen':
        plaintes = Plainte.objects.filter(citoyen=request.user).prefetch_related('actions')
    else:
        plaintes = Plainte.objects.all().prefetch_related('actions')
    return render(request, 'plaintes/historique.html', {'plaintes': plaintes, 'role': role})
