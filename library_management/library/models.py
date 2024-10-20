# library/models.py
from django.db import models
from django.utils import timezone

class Book(models.Model):
    title = models.CharField(max_length=255)
    authors = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    publisher = models.CharField(max_length=255)
    num_pages = models.IntegerField(default=200)
    stock = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.title} by {self.authors}"

class Member(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    debt = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)

    def __str__(self):
        return self.name

    def can_borrow(self):
        return self.debt <= 500  # Maximum allowable debt is Rs.500

class Transaction(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    issued_date = models.DateField(default=timezone.now)
    return_date = models.DateField(null=True, blank=True)
    rent_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.book.title} issued to {self.member.name}"
