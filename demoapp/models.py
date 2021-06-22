"""
These models are copied from
https://github.com/mdn/django-locallibrary-tutorial/blob/master/catalog/models.py
"""
from datetime import date
import uuid

import django
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse  # To generate URLS by reversing URL patterns

if django.VERSION < (3, 1, 0):
    RESTRICT = models.PROTECT
else:
    RESTRICT = models.RESTRICT


class Genre(models.Model):
    """Model representing a book genre (e.g. Science Fiction, Non Fiction)."""
    name = models.CharField(
        max_length=200,
        help_text="Enter a book genre "
                  "(e.g. Science Fiction, French Poetry etc.)"
    )

    def get_absolute_url(self):
        """Returns the url to access a particular genre instance."""
        return reverse('genre-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name


class Language(models.Model):
    """Model representing a Language (e.g. English, French, Japanese, etc.)"""
    name = models.CharField(
        max_length=200,
        help_text="Enter the book's natural language "
                  "(e.g. English, French, Japanese etc.)"
    )

    def get_absolute_url(self):
        """Returns the url to access a particular genre instance."""
        return reverse('language-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name


class Book(models.Model):
    """Model representing a book (but not a specific copy of a book)."""
    title = models.CharField(max_length=200)
    author = models.ForeignKey(
        'Author',
        on_delete=models.SET_NULL,
        null=True
    )
    # Foreign Key used because book can only have one author, but authors can
    # have multiple books Author as a string rather than object because it
    # hasn't been declared yet in file.
    summary = models.TextField(
        max_length=1000,
        help_text="Enter a brief description of the book"
    )
    isbn = models.CharField(
        'ISBN',
        max_length=13,
        unique=True,
        help_text='13 Character <a '
                  'href="https://www.isbn-international.org/content/what-isbn"'
                  '>ISBN number</a>'
    )
    genre = models.ManyToManyField(
        Genre,
        help_text="Select a genre for this book"
    )
    # ManyToManyField used because a genre can contain many books and a Book
    # can cover many genres.
    # Genre class has already been defined so we can specify the object above.
    language = models.ForeignKey(
        'Language',
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        ordering = ['title', 'author']

    def display_genre(self):
        """
        Creates a string for the Genre. This is required to display genre
        in Admin.
        """
        return ', '.join([genre.name for genre in self.genre.all()[:3]])

    display_genre.short_description = 'Genre'

    def get_absolute_url(self):
        """Returns the url to access a particular book instance."""
        return reverse('book-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return self.title


class BookInstance(models.Model):
    """
    Model representing a specific copy of a book (i.e. that can be borrowed
    from the library).
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        help_text="Unique ID for this particular book across whole library"
    )
    book = models.ForeignKey(
        'Book',
        on_delete=RESTRICT,
        null=True
    )
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(
        null=True,
        blank=True
    )
    borrower = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

    LOAN_STATUS = (
        ('d', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='d',
        help_text='Book availability')

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        """String for representing the Model object."""
        return '{0} ({1})'.format(self.id, self.book.title)


class Author(models.Model):
    """Model representing an author."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(
        null=True,
        blank=True
    )
    date_of_death = models.DateField(
        'died',
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return '{0}, {1}'.format(self.last_name, self.first_name)


class Profile(models.Model):
    LIBRARIAN = 1
    VISITOR = 2
    SUPERVISOR = 3
    ROLE_CHOICES = (
        (LIBRARIAN, 'Librarian'),
        (VISITOR, 'Visitor'),
        (SUPERVISOR, 'Supervisor'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=30, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    role = models.PositiveSmallIntegerField(
        choices=ROLE_CHOICES,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
