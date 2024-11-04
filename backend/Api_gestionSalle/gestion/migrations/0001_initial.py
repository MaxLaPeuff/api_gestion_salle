# Generated by Django 5.1 on 2024-11-02 20:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Entite",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nom", models.CharField(max_length=100)),
                ("filiere", models.CharField(max_length=100)),
                ("anne_etude", models.CharField(max_length=10)),
                ("effectif", models.IntegerField()),
                ("heure_debut", models.TimeField()),
                ("heure_fin", models.TimeField()),
                ("priorite", models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name="Salle",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nom", models.CharField(max_length=100)),
                ("capacite_max", models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="Attribution",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date_attribution", models.DateTimeField(auto_now_add=True)),
                (
                    "statut",
                    models.CharField(
                        choices=[("actif", "Actif"), ("archive", "Archivé")],
                        default="actif",
                        max_length=50,
                    ),
                ),
                (
                    "entite",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attributions",
                        to="gestion.entite",
                    ),
                ),
                (
                    "salle",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attributions",
                        to="gestion.salle",
                    ),
                ),
            ],
            options={
                "ordering": ["date_attribution"],
                "unique_together": {("entite", "salle")},
            },
        ),
    ]
