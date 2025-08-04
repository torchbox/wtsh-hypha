from django.urls import re_path
from wagtail import hooks
from wagtail.models import Site

from hypha.apply.activity.messaging import MESSAGES, messenger

from .admin_views import CustomGroupViewSet, CustomUserIndexView
from .utils import send_activation_email, update_is_staff


@hooks.register("register_admin_urls")
def register_admin_urls():
    return [
        re_path(r"^users/$", CustomUserIndexView.as_view(), name="index"),
    ]


@hooks.register("register_admin_viewset")
def register_viewset():
    return CustomGroupViewSet("groups", url_prefix="groups")


@hooks.register("after_create_user")
def notify_after_create_user(request, user):
    messenger(
        MESSAGES.STAFF_ACCOUNT_CREATED,
        request=request,
        user=request.user,
        source=user,
    )

    site = Site.find_for_request(request)
    send_activation_email(user, site)


@hooks.register("after_edit_user")
def notify_after_edit_user(request, user):
    roles = list(user.groups.values_list("name", flat=True))
    if user.is_superuser:
        roles.append("Administrator")
    if roles:
        roles = ", ".join(roles)
        messenger(
            MESSAGES.STAFF_ACCOUNT_EDITED,
            request=request,
            user=request.user,
            source=user,
            roles=roles,
        )


@hooks.register("after_edit_user")
def update_user_data_in_applications(request, user):
    """
    When a user's name is updated, also update the name attached to all their
    submissions.
    """
    user_data_fields = ["full_name", "email"]
    updated_applications = []
    for submission in user.applicationsubmission_set.all():
        updated = False

        for field in user_data_fields:
            if submission.data(field) != getattr(user, field):
                submission.form_data[field] = getattr(user, field)
                updated = True

        if updated:
            updated_applications.append(submission)

    if updated_applications:
        user.applicationsubmission_set.model.objects.bulk_update(
            updated_applications,
            fields=["form_data"],
        )


# Handle setting of `is_staff` after updating a user
hooks.register("after_create_user", update_is_staff)
hooks.register("after_edit_user", update_is_staff)
