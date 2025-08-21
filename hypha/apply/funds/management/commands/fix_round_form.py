from django.core.management.base import BaseCommand

from hypha.apply.funds.models import ApplicationForm, Round
from hypha.apply.funds.models.forms import RoundBaseForm, RoundBaseReviewForm
from hypha.apply.review.models import ReviewForm


def _prompt_qs(queryset, intro_str, item_str, input_str):
    d = dict(enumerate(queryset, start=1))

    print(intro_str)
    for i, item in d.items():
        print(item_str.format(i=i, item=item))
    print()
    index = int(input(input_str))
    return d[index]


def input_round() -> Round:
    """
    Assuming there's only a single Round defined, return it. Otherwise prompt
    the user for it then return the result.
    """
    try:
        return Round.objects.get()
    except Round.MultipleObjectsReturned:
        pass

    return _prompt_qs(
        Round.objects.all(),
        intro_str="Here are the available rounds:",
        item_str=" * {i} {item.fund.title} > {item.title}",
        input_str="Which round do you want to change? ",
    )


def input_roundform(round_: Round) -> RoundBaseForm:
    return _prompt_qs(
        round_.forms.all(),
        intro_str="Here are the round's stage forms:",
        item_str=" * {i} {item.form.name}",
        input_str="Which stage do you want to change? ",
    )


def input_roundform_review(round_: Round) -> RoundBaseReviewForm:
    return _prompt_qs(
        round_.review_forms.all(),
        intro_str="Here are the round's stage review forms:",
        item_str=" * {i} {item.form.name}",
        input_str="Which stage do you want to change? ",
    )


def input_replacement_form(round_: Round) -> ApplicationForm:
    """
    Prompt the user for which replacement form they want to use and return
    the actual ApplicationForm.
    """
    qs = ApplicationForm.objects.exclude(pk__in=round_.forms.values("pk"))

    return _prompt_qs(
        qs,
        intro_str="Here are all the forms in the system",
        item_str=" * ({i}) {item.name}",
        input_str="Which form do you want to use instead? ",
    )


def input_replacement_review_form(round_: Round) -> ReviewForm:
    """
    Prompt the user for which replacement form they want to use and return
    the actual ReviewForm.
    """
    qs = ReviewForm.objects.exclude(pk__in=round_.forms.values("pk"))

    return _prompt_qs(
        qs,
        intro_str="Here are all the review forms in the system",
        item_str=" * ({i}) {item.name}",
        input_str="Which review form do you want to use instead? ",
    )


class Command(BaseCommand):
    help = "A custom WTSH command to fix a round's form after it's been created"

    def add_arguments(self, parser):
        parser.add_argument(
            "--review", help="Replace a **review** form", action="store_true"
        )

    def handle(self, **options):
        round_ = input_round()
        if options["review"]:
            roundform = input_roundform_review(round_)
            form = input_replacement_review_form(round_)
        else:
            roundform = input_roundform(round_)
            form = input_replacement_form(round_)

        roundform.form = form

        if input("Confirm (y/N)").upper() in {"Y", "YES"}:
            roundform.save()
            self.stdout.write(self.style.SUCCESS("Done."))
        else:
            self.stdout.write(self.style.WARNING("Cancelled."))
