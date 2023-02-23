# Generated by Django 4.1.7 on 2023-02-23 09:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RootModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='RootEntity',
            fields=[
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('rootentity_rootmodel_ptr', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='example_one.rootmodel')),
            ],
            bases=('example_one.rootmodel',),
        ),
        migrations.CreateModel(
            name='StatementTemporalisationMixin',
            fields=[
                ('statement_start', models.CharField(blank=True, max_length=100, null=True, verbose_name='start_date_written')),
                ('statement_end', models.CharField(blank=True, max_length=100, null=True, verbose_name='end_date_written')),
                ('statement_temproalistaion_mixin_rootmodel_ptr', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='example_one.rootmodel')),
            ],
            bases=('example_one.rootmodel',),
        ),
        migrations.CreateModel(
            name='TempMixin',
            fields=[
                ('start_date_written', models.CharField(blank=True, max_length=100, null=True, verbose_name='start_date_written')),
                ('end_date_written', models.CharField(blank=True, max_length=100, null=True, verbose_name='end_date_written')),
                ('tempmixin_rootmodel_ptr', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='example_one.rootmodel')),
            ],
            bases=('example_one.rootmodel',),
        ),
        migrations.CreateModel(
            name='MixinPerson',
            fields=[
                ('statementtemporalisationmixin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to='example_one.statementtemporalisationmixin')),
                ('tempmixin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to='example_one.tempmixin')),
                ('first_name', models.CharField(max_length=50, null=True, verbose_name='first_name')),
                ('mixinperson_rootentity_ptr', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='example_one.rootentity')),
                ('new_field', models.CharField(blank=True, max_length=200, null=True)),
            ],
            bases=('example_one.tempmixin', 'example_one.statementtemporalisationmixin', 'example_one.rootentity'),
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('first_name', models.CharField(max_length=100, verbose_name='first_name')),
                ('person_rootentity_ptr', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='example_one.rootentity')),
            ],
            bases=('example_one.rootentity',),
        ),
        migrations.CreateModel(
            name='TempWork',
            fields=[
                ('tempmixin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to='example_one.tempmixin')),
                ('rootentity_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='example_one.rootentity')),
                ('title', models.CharField(max_length=100, verbose_name='title')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='example_one.mixinperson')),
            ],
            bases=('example_one.rootentity', 'example_one.tempmixin'),
        ),
    ]
