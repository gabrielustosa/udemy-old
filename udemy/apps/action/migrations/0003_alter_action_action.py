# Generated by Django 4.1.2 on 2022-11-07 22:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('action', '0002_alter_action_action'),
    ]

    operations = [
        migrations.AlterField(
            model_name='action',
            name='action',
            field=models.CharField(choices=[(1, 'Like'), (2, 'Dislike')], max_length=2),
        ),
    ]