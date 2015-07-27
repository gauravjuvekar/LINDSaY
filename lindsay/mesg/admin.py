from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from mesg.models import Category, Message, UserDetails

admin.site.register(UserDetails)
admin.site.register(Category, MPTTModelAdmin)
admin.site.register(Message)
