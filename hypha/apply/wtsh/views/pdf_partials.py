from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from hypha.apply.funds.models.utils import (
    STATUS_ERROR,
    STATUS_GENERATING,
    STATUS_SUCCESS,
)
from hypha.apply.funds.utils import get_export_polling_time
from hypha.apply.todo.options import DOWNLOAD_SUBMISSIONS_EXPORT
from hypha.apply.todo.views import remove_tasks_of_related_obj_for_specific_code
from hypha.apply.wtsh.models import SubmissionPDFExportManager

User = get_user_model()


# Adapted from hypha.apply.funds.views.partials.submission_export_status()
def submission_export_pdf_status(request: HttpRequest) -> HttpResponse:
    ctx = {}
    status = None

    if not settings.CELERY_TASK_ALWAYS_EAGER:
        if export_manager := SubmissionPDFExportManager.objects.filter(
            user=request.user
        ).first():
            # If there's an existing/active export, show it's status
            status = export_manager.status
            if status == STATUS_GENERATING:
                ctx["poll_time"] = get_export_polling_time(export_manager.total_export)
    else:
        ctx["not_async"] = True

    if status is None or status == STATUS_ERROR:
        # There's not an active job or we're running in sync, extract all submissions
        # view URL to pass the query params to the `submissions_all` view for
        # generation, appending `&format=csv`
        all_url = urlparse(request.headers.get("Hx-Current-Url"))
        url_list = list(all_url)
        url_list[4] = urlencode(
            {**parse_qs(all_url.query), "format": "pdf"}, doseq=True
        )
        ctx["start_export_url"] = urlunparse(url_list)

    ctx["generating"] = status == STATUS_GENERATING
    ctx["failed"] = status == STATUS_ERROR
    ctx["success"] = status == STATUS_SUCCESS

    return render(
        request, "submissions/partials/export-submission-pdf-button.html", ctx
    )


# Adapted from hypha.apply.funds.views.partials.submission_export_download()
def submission_export_pdf_download(request: HttpRequest) -> HttpResponse:
    export_manager = get_object_or_404(SubmissionPDFExportManager, user=request.user)
    if export_manager.status == "success":
        response = HttpResponse(
            export_manager.export_data, content_type="application/zip"
        )
        response["Content-Disposition"] = "attachment; filename=submissions.zip"

        remove_tasks_of_related_obj_for_specific_code(
            code=DOWNLOAD_SUBMISSIONS_EXPORT, related_obj=export_manager
        )
        export_manager.delete()

        return response

    raise Http404()
