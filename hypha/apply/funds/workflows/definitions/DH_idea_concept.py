from django.utils.translation import gettext as _

from ..constants import DRAFT_STATE, INITIAL_STATE, UserPermissions
from ..models.stage import DHConcept, DHIdea
from ..permissions import (
    applicant_edit_permissions,
    default_permissions,
    hidden_from_applicant_permissions,
    no_permissions,
    reviewer_review_permissions,
    staff_edit_permissions,
)

DHIdeaConceptDefinition = [
    {
        DRAFT_STATE: {
            "transitions": {
                INITIAL_STATE: {
                    "display": _("Submit"),
                    "permissions": {UserPermissions.APPLICANT},
                    "method": "create_revision",
                    "custom": {"trigger_on_submit": True},
                },
            },
            "display": _("Draft"),
            "stage": DHIdea,
            "permissions": applicant_edit_permissions,
        }
    },
    {
        INITIAL_STATE: {
            "transitions": {
                "idea_more_info": _("Request More Information"),
                "idea_external_review": _("Open Review"),
                "idea_rejected": _("Dismiss"),
            },
            "display": _("Need screening"),
            "public": _("Idea Received"),
            "stage": DHIdea,
            "permissions": default_permissions,
        },
        "idea_more_info": {
            "transitions": {
                INITIAL_STATE: {
                    "display": _("Submit"),
                    "permissions": {
                        UserPermissions.APPLICANT,
                        UserPermissions.STAFF,
                        UserPermissions.LEAD,
                        UserPermissions.ADMIN,
                    },
                    "method": "create_revision",
                    "custom": {"trigger_on_submit": True},
                },
                "idea_rejected": _("Dismiss"),
            },
            "display": _("More information required"),
            "stage": DHIdea,
            "permissions": applicant_edit_permissions,
        },
    },
    {
        "idea_external_review": {
            "transitions": {
                "idea_determination": _("Close Review"),
                INITIAL_STATE: _("Need screening (revert)"),
            },
            "display": _("External Review"),
            "stage": DHIdea,
            "permissions": reviewer_review_permissions,
        },
    },
    {
        "idea_determination": {
            "transitions": {
                "idea_external_review": _("Open Review (revert)"),
                "idea_accepted": _("Invite to Concept"),
                "idea_rejected": _("Dismiss"),
            },
            "display": _("Ready for Preliminary Determination"),
            "permissions": hidden_from_applicant_permissions,
            "stage": DHIdea,
        },
    },
    {
        "idea_accepted": {
            "display": _("Idea Accepted"),
            "future": _("Preliminary Determination"),
            "transitions": {
                "concept_draft": {
                    "display": _("Progress"),
                    "method": "progress_application",
                    "permissions": {
                        UserPermissions.STAFF,
                        UserPermissions.LEAD,
                        UserPermissions.ADMIN,
                    },
                    "conditions": "not_progressed",
                },
            },
            "stage": DHIdea,
            "permissions": no_permissions,
        },
        "idea_rejected": {
            "display": _("Dismissed"),
            "stage": DHIdea,
            "permissions": no_permissions,
        },
    },
    {
        "concept_draft": {
            "transitions": {
                "concept_discussion": {
                    "display": _("Submit"),
                    "permissions": {UserPermissions.APPLICANT},
                    "method": "create_revision",
                    "custom": {"trigger_on_submit": True},
                },
                "external_review": _("Open Review"),
                "concept_rejected": _("Dismiss"),
            },
            "display": _("Invited for Concept"),
            "stage": DHConcept,
            "permissions": applicant_edit_permissions,
        },
    },
    {
        "concept_discussion": {
            "transitions": {
                "concept_more_info": _("Request More Information"),
                "concept_external_review": _("Open Review"),
                "concept_rejected": _("Dismiss"),
            },
            "display": _("Concept Received"),
            "stage": DHConcept,
            "permissions": default_permissions,
        },
        "concept_more_info": {
            "transitions": {
                "concept_discussion": {
                    "display": _("Submit"),
                    "permissions": {
                        UserPermissions.APPLICANT,
                        UserPermissions.STAFF,
                        UserPermissions.LEAD,
                        UserPermissions.ADMIN,
                    },
                    "method": "create_revision",
                    "custom": {"trigger_on_submit": True},
                },
                "concept_external_review": _("Open Review"),
                "concept_rejected": _("Dismiss"),
            },
            "display": _("More information required"),
            "stage": DHConcept,
            "permissions": applicant_edit_permissions,
        },
    },
    {
        "concept_external_review": {
            "transitions": {
                "concept_determination": _("Close Review"),
                "concept_discussion": _("Concept Received (revert)"),
            },
            "display": _("External Review"),
            "stage": DHConcept,
            "permissions": reviewer_review_permissions,
        },
    },
    {
        "concept_determination": {
            "transitions": {
                "concept_accepted": _("Accept"),
                "concept_rejected": _("Dismiss"),
            },
            "display": _("Ready for Final Determination"),
            "permissions": hidden_from_applicant_permissions,
            "stage": DHConcept,
        },
    },
    {
        "concept_accepted": {
            "display": _("Accepted"),
            "future": _("Final Determination"),
            "stage": DHConcept,
            "permissions": staff_edit_permissions,
        },
        "concept_rejected": {
            "display": _("Dismissed"),
            "stage": DHConcept,
            "permissions": no_permissions,
        },
    },
]
