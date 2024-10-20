# library/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # for books
    
    path('book-list/', views.book_list, name='book_list'),
    path('books/delete/<str:isbn>/', views.delete_book, name='delete_book'),
    path('books/update/<str:isbn>/', views.update_book, name='update_book'),
    path('import/', views.import_books, name='import_books'),
    
    # for members
    path('members/', views.member_list, name='member_list'),  # List members
    path('members/add/', views.add_member, name='add_member'),  # Add a member
    path('members/update/<int:id>/', views.update_member, name='update_member'),  # Update a member
    path('members/delete/<int:id>/', views.delete_member, name='delete_member'),
    
    # for transaction
    path('transactions/', views.transaction_list, name='transaction_list'),  # View transaction log
    path('transactions/issue/', views.issue_book, name='issue_book'),  # Issue a book
    path('transactions/return/<int:id>/', views.return_book, name='return_book'),
    path('issue/<int:book_id>/', views.issue_book, name='issue_book'),
]
