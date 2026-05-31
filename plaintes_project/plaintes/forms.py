from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Plainte, Action, Categorie, ProfilUtilisateur


class InscriptionForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True, label="Prénom")
    last_name = forms.CharField(max_length=50, required=True, label="Nom")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            ProfilUtilisateur.objects.create(user=user, role='citoyen')
        return user


class PlainteForm(forms.ModelForm):
    class Meta:
        model = Plainte
        fields = ['titre', 'categorie', 'description', 'localisation']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de la plainte'}),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Décrivez votre problème...'}),
            'localisation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adresse ou lieu concerné'}),
        }


class PlainteUpdateForm(forms.ModelForm):
    class Meta:
        model = Plainte
        fields = ['titre', 'categorie', 'description', 'localisation', 'statut', 'priorite', 'responsable']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'localisation': forms.TextInput(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'priorite': forms.Select(attrs={'class': 'form-select'}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['responsable'].queryset = User.objects.filter(
            profil__role__in=['responsable', 'employe', 'administrateur']
        )
        self.fields['responsable'].required = False


class ActionForm(forms.ModelForm):
    class Meta:
        model = Action
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': "Décrivez l'action entreprise..."
            }),
        }
        labels = {'description': "Description de l'action"}


class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom', 'type', 'description']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ProfilForm(forms.ModelForm):
    class Meta:
        model = ProfilUtilisateur
        fields = ['telephone', 'adresse']
        widgets = {
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
