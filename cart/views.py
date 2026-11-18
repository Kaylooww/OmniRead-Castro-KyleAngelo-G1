from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from accounts.models import CustomUser
from dashboard.views import RoleRequiredMixin

from .forms import CartEditForm, available_ebooks
from .models import Cart, CartItem


def cart_for(user, *, lock=False):
    # Repair missing carts for accounts created outside signup.
    queryset = Cart.objects.select_for_update() if lock else Cart.objects
    cart, _ = queryset.get_or_create(user=user)
    return cart


class ReaderCartView(RoleRequiredMixin, View):
    role = CustomUser.Role.READER


class CatalogView(ReaderCartView):
    def get(self, request):
        return render(request, "cart/catalog.html", {"ebooks": available_ebooks()})


class CartReviewView(ReaderCartView):
    def get(self, request):
        cart = cart_for(request.user)
        items = list(cart.items.select_related("ebook").order_by("added_at", "pk"))
        prices = dict(
            available_ebooks().filter(pk__in=[item.ebook_id for item in items])
            .values_list("pk", "price")
        )
        lines = [(item, prices.get(item.ebook_id)) for item in items]
        total = sum(prices.values(), Decimal("0.00"))
        return render(request, "cart/review.html", {"lines": lines, "total": total})


class CartAddView(ReaderCartView):
    @transaction.atomic
    def post(self, request, ebook_id):
        cart = cart_for(request.user, lock=True)
        ebook = available_ebooks().filter(pk=ebook_id).first()
        if ebook is None:
            messages.error(request, "That ebook is unavailable.")
            return redirect("cart:catalog")

        _, created = cart.items.get_or_create(ebook=ebook)
        if created:
            cart.save(update_fields=["updated_at"])
            messages.success(request, f"Added {ebook.title} to your cart.")
        else:
            messages.info(request, f"{ebook.title} is already in your cart.")
        return redirect("cart:review")


class CartEditView(ReaderCartView):
    def get(self, request):
        cart = cart_for(request.user)
        form = CartEditForm(initial={
            "ebooks": list(cart.items.values_list("ebook_id", flat=True)),
            "revision": cart.updated_at.isoformat(),
        })
        return render(request, "cart/edit.html", {"form": form})

    @transaction.atomic
    def post(self, request):
        cart = cart_for(request.user, lock=True)
        form = CartEditForm(request.POST)
        if not form.is_valid():
            return render(request, "cart/edit.html", {"form": form}, status=400)

        if form.cleaned_data["revision"] != cart.updated_at.isoformat():
            messages.error(request, "Your cart changed. Review it and save again.")
            return redirect("cart:edit")

        selected_ids = {ebook.pk for ebook in form.cleaned_data["ebooks"]}
        current_ids = set(cart.items.values_list("ebook_id", flat=True))
        if selected_ids != current_ids:
            cart.items.filter(ebook_id__in=current_ids - selected_ids).delete()
            CartItem.objects.bulk_create([
                CartItem(cart=cart, ebook_id=ebook_id)
                for ebook_id in selected_ids - current_ids
            ])
            cart.save(update_fields=["updated_at"])

        messages.success(request, "Cart updated.")
        return redirect("cart:review")


class CartRemoveView(ReaderCartView):
    @transaction.atomic
    def post(self, request, item_id):
        cart = cart_for(request.user, lock=True)
        item = get_object_or_404(cart.items.select_related("ebook"), pk=item_id)
        title = item.ebook.title
        item.delete()
        cart.save(update_fields=["updated_at"])
        messages.success(request, f"Removed {title} from your cart.")
        return redirect("cart:review")
