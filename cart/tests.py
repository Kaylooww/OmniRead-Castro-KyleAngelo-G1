from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .models import Author, Cart, CartItem, Category, Ebook, EbookFile

User = get_user_model()
PASSWORD = "OmniRead-Test-Password-82"


@override_settings(STORAGES={
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
})
class CartFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.reader = User.objects.create_user(
            username="reader", email="reader@example.com", password=PASSWORD
        )
        cls.other_reader = User.objects.create_user(
            username="other", email="other@example.com", password=PASSWORD
        )
        cls.admin = User.objects.create_user(
            username="admin", email="admin@example.com", role=User.Role.ADMIN
        )
        author = Author.objects.create(author_name="Demo Author")
        category = Category.objects.create(
            category_name="Fiction", category_type=Category.Type.GENRE
        )
        cls.first = cls.make_ebook("First Ebook", "149.00", author, category)
        cls.second = cls.make_ebook("Second Ebook", "199.00", author, category)

    @staticmethod
    def make_ebook(title, price, author, category):
        ebook = Ebook.objects.create(
            title=title, price=price, is_active=True, distribution_authorized=True
        )
        ebook.authors.add(author)
        ebook.categories.add(category)
        EbookFile.objects.create(ebook=ebook, file_format="PDF", storage_path="private/demo.pdf")
        return ebook

    def test_reader_adds_edits_and_removes_persisted_items(self):
        self.client.force_login(self.reader)
        dashboard = self.client.get(reverse("reader_dashboard"))
        self.assertContains(dashboard, reverse("cart:catalog"))
        self.assertContains(dashboard, reverse("cart:review"))
        catalog = self.client.get(reverse("cart:catalog"))
        self.assertContains(catalog, "First Ebook")

        for ebook in (self.first, self.second, self.first):
            self.client.post(reverse("cart:add", args=[ebook.pk]))

        review = self.client.get(reverse("cart:review"))
        self.assertContains(review, "PHP 348.00")
        self.assertEqual(CartItem.objects.filter(cart__user=self.reader).count(), 2)

        edit = self.client.get(reverse("cart:edit"))
        self.assertContains(edit, "Save selection")
        self.client.post(reverse("cart:edit"), {
            "ebooks": [self.second.pk],
            "revision": edit.context["form"].initial["revision"],
        })

        new_session = Client()
        self.assertTrue(new_session.login(email=self.reader.email, password=PASSWORD))
        review = new_session.get(reverse("cart:review"))
        self.assertEqual(review.context["total"], Decimal("199.00"))
        self.assertNotContains(review, "First Ebook")
        self.assertContains(review, "Second Ebook")

        item = CartItem.objects.get(cart__user=self.reader)
        removed = new_session.post(reverse("cart:remove", args=[item.pk]), follow=True)
        self.assertContains(removed, "Your cart is empty.")
        self.assertContains(removed, "PHP 0.00")
        self.assertFalse(CartItem.objects.filter(cart__user=self.reader).exists())

    def test_signup_login_profile_and_logout(self):
        details = {
            "email": "new@example.com", "username": "newreader",
            "first_name": "New", "last_name": "Reader", "contact_number": "",
        }
        response = self.client.post(reverse("signup"), {
            **details, "password1": PASSWORD, "password2": PASSWORD,
        })
        self.assertRedirects(response, reverse("login"))
        self.assertTrue(Cart.objects.filter(user__email=details["email"]).exists())

        response = self.client.post(
            reverse("login"), {"username": details["email"], "password": PASSWORD},
            follow=True,
        )
        self.assertContains(response, reverse("cart:review"))
        response = self.client.post(reverse("profile_edit"), {
            **details, "first_name": "Updated",
        }, follow=True)
        self.assertContains(response, "Profile updated.")
        self.assertEqual(User.objects.get(email=details["email"]).first_name, "Updated")
        self.assertRedirects(self.client.post(reverse("logout")), reverse("login"))

    def test_guest_and_admin_access(self):
        review_url = reverse("cart:review")
        self.assertRedirects(self.client.get(review_url), f'{reverse("login")}?next={review_url}')
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse("admin_dashboard")).status_code, 200)
        self.assertEqual(self.client.get(reverse("user_list")).status_code, 200)
        self.assertEqual(self.client.get(review_url).status_code, 403)
        self.assertEqual(self.client.post(reverse("cart:add", args=[self.first.pk])).status_code, 403)

    def test_other_reader_cannot_see_or_remove_item(self):
        cart = Cart.objects.create(user=self.reader)
        item = cart.items.create(ebook=self.first)
        self.client.force_login(self.other_reader)
        self.assertContains(self.client.get(reverse("cart:review")), "Your cart is empty.")
        self.assertEqual(self.client.post(reverse("cart:remove", args=[item.pk])).status_code, 404)
        self.assertTrue(CartItem.objects.filter(pk=item.pk).exists())

    def test_unavailable_ebook_and_invalid_edit(self):
        self.first.is_active = False
        self.first.save(update_fields=["is_active"])
        self.client.force_login(self.reader)
        catalog = self.client.get(reverse("cart:catalog"))
        self.assertNotContains(catalog, "First Ebook")

        add = self.client.post(reverse("cart:add", args=[self.first.pk]), follow=True)
        self.assertContains(add, "That ebook is unavailable.")
        edit_url = reverse("cart:edit")
        revision = self.client.get(edit_url).context["form"].initial["revision"]
        edit = self.client.post(edit_url, {"ebooks": [self.first.pk], "revision": revision})
        self.assertContains(edit, "One of your selected ebooks is unavailable.", status_code=400)
        self.assertFalse(CartItem.objects.exists())

    def test_stale_edit_preserves_a_newer_cart_change(self):
        self.client.force_login(self.reader)
        edit_url = reverse("cart:edit")
        revision = self.client.get(edit_url).context["form"].initial["revision"]
        self.client.post(reverse("cart:add", args=[self.first.pk]))
        edit = self.client.post(edit_url, {"revision": revision}, follow=True)
        self.assertContains(edit, "Your cart changed.")
        self.assertTrue(CartItem.objects.filter(cart__user=self.reader, ebook=self.first).exists())
