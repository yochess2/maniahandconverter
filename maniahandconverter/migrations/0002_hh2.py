# Generated by Django 2.0 on 2018-01-07 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maniahandconverter', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HH2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='asdf/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
