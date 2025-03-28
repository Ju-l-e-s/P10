from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Project, Contributor, Issue, Comment

# custom User model to the Django admin
admin.site.register(User, UserAdmin)

# models to manage via the admin
admin.site.register(Project)
admin.site.register(Contributor)
admin.site.register(Issue)
admin.site.register(Comment)
