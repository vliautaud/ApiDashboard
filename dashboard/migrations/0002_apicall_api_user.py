# Generated by Django 2.1.3 on 2018-11-15 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='apicall',
            name='api_user',
            field=models.CharField(max_length=50, null=True, verbose_name='UserName'),
        ),
    ]
