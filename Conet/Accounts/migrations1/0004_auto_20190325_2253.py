# Generated by Django 2.1.7 on 2019-03-26 04:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0003_auto_20190325_2252'),
    ]

    operations = [
        migrations.RenameField(
            model_name='node',
            old_name='account',
            new_name='authAccount',
        ),
    ]