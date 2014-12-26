from django.contrib import admin
from mesg.models import Category, Message, UserDetails

admin.site.register(UserDetails)
admin.site.register(Category)
admin.site.register(Message)

