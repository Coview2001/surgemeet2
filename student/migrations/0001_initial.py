# Generated by Django 4.1.13 on 2024-07-24 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('stuId', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('stuname', models.CharField(max_length=100)),
                ('gender', models.CharField(max_length=10)),
                ('age', models.IntegerField()),
                ('branch', models.CharField(max_length=100)),
                ('collegeName', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
    ]
