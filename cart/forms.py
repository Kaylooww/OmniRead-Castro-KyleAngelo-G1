from django import forms
from django.db.models import Exists, OuterRef

from .models import Ebook, EbookFile


def available_ebooks():
    return Ebook.objects.filter(
        Exists(Ebook.authors.through.objects.filter(ebook_id=OuterRef("pk"))),
        Exists(Ebook.categories.through.objects.filter(ebook_id=OuterRef("pk"))),
        Exists(
            EbookFile.objects.filter(ebook_id=OuterRef("pk")).exclude(storage_path="")
        ),
        is_active=True,
        distribution_authorized=True,
    ).exclude(title="").order_by("title", "pk")


class EbookChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, ebook):
        return f"{ebook.title} (PHP {ebook.price:,.2f})"


class CartEditForm(forms.Form):
    ebooks = EbookChoiceField(
        queryset=Ebook.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Ebooks in your cart",
        error_messages={
            "invalid_choice": "One of your selected ebooks is unavailable.",
            "invalid_pk_value": "One of your selected ebook IDs is invalid.",
        },
    )
    revision = forms.CharField(widget=forms.HiddenInput, max_length=40)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ebooks"].queryset = available_ebooks()
