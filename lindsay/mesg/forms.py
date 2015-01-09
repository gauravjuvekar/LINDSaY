from django import forms
from mesg.models import Category

class CalendarWidget(forms.TextInput):
    class Media:
        # TODO:Untie this from mesg app later
        # TODO:Use minified js
        css = {
                'all': ('mesg/css/jquery-ui.css',)
        }
        js = (
                'mesg/js/external/jquery/jquery.js',
                'mesg/js/jquery-ui.js',
        )



class CreateMessageForm(forms.Form):
    message_text = forms.CharField(
            label='Message',
            widget=forms.Textarea,
            # TODO: set maxlength from message model
            max_length=200
    )

    expires_date = forms.DateField(
            label='Expire this message after',
            required=False,
            widget = CalendarWidget,
    )

    choices = [('','----')]
    for division in Category.objects.filter(parent=None):
        choices.append((division.id, division.name))
        for subdivision in division.subcategories.all():
            choices.append((subdivision.id, '----' + subdivision.name))

    category = forms.ChoiceField(
            choices=choices,
            label='Category',
            required=True
    )


class UserConfigForm(forms.Form):

    choices = [('','----')]
    for division in Category.objects.filter(parent=None):
        choices.append((division.id, division.name))
        for subdivision in division.subcategories.all():
            choices.append((subdivision.id, '----' + subdivision.name))

    category = forms.ChoiceField(
            choices=choices,
            label='Category',
            required=True,
    )
    
