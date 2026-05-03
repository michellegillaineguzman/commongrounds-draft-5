from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=100, default='Reader')

    def __str__(self):
        return self.name

class Genre(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Book(models.Model):
    title = models.CharField(max_length=255)
    genre = models.ForeignKey(Genre, null=True, blank=True, on_delete=models.SET_NULL, related_name='books')
    contributor = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    author = models.CharField(max_length=255)
    synopsis = models.TextField(null=True, blank=True)
    publication_year = models.IntegerField()
    available_to_borrow = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-publication_year']

class BookReview(models.Model):
    user_reviewer = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    anon_reviewer = models.CharField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    title = models.CharField(max_length=255)
    comment = models.TextField()

class Bookmark(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    date_bookmarked = models.DateTimeField(auto_now_add=True)

class Borrow(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrower = models.ForeignKey(Profile, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True)
    date_borrowed = models.DateTimeField()
    due_date = models.DateTimeField()
