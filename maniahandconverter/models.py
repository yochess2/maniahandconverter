from django.db import models
from mhc.storage_backend import JsonStorage, ConvertedStorage

class HHManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(active=True)

class HH(models.Model):
    name         = models.CharField(max_length=120, null=True, blank=True)
    file_type    = models.CharField(max_length=120, null=True, blank=True)
    path         = models.TextField(blank=True, null=True)
    size         = models.BigIntegerField(default=0)
    uploaded     = models.BooleanField(default=False)
    active       = models.BooleanField(default=True)
    uploaded_at  = models.DateTimeField(auto_now_add=True)
    active_items = HHManager()

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.name

class HHJson(models.Model):
    hh          = models.ForeignKey('HH', null=True, on_delete=models.SET_NULL)
    file        = models.FileField(storage=JsonStorage())
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

class Player(models.Model):
    name        = models.CharField(max_length=63)

class Game(models.Model):
    name        = models.CharField(max_length=63)

class HHJson_Player(models.Model):
    hh_json     = models.ForeignKey('HHJson', null=True, on_delete=models.SET_NULL)
    player      = models.ForeignKey('Player', null=True, on_delete=models.SET_NULL)

class HHJson_Player_Game(models.Model):
    hh_json_player   = models.ForeignKey('HHJson_Player', null=True, on_delete=models.SET_NULL)
    game             = models.ForeignKey('Game', null=True, on_delete=models.SET_NULL)
    amount           = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    count            = models.IntegerField(default=0)
    sit              = models.IntegerField(default=0)

class HHNew(models.Model):
    hh_json     = models.ForeignKey('HHJson', null=True, on_delete=models.SET_NULL)
    file        = models.FileField(storage=ConvertedStorage())
    hero        = models.CharField(max_length=63)
