
from django.db import models
from django.conf import settings
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Ticket(models.Model):

    STATUS_CHOICES = [
        ('New', 'Нова'),
        ('In Progress', 'В роботі'),
        ('Waiting', 'Очікує відповіді клієнта'),
        ('Resolved', 'Вирішена'),
        ('Closed', 'Закрита'),
        ('Rejected', 'Відхилена'),
    ]

    PRIORITY_CHOICES = [
        ('Low', 'Низький'),
        ('Medium', 'Середній'),
        ('High', 'Високий'),
        ('Critical', 'Критичний'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='Medium'
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='New'
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tickets'
    )

    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def is_closed(self):
        return self.status in ['Closed', 'Rejected']

    @property
    def can_reopen(self):
        if self.status != 'Resolved' or not self.resolved_at:
            return False

        return timezone.now() <= self.resolved_at + timezone.timedelta(days=3)


class Comment(models.Model):

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    text = models.TextField()
    is_internal = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Коментар від {self.author}'
