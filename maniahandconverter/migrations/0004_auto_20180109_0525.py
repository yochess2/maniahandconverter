# Generated by Django 2.0 on 2018-01-09 05:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('maniahandconverter', '0003_hand_hand_player'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hand',
            name='game',
        ),
        migrations.RemoveField(
            model_name='hand',
            name='hh',
        ),
        migrations.RemoveField(
            model_name='hand_player',
            name='hand',
        ),
        migrations.RemoveField(
            model_name='hand_player',
            name='player',
        ),
        migrations.DeleteModel(
            name='Hand',
        ),
        migrations.DeleteModel(
            name='Hand_Player',
        ),
    ]
