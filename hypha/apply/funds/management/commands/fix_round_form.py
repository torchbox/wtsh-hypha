from django.core.management.base import BaseCommand

from hypha.apply.funds.models import ApplicationForm, Round


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


def input_stage(round_: Round) -> int:
    """
    Prompt the user for which stage they want to replace (1 or 2).
    """
    print("Here are the round's current forms:")
    print(" * Concept (1):", round_.forms.get(stage=1))
    print(" * Proposal (2):", round_.forms.get(stage=2))
    print()

    return int(input("Which one do you want to replace (1/2)? "))


def input_replacement_form(round_: Round) -> ApplicationForm:
    """
    Prompt the user for which replacement form they want to use and return
    the actual ApplicationForm.
    """
    qs = ApplicationForm.objects.exclude(pk__in=round_.forms.values("pk"))
    d = dict(enumerate(qs))

    return _prompt_qs(
        qs,
        intro_str="Here are all the forms in the system",
        item_str=" * ({i}) {item.name}",
        input_str="Which form do you want to use instead? ",
    )


class Command(BaseCommand):
    help = "A custom WTSH command to fix a round's form after it's been created"

    def handle(self, **options):
        round_ = input_round()
        stage = input_stage(round_)
        form = input_replacement_form(round_)

        roundform = round_.forms.get(stage=stage)
        roundform.form = form

        if input("Confirm (y/N)").upper() in {"Y", "YES"}:
            roundform.save()
            self.stdout.write(self.style.SUCCESS("Done."))
        else:
            self.stdout.write(self.style.WARNING("Cancelled."))
