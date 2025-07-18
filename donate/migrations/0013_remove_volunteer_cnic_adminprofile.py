# Generated by Django 5.0.3 on 2025-07-09 11:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donate', '0012_beneficiary_father_name_beneficiary_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='volunteer',
            name='Cnic',
        ),
        migrations.CreateModel(
            name='Adminprofile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact', models.CharField(max_length=50, null=True)),
                ('address', models.CharField(max_length=150, null=True)),
                ('adminpic', models.FileField(null=True, upload_to='')),
                ('regdate', models.DateField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
