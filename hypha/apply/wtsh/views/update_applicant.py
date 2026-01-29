from django.contrib.messages.views import SuccessMessageMixin
from django.utils.decorators import method_decorator
from django.utils.translation import gettext, gettext_lazy
from django.views import generic

from hypha.apply.funds.models.submissions import ApplicationSubmission
from hypha.apply.users.decorators import (
    staff_required,
)


@method_decorator(staff_required, name="dispatch")
class SubmissionUpdateApplicantView(SuccessMessageMixin, generic.UpdateView):
    model = ApplicationSubmission
    fields = ["user"]
    template_name = "submissions/update-applicant.html"
    success_message = gettext_lazy("Applicant was changed successfully.")

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["user"].queryset = form.fields["user"].queryset.applicants()
        form.fields["user"].label = gettext("New applicant")
        return form
