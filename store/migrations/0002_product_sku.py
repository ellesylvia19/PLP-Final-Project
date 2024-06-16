

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='sku',
            field=models.CharField(default=1, max_length=255, unique=True, verbose_name='Unique Product ID (SKU)'),
            preserve_default=False,
        ),
    ]
