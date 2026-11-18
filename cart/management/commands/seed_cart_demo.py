from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from cart.models import Author, Category, Ebook, EbookFile


class Command(BaseCommand):
    help = "Create two demo catalog entries using a PDF you have permission to distribute."

    def add_arguments(self, parser):
        parser.add_argument("--pdf", required=True, type=Path)

    @transaction.atomic
    def handle(self, *args, **options):
        pdf = options["pdf"].expanduser().resolve()
        try:
            with pdf.open("rb") as file:
                is_pdf = file.read(5) == b"%PDF-"
        except OSError as exc:
            raise CommandError("The demo PDF could not be opened.") from exc

        if not is_pdf:
            raise CommandError("Supply a valid PDF for the demo catalog.")

        author, _ = Author.objects.get_or_create(author_name="OmniRead Demo Author")
        category, _ = Category.objects.get_or_create(
            category_name="Demo Books", category_type=Category.Type.CATEGORY
        )
        for title, price in [
            ("OmniRead Demo Ebook A", Decimal("149.00")),
            ("OmniRead Demo Ebook B", Decimal("199.00")),
        ]:
            ebook, _ = Ebook.objects.get_or_create(title=title, defaults={"price": price})
            ebook.authors.add(author)
            ebook.categories.add(category)
            EbookFile.objects.update_or_create(
                ebook=ebook,
                file_format=EbookFile.Format.PDF,
                defaults={"storage_path": str(pdf)},
            )
            ebook.distribution_authorized = True
            ebook.is_active = True
            ebook.save(update_fields=["distribution_authorized", "is_active"])

        self.stdout.write(self.style.SUCCESS("Two demo ebooks are ready in Explore Books."))
