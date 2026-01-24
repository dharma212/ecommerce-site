from django.contrib import admin
from .models import *
from users.models import User

admin.site.register(User)