# Generated by Django 4.0 on 2021-12-31 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='author_name',
            field=models.CharField(default='Author', max_length=255),
            preserve_default=False,
        ),
    ]