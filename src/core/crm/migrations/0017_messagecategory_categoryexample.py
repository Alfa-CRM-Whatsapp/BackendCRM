# Generated migration for MessageCategory and CategoryExample models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0016_templatesubmission'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('color', models.CharField(default='#6c757d', max_length=7)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_message_categories', to=settings.AUTH_USER_MODEL)),
                ('whatsapp_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message_categories', to='crm.whatsappnumber')),
            ],
            options={
                'verbose_name': 'Message Category',
                'verbose_name_plural': 'Message Categories',
                'unique_together': {('whatsapp_number', 'name')},
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='CategoryExample',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='Exemplo de mensagem que representa esta categoria')),
                ('is_positive', models.BooleanField(default=True, help_text='Se este exemplo representa positivamente a categoria')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('added_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='added_category_examples', to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='examples', to='crm.messagecategory')),
            ],
            options={
                'verbose_name': 'Category Example',
                'verbose_name_plural': 'Category Examples',
            },
        ),
        migrations.AddField(
            model_name='whatsappmessage',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='messages', to='crm.messagecategory'),
        ),
        migrations.AddField(
            model_name='whatsappmessage',
            name='category_confidence',
            field=models.FloatField(blank=True, help_text='Confidence score of the categorization (0.0 to 1.0)', null=True),
        ),
    ]