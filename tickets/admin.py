from django.contrib import admin
from .models import Category, Ticket, Comment


admin.site.register(Category)
admin.site.register(Ticket)
admin.site.register(Comment)