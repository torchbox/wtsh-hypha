from io import BytesIO
from typing import List

from celery import shared_task
from django.conf import settings

from hypha.apply.funds.models.submissions import ApplicationSubmission
from hypha.apply.todo.options import (
    DOWNLOAD_SUBMISSIONS_EXPORT,
    FAILED_SUBMISSIONS_EXPORT,
)
from hypha.apply.todo.views import add_task_to_user
from hypha.apply.users.models import User
from hypha.apply.utils.pdfs import pdfs_to_zip
from hypha.apply.wtsh.models import SubmissionPDFExportManager
from hypha.apply.wtsh.utils import export_submission_to_pdf


@shared_task
def generate_submission_pdf(
    qs_ids: List[int], request_user_id: int, base_uri: str
) -> None:
    """Celery task to generate a zip file containing PDFs of the given submission IDs

    Integer IDs have to be used as QuerySets are not simple data types & can't be
    passed to workers.

    Updates the user's SubmissionPDFExportManager object with status/final data, then
    adds a download task to the user's `My Tasks` when completed.

    Args:
        qs_ids: A list of application IDs to generate the CSV export for
        request_user_id: The ID of the user issuing the export request
    """
    try:
        qs = ApplicationSubmission.objects.filter(id__in=qs_ids)
        request_user = User.objects.get(pk=request_user_id)

        # If the user already has an existing export, delete it to begin the new one
        if current := SubmissionPDFExportManager.objects.filter(user=request_user):
            current.delete()

        export_manager = SubmissionPDFExportManager.objects.create(
            user=request_user, total_export=len(qs_ids)
        )
        pdfs = [
            export_submission_to_pdf(submission, request_user, base_uri)
            for submission in qs
        ]
        pdfs_to_zip((outfile := BytesIO()), pdfs)
        export_manager.export_data = outfile.getvalue()
        export_manager.set_completed_and_save()

        user_task = DOWNLOAD_SUBMISSIONS_EXPORT

    except Exception as exc:
        # Update the status to failed
        export_manager.set_failed_and_save()
        user_task = FAILED_SUBMISSIONS_EXPORT

        if settings.SENTRY_DSN:
            # If sentry is enabled, pass the exception to sentry
            from sentry_sdk import capture_exception

            capture_exception(exc)
        else:
            # Otherwise re-raise it
            raise exc
    finally:
        # When the generation is complete or failed, add a task to the user's dashboard (only if async)
        if not settings.CELERY_TASK_ALWAYS_EAGER:
            add_task_to_user(
                code=user_task,
                user=request_user,
                related_obj=export_manager,
            )
