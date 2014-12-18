from django.contrib import admin
from mesg.models import Division, SubDivision, Message, UserDetails

admin.site.register(UserDetails)
admin.site.register(Division)
admin.site.register(SubDivision)
admin.site.register(Message)

