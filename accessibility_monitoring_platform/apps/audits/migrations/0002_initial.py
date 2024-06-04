# Generated by Django 5.0.4 on 2024-06-04 14:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("audits", "0001_initial"),
        ("cases", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="audit",
            name="case",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="audit_case",
                to="cases.case",
            ),
        ),
        migrations.AddField(
            model_name="checkresult",
            name="audit",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="checkresult_audit",
                to="audits.audit",
            ),
        ),
        migrations.AddField(
            model_name="page",
            name="audit",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="page_audit",
                to="audits.audit",
            ),
        ),
        migrations.AddField(
            model_name="checkresult",
            name="page",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="checkresult_page",
                to="audits.page",
            ),
        ),
        migrations.AddField(
            model_name="retest",
            name="case",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="cases.case"
            ),
        ),
        migrations.AddField(
            model_name="retestcheckresult",
            name="check_result",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="audits.checkresult"
            ),
        ),
        migrations.AddField(
            model_name="retestcheckresult",
            name="retest",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="audits.retest"
            ),
        ),
        migrations.AddField(
            model_name="retestpage",
            name="page",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="audits.page"
            ),
        ),
        migrations.AddField(
            model_name="retestpage",
            name="retest",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="audits.retest"
            ),
        ),
        migrations.AddField(
            model_name="retestcheckresult",
            name="retest_page",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="audits.retestpage"
            ),
        ),
        migrations.AddField(
            model_name="reteststatementcheckresult",
            name="retest",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="audits.retest"
            ),
        ),
        migrations.AddField(
            model_name="reteststatementcheckresult",
            name="statement_check",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="audits.statementcheck",
            ),
        ),
        migrations.AddField(
            model_name="statementcheckresult",
            name="audit",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="audits.audit"
            ),
        ),
        migrations.AddField(
            model_name="statementcheckresult",
            name="statement_check",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="audits.statementcheck",
            ),
        ),
        migrations.AddField(
            model_name="statementpage",
            name="audit",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="audits.audit"
            ),
        ),
        migrations.AddField(
            model_name="checkresult",
            name="wcag_definition",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="checkresult_wcagdefinition",
                to="audits.wcagdefinition",
            ),
        ),
    ]
