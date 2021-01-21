# Generated by Django 3.1.4 on 2021-01-11 20:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0005_auto_20210104_1848'),
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MoneyTransfer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.CharField(default=None, max_length=150)),
                ('destination_account_number', models.IntegerField()),
                ('amount_to_be_transferred', models.IntegerField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AlterModelOptions(
            name='transaction',
            options={'ordering': ['-timestamp']},
        ),
        migrations.AlterField(
            model_name='transaction',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transaction', to='authentication.userbankaccount'),
        ),
    ]
