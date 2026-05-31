from django.db import models
from django.contrib.auth.models import User


class Categorie(models.Model):
    TYPE_CHOICES = [
        ('mairie', 'Mairie'),
        ('entreprise', 'Entreprise'),
        ('service_public', 'Service Public'),
        ('environnement', 'Environnement'),
        ('securite', 'Sécurité'),
        ('autre', 'Autre'),
    ]
 
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='autre')
 
    def __str__(self):
        return f"{self.nom} ({self.get_type_display()})"
 
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

class Plainte(models.Model):
    STATUT_CHOICES = [
        ('en_cours', 'En cours'),
        ('resolue', 'Résolue'),
        ('fermee', 'Fermée'),
    ]

    PRIORITE_CHOICES = [
        ('basse', 'Basse'),
        ('normale', 'Normale'),
        ('haute', 'Haute'),
        ('urgente', 'Urgente'),
    ]

    citoyen = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plaintes')
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, blank=True)
    titre = models.CharField(max_length=200)
    description = models.TextField()
    localisation = models.CharField(max_length=255, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_cours')
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES, default='normale')
    responsable = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='plaintes_assignees'
    )
    date_soumission = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"#{self.pk} - {self.titre} ({self.get_statut_display()})"

    class Meta:
        ordering = ['-date_soumission']
        verbose_name = "Plainte"
        verbose_name_plural = "Plaintes"


class Action(models.Model):
    plainte = models.ForeignKey(Plainte, on_delete=models.CASCADE, related_name='actions')
    auteur = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Action sur #{self.plainte.pk} par {self.auteur.username}"

    class Meta:
        ordering = ['date']
        verbose_name = "Action"
        verbose_name_plural = "Actions"


class Notification(models.Model):
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    plainte = models.ForeignKey(Plainte, on_delete=models.CASCADE)
    message = models.TextField()
    lue = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notif pour {self.destinataire.username} - {'Lue' if self.lue else 'Non lue'}"

    class Meta:
        ordering = ['-date']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"


class ProfilUtilisateur(models.Model):
    ROLE_CHOICES = [
        ('citoyen', 'Citoyen'),
        ('employe', 'Employé'),
        ('responsable', 'Responsable'),
        ('administrateur', 'Administrateur'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='citoyen')
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    class Meta:
        verbose_name = "Profil Utilisateur"
        verbose_name_plural = "Profils Utilisateurs"
