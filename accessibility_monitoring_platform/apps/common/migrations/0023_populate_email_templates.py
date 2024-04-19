# Generated by Django 5.0.4 on 2024-04-19 13:58

from django.db import migrations

TWELVE_WEEK_UPDATE_REQUEST: str = """Dear <b>[NAMED CONTACT]</b>,
<br>
<br>
We emailed you an accessibility report on
{% if case.report_sent_date %}
    {{ case.report_sent_date|amp_date }}
{% else %}
    <b>[DATE]</b>
{% endif %}
with a deadline of
{% if case.report_followup_week_12_due_date %}
    {{ case.report_followup_week_12_due_date|amp_date }}
{% else %}
    <b>[DATE]</b>
{% endif %}
to review the accessibility of
{% if case.home_page_url %}
    <a href="{{ case.home_page_url }}">{{ case.home_page_url }}</a>
{% else %}
    <b>[HOME PAGE URL]</b>
{% endif %}
and fix any issues.
<br>
<br>
You must now provide an update on the progress you have made.
<br>
<br>
<h2 class="amp-margin-bottom-0">What you need to do</h2>
Please provide an update on each issue raised in the accessibility report including:
<ul>
    <li>Issues you have fixed</li>
    <li>Issues you have been unable to fix</li>
    <li>A timeline for fixing unresolved issues</li>
    <li>Any other comments about the accessibility of your website</li>
</ul>
The issues found in the report have been listed below.
You do not need to provide information from your own audit.
<br>
<br>
{% if case.audit.unfixed_check_results %}
    Please provide these by filling in the last column of the below tables
    and provide an update on the Accessibility statement.
    <br>
    <br>
    {% for issues_table in issues_tables %}
    {% if issues_table.rows %}
    <h2>{{ issues_table.page }}{% if issues_table.page.page_type != 'pdf' %} page{% endif %} issues</h2>
    <table id="email-issues-table-{{ forloop.counter }}">
    <thead>
    <tr>
    <th width=1%>#</th>
    <th id="issue-{{ forloop.counter }}" width=33%>Issue and description</th>
    <th id="where-found-{{ forloop.counter }}" width=33%>Where the issue was found</th>
    <th id="12-week-update-{{ forloop.counter }}" width=33%>12-week update</th>
    </tr>
    </thead>
    <tbody>
    {% for row in issues_table.rows %}
    <tr valign="top">
    <td width=1%>{{ forloop.counter }}</td>
    <td headers="issue-{{ forloop.parentloop.counter }}" width=33%>{{ row.cell_content_1|markdown_to_html }}</td>
    <td headers="where-found-{{ forloop.parentloop.counter }}" width=33%>{{ row.cell_content_2|markdown_to_html }}</td>
    <td headers="12-week-update-{{ forloop.parentloop.counter }}" width=33%></td>
    </tr>
    {% endfor %}
    </tbody>
    </table>
    {% endif %}
    {% endfor %}
{% else %}
    We found no major issues.
{% endif %}
<h2>Accessibility statement comments</h2>
{% if case.audit.uses_statement_checks %}
    {% if case.audit.failed_statement_check_results %}
    An accessibility statement for the website was found
    but we found the following issues.
    <br>
    <br>
    <table id="email-statement-issues-table">
    <thead>
    <tr>
    <th width=4%>#</th>
    <th id="statement-issue" width=48%>Issue and description</th>
    <th id="statement-12-week-update" width=48%>12-week update</th>
    </tr>
    </thead>
    <tbody>
    {% for statement_check_result in case.audit.failed_statement_check_results %}
    <tr valign="top">
    <td width=4%>{{ forloop.counter }}</td>
    <td headers="statement-issue" width=48%>
    {{ statement_check_result.statement_check.report_text }}
    {% if statement_check_result.report_comment %}
    <br>
    <br>
    {{ statement_check_result.report_comment }}
    {% endif %}
    </td>
    <td headers="statement-12-week-update" width=48%></td>
    </tr>
    {% endfor %}
    </tbody>
    </table>
    {% elif case.audit.accessibility_statement_found and case.audit.statement_check_result_statement_found %}
    An accessibility statement for the website was found in the correct format.
    {% else %}
    An accessibility statement for the website was not found.
    {% endif %}
{% else %}
    {{ case.audit.get_archive_accessibility_statement_state_display }}
    <br>
    <br>
    {% if case.audit.archive_accessibility_statement_state == 'found-but' %}
    <ul>
    {% for issue in case.audit.report_accessibility_issues %}
    <li>{{ issue }}</li>
    {% endfor %}
    </ul>
    {% endif %}
{% endif %}
<br>
<br>
Please provide the update within 7 days.
<br>
<br>
We will retest parts of your website to check that they meet the
accessibility regulations.
<br>
<br>
Any remaining accessibility issues will be passed to the
{% if case.enforcement_body == 'ehrc' %}
    Equality and Human Rights Commission (EHRC)
{% else %}
    Equality Commission for Northern Ireland (ECNI)
{% endif %}
for further action and a list of websites without correct
accessibility statements will be published by the Cabinet Office.
<br>
<br>"""
EQUALITY_BODY_RETEST: str = """<h1 class="amp-margin-bottom-0">{% if case.website_name %}{{ case.website_name }}{% else %}{{ case.organisation_name }}{% endif %}</h1>
{{ case.domain }}
<br>
<br>
Case started: {{ case.created|amp_date }}
<br>
Report published: {{ case.report.latest_s3_report.created|amp_date }}
<br>
Case sent to Equality body: {{ case.sent_to_enforcement_body_sent_date|amp_date }}
<br>
Most recent retest: {{ case.retests.first.date_of_retest|amp_date }}
<br>
<br>
<h2 class="amp-margin-bottom-0">Overview</h2>
<ul>
    <li>
    Retest results:
    <ul>
    {% for retest_page in retest.retestpage_set.all %}
    <li>
    {{ retest_page.page }}{% if retest_page.page.page_type != 'pdf' %} page{% endif %}
    ({{ retest_page.unfixed_check_results.count }} of {{ retest_page.original_check_results.count }}
    issue{% if retest_page.original_check_results.count != 1 %}s{% endif %} remaining)
    </li>
    {% endfor %}
    </ul>
    </li>
</ul>
<br>
<h2 class="amp-margin-bottom-0">Pages we retested</h2>
<table id="pages-table">
    <thead>
    <tr>
    <td id="page-name" width=50%>Page name</td>
    <td id="page-url" width=50%>URL</td>
    </tr>
    </thead>
    <tbody>
    {% for retest_page in retest.retestpage_set.all %}
    <tr valign="top">
    <td headers="page-name" width=50%>{{ retest_page.page }}</td>
    <td headers="page-url" width=50%>
    <a href="{{ retest_page.page.url }}">{{ retest_page.page.url }}</a>
    </td>
    </tr>
    {% endfor %}
    </tbody>
</table>
<br>
<h2 class="amp-margin-bottom-0">Correspondence</h2>
<br>
{% if case.report_sent_date %}
    Report sent {{ case.report_sent_date|amp_date }}
    <br>
    <br>
{% endif %}
{% if case.report_followup_week_1_sent_date %}
    1-week follow-up sent {{ case.report_followup_week_1_sent_date|amp_date }}
    <br>
    <br>
{% endif %}
{% if case.report_followup_week_4_sent_date %}
    4-week follow-up sent {{ case.report_followup_week_4_sent_date|amp_date }}
    <br>
    <br>
{% endif %}
{% if case.report_acknowledged_date %}
    Report acknowledged {{ case.report_acknowledged_date|amp_date }}
    <br>
    <br>
{% endif %}
{% if case.twelve_week_update_requested_date %}
    12-week update request sent {{ case.twelve_week_update_requested_date|amp_date }}
    <br>
    <br>
{% endif %}
{% if case.twelve_week_1_week_chaser_sent_date %}
    12-week update follow-up request sent {{ case.twelve_week_1_week_chaser_sent_date|amp_date }}
    <br>
    <br>
{% endif %}
{% if case.twelve_week_correspondence_acknowledged_date %}
    12-week update follow-up request acknowledged {{ case.twelve_week_correspondence_acknowledged_date|amp_date }}
    <br>
    <br>
{% endif %}
<h2 class="amp-margin-bottom-0">Errors found in retest</h2>
<br>
{% for retest_page in retest.retestpage_set.all %}
    <b>{{ retest_page.page }}{% if retest_page.page.page_type != 'pdf' %} page{% endif %} issues</b>
    ({{ retest_page.unfixed_check_results.count }} issue{% if retest_page.unfixed_check_results.count != 1 %}s{% endif %} remaining)
    <br>
    <a href="{{ retest_page.page.url }}">{{ retest_page.page.url }}</a>
    <br>
    <br>
    {% if retest_page.missing_date %}
    This page has been removed by the organisation.
    <br>
    <br>
    {% else %}
    <table id="email-issues-table-{{ forloop.counter }}">
    <thead>
    <tr>
    <td width=1%>#</td>
    <td id="issue-{{ forloop.counter }}" width=33%>Issue and description</td>
    <td id="where-found-{{ forloop.counter }}" width=33%>Where the issue was found</td>
    <td id="retest-update-{{ forloop.counter }}" width=33%>Retest outcome</td>
    </tr>
    </thead>
    <tbody>
    {% for retest_check_result in retest_page.original_check_results %}
    <tr valign="top">
    <td width=1%>{{ forloop.counter }}</td>
    <td headers="issue-{{ forloop.parentloop.counter }}" width=33%>
    {% if retest_check_result.check_result.wcag_definition.url_on_w3 %}
    <a href="{{ retest_check_result.check_result.wcag_definition.url_on_w3 }}">
    {{ retest_check_result.check_result.wcag_definition.name }}</a>
    {% else %}
    {{ retest_check_result.check_result.wcag_definition.name }}
    {% endif %}
    <br>
    <br>
    {{ retest_check_result.check_result.wcag_definition.description|markdown_to_html }}
    <br>
    {{ retest_check_result.check_result.wcag_definition.report_boilerplate|markdown_to_html }}
    </td>
    <td headers="where-found-{{ forloop.parentloop.counter }}" width=33%>
    {{ retest_check_result.check_result.notes|markdown_to_html }}
    </td>
    <td headers="retest-update-{{ forloop.parentloop.counter }}" width=33%>
    {% if retest_check_result.latest_retest_check_result %}
    {{ retest_check_result.latest_retest_check_result.get_retest_state_display }}
    <br>
    <br>
    {{ retest_check_result.latest_retest_check_result.retest_notes|markdown_to_html }}
    {% else %}
    Fixed in a previous retest
    {% endif %}
    </td>
    </tr>
    {% endfor %}
    </tbody>
    </table>
    <b>Additional issues found</b>
    {% if retest_page.additional_issues_notes %}
    {{ retest_page.additional_issues_notes|markdown_to_html }}
    {% else %}
    <br>
    <br>
    None
    <br>
    <br>
    {% endif %}
    {% endif %}
{% endfor %}
<h2 class="amp-margin-bottom-0">Statement assessment</h2>
<br>
The statement in the most recent retest was: {{ retest.get_statement_compliance_state_display }}.
<br>
<br>
Disproportionate burden was: {{ retest.get_disproportionate_burden_claim_display }}.
<br>
<br>
{% if retest.disproportionate_burden_notes %}
    Notes regarding the disproportionate burden:
    <br>
    <br>
    {{ retest.disproportionate_burden_notes|markdown_to_html }}
    <br>
    <br>
{% endif %}
{% if retest.failed_statement_check_results %}
    <b>Issues found with the statement</b>
    <br>
    <table id="email-statement-issues-table">
    <thead>
    <tr>
    <td width=1%>#</td>
    <td id="statement-issue-{{ forloop.counter }}" width=99%>Issue</td>
    </tr>
    </thead>
    <tbody>
    {% for failed_statement_check_result in retest.failed_statement_check_results %}
    <tr valign="top">
    <td width=1%>{{ forloop.counter }}</td>
    <td headers="statement-issue-{{ forloop.parentloop.counter }}" width=99%>
    {{ failed_statement_check_result.statement_check.report_text }}
    {% if failed_statement_check_result.comment %}
    <br>
    <br>
    {{ failed_statement_check_result.comment|markdown_to_html }}
    {% endif %}
    </td>
    </tr>
    {% endfor %}
    </tbody>
    </table>
{% endif %}"""
OUTSTANDING_ISSUES: str = """Dear <b>[NAMED CONTACT]</b>,
<br>
<br>
We have completed the retest and some issues are still outstanding.
Please review the issues listed below and provide an update.
<br>
<br>
{% if case.audit.unfixed_check_results %}
    {% for issues_table in issues_tables %}
    {% if issues_table.rows %}
    <h2>{{ issues_table.page }}{% if issues_table.page.page_type != 'pdf' %} page{% endif %} issues</h2>
    <a href="{{ issues_table.page.url }}">{{ issues_table.page.url }}</a>
    <br>
    <br>
    <table id="email-issues-table-{{ forloop.counter }}">
    <thead>
    <tr>
    <th width=1%>#</th>
    <th id="issue-{{ forloop.counter }}" width=33%>Issue and description</th>
    <th id="where-found-{{ forloop.counter }}" width=33%>Where the issue was found</th>
    <th id="12-week-update-{{ forloop.counter }}" width=33%>Organisation 12-week update</th>
    </tr>
    </thead>
    <tbody>
    {% for row in issues_table.rows %}
    <tr valign="top">
    <td width=1%>{{ forloop.counter }}</td>
    <td headers="issue-{{ forloop.parentloop.counter }}" width=33%>{{ row.cell_content_1|markdown_to_html }}</td>
    <td headers="where-found-{{ forloop.parentloop.counter }}" width=33%>{{ row.cell_content_2|markdown_to_html }}</td>
    <td headers="12-week-update-{{ forloop.parentloop.counter }}" width=33%></td>
    </tr>
    {% endfor %}
    </tbody>
    </table>
    {% endif %}
    {% endfor %}
{% else %}
    We found no major issues.
{% endif %}
<h2>Your statement</h2>
{% if case.audit.uses_statement_checks %}
    {% if case.audit.outstanding_statement_check_results %}
    <table id="email-statement-issues-table">
    <thead>
    <tr>
    <th width=1%>#</th>
    <th id="statement-issue" width=49%>Issue</th>
    <th id="statement-12-week-update" width=49%>Organisation 12-week update</th>
    </tr>
    </thead>
    <tbody>
    {% for statement_check_result in case.audit.outstanding_statement_check_results %}
    <tr valign="top">
    <td width=1%>{{ forloop.counter }}</td>
    <td headers="statement-issue" width=49%>
    <p>{{ statement_check_result.statement_check.report_text }}</p>
    {{ statement_check_result.report_comment|markdown_to_html }}
    </td>
    <td headers="statement-12-week-update" width=49%>
    {{ statement_check_result.retest_comment|markdown_to_html }}
    </td>
    </tr>
    {% endfor %}
    </tbody>
    </table>
    {% else %}
    We found no major issues.
    {% endif %}
{% else %}
    {{ case.audit.get_archive_accessibility_statement_state_display }}
    {% if case.audit.archive_accessibility_statement_state == 'found-but' %}
    <ul>
    {% for issue in case.audit.report_accessibility_issues %}
    <li>{{ issue }}</li>
    {% endfor %}
    </ul>
    {% endif %}
{% endif %}
<br>
<br>"""


def populate_email_templates(apps, schema_editor):  # pylint: disable=unused-argument
    EmailTemplate = apps.get_model("common", "EmailTemplate")
    EmailTemplate.objects.create(
        name="12-week update request",
        type="12-week-request",
        template=TWELVE_WEEK_UPDATE_REQUEST,
    )
    EmailTemplate.objects.create(
        name="Outstanding issues",
        type="outstanding-issues",
        template=OUTSTANDING_ISSUES,
    )
    EmailTemplate.objects.create(
        name="Equality body retest",
        type="equality-body-retest",
        template=EQUALITY_BODY_RETEST,
    )


def reverse_code(apps, schema_editor):  # pylint: disable=unused-argument
    EmailTemplate = apps.get_model("common", "EmailTemplate")
    EmailTemplate.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0022_emailtemplate"),
    ]

    operations = [
        migrations.RunPython(populate_email_templates, reverse_code=reverse_code),
    ]
