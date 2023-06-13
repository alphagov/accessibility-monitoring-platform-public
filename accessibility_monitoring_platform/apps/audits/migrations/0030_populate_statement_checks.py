# Generated by Django 4.1.7 on 2023-06-13 10:00

from django.db import migrations

QUESTIONS = [
    {
        "type": "overview",
        "label": "Is there an accessibility page?",
        "success_criteria": "An accessibility page is found on the website",
        "report_text": "No accessibility page or statement was found on the website. You need to write and publish an accessibility statement that meets the required legislative format.",
    },
    {
        "type": "overview",
        "label": "Does the accessibility page include a statement?",
        "success_criteria": "The accessibility page includes some statement wording.",
        "report_text": "The accessibility page does not include an accessibility statement that follows the model accessibility statement template. You need to write and publish an accessibility statement that meets the required legislative format.",
    },
    {
        "type": "website",
        "label": 'Is the page heading "Accessibility statement"?',
        "success_criteria": "The title and main heading is Accessibility Statement or Accessibility Statement for [x]",
        "report_text": 'The title and main heading of the page should be "Accessibility statement" or "Accessibility statement for [name of website]"',
    },
    {
        "type": "website",
        "label": "Is there an accessibility commitment?",
        "success_criteria": "A commitment to make the site accessible is found",
        "report_text": "There is no commitment to make the website accessible, as required in the model accessibility statement.",
    },
    {
        "type": "website",
        "label": "Does the commitment use the correct wording?",
        "success_criteria": "The text is: [Name of organisation] is committed to making its [website(s)/mobile application(s), as appropriate] accessible, in accordance with the Public Sector Bodies (Websites and Mobile Applications) (No. 2) Accessibility Regulations 2018.",
        "report_text": "The wording of the commitment to make the website accessible is incorrect.",
    },
    {
        "type": "website",
        "label": "Is there a scope for the accessibility statement?",
        "success_criteria": "The statement is clear about what it applies to.",
        "report_text": "There is no scope included for the statement or is not clear enough.",
    },
    {
        "type": "website",
        "label": "Is the accessibility statement provided as a web page?",
        "success_criteria": "The statement is a web page.",
        "report_text": "Some users may have accessibility issues reading an accessibility statement that is not a standard HTML web page. It would be beneficial to publish as a web page.",
    },
    {
        "type": "website",
        "label": "Is the accessibility statement prominent on the home page or on every page of the site?",
        "success_criteria": "The statement is not properly linked.",
        "report_text": "Your statement should be prominently placed on the homepage of the website or made available on every web page, for example in a static header or footer, as the regulations require.                                                                                                                                                ",
    },
    {
        "type": "website",
        "label": "Is the statement complete on one page?",
        "success_criteria": "The statement is on one page and is not split over many pages.",
        "report_text": "The statement should be easy to read and navigate. Splitting the statement over multiple pages could mean a user cannot find the information they were looking for.",
    },
    {
        "type": "website",
        "label": "Does the statement cover the entire website?",
        "success_criteria": "The statement covers the entire website, no further accessibility statements are needed.",
        "report_text": "The accessibility statement needs to cover the entire website. Either this statement needs to be extended or an additional statement needs to be published.",
    },
    {
        "type": "compliance",
        "label": "Is there a heading for compliance status?",
        "success_criteria": "There is a heading for compliance status",
        "report_text": 'A heading for "compliance" was not found',
    },
    {
        "type": "compliance",
        "label": "Is the compliance status heading worded correctly?",
        "success_criteria": 'The heading is "compliance"',
        "report_text": 'The heading for "compliance" is not worded correctly',
    },
    {
        "type": "compliance",
        "label": "Is 1 of the 3 compliance status options included?",
        "success_criteria": "A compliance status option is included",
        "report_text": "The statement does not include the compliance status, as required in the model accessibility statement.",
    },
    {
        "type": "compliance",
        "label": "Is the compliance status option correct?",
        "success_criteria": "The status option matches our testing results and is worded correctly",
        "report_text": "The compliance status does not match the results of our testing or is not using the correct wording.",
    },
    {
        "type": "non-accessible",
        "label": "Is there a heading for non-accessible content?",
        "success_criteria": "A heading for non-accessible content is included (if needed)",
        "report_text": 'A heading for "non-accessible" was not found.',
    },
    {
        "type": "non-accessible",
        "label": "Is the non-accessible content heading worded correctly?",
        "success_criteria": 'The heading is "non-accessible"',
        "report_text": 'The heading for "non-accessible" is not worded correctly.',
    },
    {
        "type": "non-accessible",
        "label": "Is any non-compliant content found in the testing listed?",
        "success_criteria": "The issues found are included in the non-compliant content.",
        "report_text": "Known accessibility issues are not included within the 'non-accessible content' section. You need to review your accessibility statement to cover the issues found in this report and any others found during your own audit.",
    },
    {
        "type": "non-accessible",
        "label": "Is non-compliant content correct and complete?",
        "success_criteria": "Non-compliant content is correct and complete.",
        "report_text": "The non-accessible content is not correct or complete.",
    },
    {
        "type": "non-accessible",
        "label": "Is the non-compliant content clear?",
        "success_criteria": "Non-compliant content is clear.",
        "report_text": "The non-accessible content is not clear.",
    },
    {
        "type": "non-accessible",
        "label": "Does the non-compliant content mention the WCAG criteria?",
        "success_criteria": "The non-compliant content mentions the WCAG criteria it fails.",
        "report_text": "The non-accessible content does not say which WCAG criteria it fails.",
    },
    {
        "type": "non-accessible",
        "label": "Does the non-compliant content mention dates for fixes in the past?",
        "success_criteria": "There are no dates in the past for fixes.",
        "report_text": "The non-compliant content includes dates for fixes that are in the past.",
    },
    {
        "type": "non-accessible",
        "label": "Is the scope of disproportionate burden content clear?",
        "success_criteria": "The scope of disproportionate burden content is not clear.",
        "report_text": "The content where disproportionate burden is claimed is not clear or in enough detail.",
    },
    {
        "type": "non-accessible",
        "label": "Is the disproportionate burden assesment provided?",
        "success_criteria": "The disproportionate burden assessment is provided.",
        "report_text": "A disproportionate burden assessment must have been completed before adding a claim to your accessibility statement. You need to send evidence of the assessment to us for review.",
    },
    {
        "type": "non-accessible",
        "label": "Is content listed as being out of scope that should be in another part of the accessibility statement?",
        "success_criteria": "No content is listed as out of scope that should be in another section.",
        "report_text": "Content is included in the out of scope section that should be listed in another part of the statement.",
    },
    {
        "type": "preparation",
        "label": "Is there a heading for preparation of this accessibility statement?",
        "success_criteria": "There is a heading for preparation of this accessibility statement.",
        "report_text": 'A heading for "Preparation of this accessibility statement" was not found.',
    },
    {
        "type": "preparation",
        "label": "Is the statement preparation heading worded correctly?",
        "success_criteria": 'The heading is "preparation"',
        "report_text": 'The heading for "preparation" is not worded correctly.',
    },
    {
        "type": "preparation",
        "label": "Is there a date for the statement preparation?",
        "success_criteria": "There is a date for statement preparation.",
        "report_text": "A statement preparation date was not included.",
    },
    {
        "type": "preparation",
        "label": "Is the statement preparation date worded correctly?",
        "success_criteria": "The statement preparation date is worded correctly.",
        "report_text": "A statement preparation date was included but needs to be worded correctly.",
    },
    {
        "type": "preparation",
        "label": "Is there a date for the last review of the statement?",
        "success_criteria": "There is a date for the last statement review or has been published in the last year.",
        "report_text": "A statement review date was not included.",
    },
    {
        "type": "preparation",
        "label": "Is the the last review date worded correctly?",
        "success_criteria": "The last statement review date is worded correctly.",
        "report_text": "A statement review date was included but needs to be worded correctly.",
    },
    {
        "type": "preparation",
        "label": "Is the statement review or preparation date within the last year?",
        "success_criteria": "The statement has not been reviewed in the last year.",
        "report_text": "The statement has not been reviewed in the last year and is out-of-date.",
    },
    {
        "type": "preparation",
        "label": "Is there information about the method used to prepare the statement?",
        "success_criteria": "The method used to prepare the statement is not included.",
        "report_text": "The statement does not include the method used to prepare the statement.",
    },
    {
        "type": "preparation",
        "label": "Is the method used to prepare the statement descriptive enough?",
        "success_criteria": "The method used to prepare the statement is not descriptive enough.",
        "report_text": "The method used to prepare the statement needs to be more descriptive.",
    },
    {
        "type": "feedback",
        "label": "Is there a heading for feedback and contact information?",
        "success_criteria": "There is a heading for feedback and contact information.",
        "report_text": 'A heading for "Feedback and contact information" was not found.',
    },
    {
        "type": "feedback",
        "label": "Is the feedback and contact information heading worded correctly?",
        "success_criteria": 'The heading is "Feedback and contact information"',
        "report_text": 'The heading for "non-accessible" is not worded correctly.',
    },
    {
        "type": "feedback",
        "label": "Is there contact information for the organisation?",
        "success_criteria": "There is an email address or contact form.",
        "report_text": "There is no contact information to report accessibility issues.",
    },
    {
        "type": "feedback",
        "label": "Is there a heading for enforcement procedure?",
        "success_criteria": "There is a heading for enforcement procedure.",
        "report_text": 'A heading for "Enforcement procedure" is not found.',
    },
    {
        "type": "feedback",
        "label": "Is the heading for enforcement procedure worded correctly?",
        "success_criteria": 'The heading is "Enforcement procedure".',
        "report_text": 'The heading for "Enforcement procedure" is not worded correctly.',
    },
    {
        "type": "feedback",
        "label": "If GB: does the content mention EHRC?",
        "success_criteria": "The content mentions EHRC as the enforcement body.",
        "report_text": "The statement must say that EHRC are responsible for enforcing the regulations.",
    },
    {
        "type": "feedback",
        "label": "If NI: does the content mention ECNI?",
        "success_criteria": "The content mentions ECNI as the enforcement body.",
        "report_text": "The statement must say that ECNI are responsible for enforcing the regulations.",
    },
    {
        "type": "feedback",
        "label": "If GB: is there a link to EASS?",
        "success_criteria": "There is a line about contacting EASS and this is linked.",
        "report_text": "There must be a link to the EASS website for complaints.",
    },
    {
        "type": "feedback",
        "label": "If NI: is there a link to ECNI?",
        "success_criteria": "There is a line about contacting ECNI and this is linked.",
        "report_text": "There must be a link to the ECNI website for complaints.",
    },
]


def populate_statement_checks(apps, schema_editor):  # pylint: disable=unused-argument
    """Populate statement checks"""
    # pylint: disable=invalid-name
    StatementCheck = apps.get_model("audits", "StatementCheck")
    for count, question in enumerate(QUESTIONS, start=1):
        StatementCheck.objects.create(
            type=question["type"],
            label=question["label"],
            success_criteria=question["success_criteria"],
            report_text=question["report_text"],
            position=count,
        )


def remove_statement_checks(apps, schema_editor):  # pylint: disable=unused-argument
    """Delete all statement checks and results to undo change"""
    # pylint: disable=invalid-name
    StatementCheckResult = apps.get_model("audits", "StatementCheckResult")
    for statement_check_result in StatementCheckResult.objects.all():
        statement_check_result.delete()
    StatementCheck = apps.get_model("audits", "StatementCheck")
    for statement_check in StatementCheck.objects.all():
        statement_check.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("audits", "0029_statementcheck_and_more"),
    ]

    operations = [
        migrations.RunPython(
            populate_statement_checks, reverse_code=remove_statement_checks
        )
    ]
