from django.conf import settings
from django.db import models


class Author(models.Model):
    author_id = models.AutoField(primary_key=True)
    author_name = models.CharField(max_length=150)

    class Meta:
        db_table = "authors"


class Category(models.Model):
    class Type(models.TextChoices):
        CATEGORY = "CATEGORY", "Category"
        GENRE = "GENRE", "Genre"

    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=10, choices=Type.choices)

    class Meta:
        db_table = "categories"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(category_type__in=["CATEGORY", "GENRE"]),
                name="category_type_valid",
            ),
            models.UniqueConstraint(
                fields=["category_name", "category_type"],
                name="category_name_type_unique",
            ),
        ]


class Ebook(models.Model):
    ebook_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    synopsis = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cover_url = models.URLField(blank=True)
    distribution_authorized = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    authors = models.ManyToManyField(Author, db_table="ebook_authors")
    categories = models.ManyToManyField(Category, db_table="ebook_categories")

    class Meta:
        db_table = "ebooks"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gt=0),
                name="ebook_price_positive",
            ),
        ]

    def __str__(self):
        return self.title


class EbookFile(models.Model):
    class Format(models.TextChoices):
        EPUB = "EPUB", "EPUB"
        PDF = "PDF", "PDF"

    file_id = models.AutoField(primary_key=True)
    ebook = models.ForeignKey(Ebook, on_delete=models.CASCADE, related_name="files")
    file_format = models.CharField(max_length=4, choices=Format.choices)
    storage_path = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ebook_files"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(file_format__in=["EPUB", "PDF"]),
                name="ebook_file_format_valid",
            ),
            models.UniqueConstraint(
                fields=["ebook", "file_format"],
                name="ebook_one_file_per_format",
            ),
        ]


class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "carts"


class CartItem(models.Model):
    cart_item_id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    ebook = models.ForeignKey(Ebook, on_delete=models.PROTECT)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cart_items"
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "ebook"],
                name="cart_one_entry_per_ebook",
            ),
        ]
