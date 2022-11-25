# Generated by Django 4.1.2 on 2022-11-22 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lesson', '0004_remove_lessonrelation_user_lessonrelation_created_and_more'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='lessonrelation',
            constraint=models.UniqueConstraint(fields=('creator', 'lesson'), name='unique lesson relation'),
        ),
    ]
