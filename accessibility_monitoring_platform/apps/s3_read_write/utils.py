import boto3
from typing import Union
import os
from ...settings.base import DEBUG, DATABASES, UNDER_TEST, S3_MOCK_ENDPOINT
from django.contrib.auth.models import User
from ..cases.models import Case
from .models import S3Report


class S3ReadWriteReport:
    def __init__(self) -> None:
        self.s3_resource = boto3.resource(
            service_name="s3",
            region_name=DATABASES["aws-s3-bucket"]["aws_region"],
            aws_access_key_id=DATABASES["aws-s3-bucket"]["aws_access_key_id"],
            aws_secret_access_key=DATABASES["aws-s3-bucket"]["aws_secret_access_key"],
            endpoint_url=S3_MOCK_ENDPOINT
        )

        self.s3_client = boto3.client(
            "s3",
            region_name=DATABASES["aws-s3-bucket"]["aws_region"],
            aws_access_key_id=DATABASES["aws-s3-bucket"]["aws_access_key_id"],
            aws_secret_access_key=DATABASES["aws-s3-bucket"]["aws_secret_access_key"],
            endpoint_url=S3_MOCK_ENDPOINT
        )

        # Creates bucket for unit testing, integration testing, and local development
        if DEBUG or UNDER_TEST:
            response = self.s3_client.list_buckets()
            bucket_names = [bucket["Name"] for bucket in response["Buckets"]]
            if DATABASES["aws-s3-bucket"]["bucket_name"] not in bucket_names:
                self.s3_client.create_bucket(Bucket=DATABASES["aws-s3-bucket"]["bucket_name"])

        self.bucket: str = DATABASES["aws-s3-bucket"]["bucket_name"]

    def upload_string_to_s3_as_html(
        self,
        html_content: str,
        case: Case,
        user: User
    ) -> str:
        version = 1
        if S3Report.objects.filter(case=case).exists():
            version = len(S3Report.objects.filter(case=case)) + 1

        platform_version: Union[str, None] = os.getenv("PLATFORM_VERSION")
        if platform_version is None:
            platform_version = "0.1.0"

        # version of platform
        s3_url_for_report: str = self.url_builder(
            organisation_name=case.organisation_name,
            case_id=case.id,  # type: ignore
            version=version,
            platform_version=platform_version
        )

        self.s3_client.put_object(
            Body=html_content,
            Bucket=self.bucket,
            Key=s3_url_for_report
        )

        s3report = S3Report(
            case=case,
            created_by=user,
            s3_directory=s3_url_for_report,
            version=version,
        )

        s3report.save()
        return s3report.guid

    def retrieve_raw_html_from_s3_by_guid(self, guid: str):
        if S3Report.objects.filter(guid=guid).exists():
            s3file = S3Report.objects.get(guid=guid)
            obj = self.s3_resource.Object(self.bucket, s3file.s3_directory)  # type: ignore
            return obj.get()["Body"].read().decode("utf-8")
        return "<p> Does not exist </p>"

    def url_builder(self, organisation_name: str, case_id: int, version: int, platform_version: str) -> str:
        return f"""caseid_{case_id}/org_{organisation_name}__reportid_{version}__platformversion_{platform_version}.html"""
