from django.db import models
from mhc.storage_backend import PrivateUnconvertedStorage, PrivateJsonStorage

class HH(models.Model):
    file = models.FileField(storage=PrivateUnconvertedStorage())
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
      ordering = ["-uploaded_at"]

    def __str__(self):
        return self.file.name

class HHJson(models.Model):
    hh          = models.ForeignKey('HH', null=True, on_delete=models.SET_NULL)
    file        = models.FileField(storage=PrivateJsonStorage())

class Player(models.Model):
    name        = models.CharField(max_length=63)

class Game(models.Model):
    name        = models.CharField(max_length=63)

class HH_Player(models.Model):
    hh          = models.ForeignKey('HH', null=True, on_delete=models.SET_NULL)
    player      = models.ForeignKey('Player', null=True, on_delete=models.SET_NULL)

class HH_Player_Game(models.Model):
    hh_player   = models.ForeignKey('HH_Player', null=True, on_delete=models.SET_NULL)
    game        = models.ForeignKey('Game', null=True, on_delete=models.SET_NULL)
    amount      = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    count       = models.IntegerField(default=0)
    sit         = models.IntegerField(default=0)

class Hand(models.Model):
    hh          = models.ForeignKey('HH', null=True, on_delete=models.SET_NULL)
    game        = models.ForeignKey('Game', null=True, on_delete=models.SET_NULL)
    hand_number = models.CharField(max_length=31)
    date_played = models.CharField(max_length=31)
    time_played = models.CharField(max_length=31)
    sb          = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    bb          = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    ante        = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    table       = models.CharField(max_length=63)
    blind_type  = models.CharField(max_length=63)
    rake        = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    pot         = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    sitting     = models.IntegerField(default=0)
    dealt       = models.IntegerField(default=0)
    body        = models.TextField()

class Hand_Player(models.Model):
    hand        = models.ForeignKey('Hand', null=True, on_delete=models.SET_NULL)
    player      = models.ForeignKey('Player', null=True, on_delete=models.SET_NULL)
    amount      = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    sitting     = models.BooleanField()
