# Generated by Django 4.1.13 on 2024-07-24 09:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('Session_Topic', models.CharField(max_length=100)),
                ('Date', models.DateField()),
                ('Start_Time', models.CharField(max_length=20)),
                ('conductedby', models.CharField(max_length=50)),
                ('meetlink', models.URLField()),
                ('Colleges', models.JSONField(default=list)),
                ('Branches', models.JSONField(default=list)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stuId', models.CharField(max_length=10)),
                ('stuname', models.CharField(max_length=100)),
                ('gender', models.CharField(max_length=10)),
                ('age', models.CharField(max_length=3)),
                ('branch', models.CharField(max_length=100)),
                ('collegeName', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students', to='meetsessions.session')),
            ],
        ),
    ]
