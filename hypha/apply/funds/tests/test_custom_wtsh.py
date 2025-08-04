from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from hypha.apply.funds.tests.factories import ApplicationSubmissionFactory
from hypha.apply.users.tests.factories import AdminFactory


class UpdateUserFullNameInApplicationsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.application = ApplicationSubmissionFactory(
            form_data__title="Test application",
        )
        cls.user = cls.application.user
        cls.admin = AdminFactory()

    def setUp(self):
        self.client.force_login(self.admin)

    def post_user_update(self, **data):
        url = reverse("wagtailusers_users:edit", args=[self.user.pk])
        defaults = {
            "full_name": self.user.full_name,
            "first_name": self.user.first_name or "(irrelevant but required)",
            "last_name": self.user.last_name or "(irrelevant but required)",
            "email": self.user.email,
            "is_active": self.user.is_active,
            "groups": self.user.groups.values_list("pk", flat=True),
        }
        return self.client.post(url, defaults | data)

    def refresh_application_from_db(self):
        # Can't use refresh_from_db() on ApplicationSubmission :(
        self.application = self.application.__class__.objects.get(
            pk=self.application.pk
        )

    def test_updating_user_name_also_updates_application_data(self):
        response = self.post_user_update(full_name="Test Updated")
        self.refresh_application_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.application.data("full_name"), "Test Updated")
        self.assertEqual(self.application.data("title"), "Test application")

    def test_updating_user_email_also_updates_application_data(self):
        response = self.post_user_update(email="updated@example.com")
        self.refresh_application_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.application.data("email"), "updated@example.com")
        self.assertEqual(self.application.data("title"), "Test application")

    def test_query_count_not_linear_with_application_count(self):
        with CaptureQueriesContext(connection) as ctx:
            self.post_user_update(full_name="Test Updated")

        baseline_count = len(ctx.captured_queries)
        for _ in range(50):
            ApplicationSubmissionFactory(user=self.user)

        with self.assertNumQueries(baseline_count):
            self.post_user_update(full_name="Test Updated")
