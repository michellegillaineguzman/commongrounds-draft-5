from django.urls import path
from . import views

app_name = 'bookclub'

urlpatterns = [
    path('books/', views.BookListView.as_view(), name='book_list'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('book/add/', views.BookCreateView.as_view(), name='book_create'),
    path('book/<int:pk>/edit/', views.BookUpdateView.as_view(), name='book_update'),
    path('book/<int:pk>/borrow/', views.BookBorrowView.as_view(), name='book_borrow'),
    path('book/<int:pk>/bookmark/', views.BookmarkToggleView.as_view(), name='bookmark_toggle'),
    path('review/<int:pk>/delete/', views.delete_review, name='review_delete'),
]