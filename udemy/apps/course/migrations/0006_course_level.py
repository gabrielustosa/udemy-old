# Generated by Django 4.1.2 on 2022-11-16 01:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0005_remove_courserelation_unique course relation_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='level',
            field=models.TextField(default='beginner', verbose_name='Course Level'),
            preserve_default=False,
        ),
    ]
