# Generated by Django 2.1.7 on 2019-03-26 04:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0004_auto_20190325_2253'),
    ]

    operations = [
        migrations.RenameField(
            model_name='node',
            old_name='authAccount',
            new_name='authUser',
        ),
    ]