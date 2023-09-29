# Generated by Django 4.2.5 on 2023-09-29 00:05

from django.db import migrations
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_product_price_product_price_currency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price',
            field=djmoney.models.fields.MoneyField(decimal_places=2, default_currency='AUD', max_digits=10),
        ),
    ]
