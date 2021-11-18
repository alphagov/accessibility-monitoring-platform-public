# Generated by Django 3.2.8 on 2021-11-18 09:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cases', '0018_case_testing_methodology'),
    ]

    operations = [
        migrations.CreateModel(
            name='Audit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.IntegerField(default=0)),
                ('is_deleted', models.BooleanField(default=False)),
                ('date_of_test', models.DateTimeField(blank=True, null=True)),
                ('description', models.TextField(blank=True, default='')),
                ('screen_size', models.CharField(choices=[('15in', '15 inch'), ('13in', '13 inch')], default='15in', max_length=20)),
                ('is_exemption', models.CharField(choices=[('yes', 'Yes'), ('no', 'No'), ('unknown', 'Unknown')], default='unknown', max_length=20)),
                ('notes', models.TextField(blank=True, default='')),
                ('type', models.CharField(choices=[('initial', 'Initial'), ('eq-retest', 'Equality body retest')], default='initial', max_length=20)),
                ('audit_metadata_complete_date', models.DateField(blank=True, null=True)),
                ('audit_pages_complete_date', models.DateField(blank=True, null=True)),
                ('audit_manual_complete_date', models.DateField(blank=True, null=True)),
                ('audit_axe_complete_date', models.DateField(blank=True, null=True)),
                ('audit_pdf_complete_date', models.DateField(blank=True, null=True)),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='audit_case', to='cases.case')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='WcagDefinition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('axe', 'Axe'), ('manual', 'Manual'), ('pdf', 'PDF')], default='pdf', max_length=20)),
                ('sub_type', models.CharField(choices=[('additional', 'Additional'), ('audio-visual', 'Audio and Visual'), ('keyboard', 'Keyboard'), ('other', 'Other'), ('pdf', 'PDF'), ('zoom', 'Zoom and Reflow'), ('relationship', 'Relationship'), ('navigation', 'Navigation'), ('presentation', 'Presentation'), ('aria', 'ARIA'), ('timing', 'Timing'), ('nontext', 'Non-text'), ('language', 'Language')], default='other', max_length=20)),
                ('name', models.TextField(blank=True, default='')),
                ('description', models.TextField(blank=True, default='')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.IntegerField(default=0)),
                ('is_deleted', models.BooleanField(default=False)),
                ('type', models.CharField(choices=[('extra', 'Page'), ('home', 'Home page'), ('contact', 'Contact page'), ('statement', 'Accessibility statement'), ('pdf', 'PDF'), ('form', 'A form')], default='extra', max_length=20)),
                ('name', models.TextField(blank=True, default='')),
                ('url', models.TextField(blank=True, default='')),
                ('not_found', models.CharField(choices=[('no', 'No'), ('yes', 'Yes')], default='no', max_length=20)),
                ('manual_checks_complete_date', models.DateField(blank=True, null=True)),
                ('axe_checks_complete_date', models.DateField(blank=True, null=True)),
                ('audit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='page_audit', to='audits.audit')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='CheckResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.IntegerField(default=0)),
                ('is_deleted', models.BooleanField(default=False)),
                ('type', models.CharField(choices=[('axe', 'Axe'), ('manual', 'Manual'), ('pdf', 'PDF')], default='pdf', max_length=20)),
                ('failed', models.CharField(choices=[('no', 'No'), ('yes', 'Yes')], default='no', max_length=20)),
                ('notes', models.TextField(blank=True, default='')),
                ('audit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checkresult_audit', to='audits.audit')),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checkresult_page', to='audits.page')),
                ('wcag_definition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checkresult_wcagdefinition', to='audits.wcagdefinition')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='audit',
            name='next_page',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='audit_next_page', to='audits.page'),
        ),
    ]
