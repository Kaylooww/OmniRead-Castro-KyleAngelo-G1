from django.urls import path

from .views import CartAddView, CartEditView, CartRemoveView, CartReviewView, CatalogView

app_name = "cart"

urlpatterns = [
    path("books/", CatalogView.as_view(), name="catalog"),
    path("cart/", CartReviewView.as_view(), name="review"),
    path("cart/edit/", CartEditView.as_view(), name="edit"),
    path("cart/add/<int:ebook_id>/", CartAddView.as_view(), name="add"),
    path("cart/remove/<int:item_id>/", CartRemoveView.as_view(), name="remove"),
]
