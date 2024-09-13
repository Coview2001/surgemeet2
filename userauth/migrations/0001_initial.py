# Generated by Django 4.1.13 on 2024-08-30 10:06

from django.db import migrations, models
import djongo.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userID', models.CharField(max_length=100, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('category', models.CharField(default='', max_length=100)),
                ('expiry_date', models.DateField()),
                ('status', models.CharField(max_length=50)),
                ('register_date', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserLogin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('token', djongo.models.fields.JSONField()),
            ],
        ),
    ]
