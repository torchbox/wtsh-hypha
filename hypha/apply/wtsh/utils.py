from django.conf import settings
from django.test import RequestFactory

from hypha.apply.funds.models.submissions import ApplicationSubmission
from hypha.apply.users.models import User


def export_submission_to_pdf(
    submission: ApplicationSubmission, user: User, base_uri: str
) -> tuple[str, bytes]:
    """
    Export the given submission to a PDF, returning a 2-tuple containing the
    canonical filename (which you'd get if you downloaded the submission as PDF),
    and the PDF data (as bytes).
    """
    from hypha.apply.funds.views.submission_detail import SubmissionDetailPDFView

    # The PDF generation logic is mostly inside the view, so in order to avoid
    # duplicating too much code we simply call the view and extract the PDF data
    # from its response. This requires creating a valid request object.
    request = RequestFactory().get(
        base_uri,
        headers={"host": settings.PRIMARY_HOST},
    )
    request.user = user

    pdf_export_view = SubmissionDetailPDFView()
    pdf_export_view.setup(request=request)
    pdf_export_view.object = submission

    pdf_response = pdf_export_view.render_pdf()

    return (
        pdf_export_view.get_slugified_file_name("pdf"),
        pdf_response.content,
    )
