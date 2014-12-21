from django import forms
from mesg.models import Category, Message

class CategoryModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        if obj.parent == None:
            return obj.name
        else:
            return '----' + obj.name

        

class CreateMessageForm(forms.Form):
    message_text = forms.CharField(
            label='Message',
            widget=forms.Textarea,
            # TODO: set maxlength from message model
            max_length=200
    )

    expires_date = forms.DateField(
            label='Expire this message after',
            required=False
    )

    categories = Category.objects.none()
    for division in Category.objects.filter(parent=None):
        categories |= Category.objects.filter(pk=division.pk)
        categories |= division.subcategories.all()

    category = CategoryModelChoiceField(
            queryset=categories,
            label='Category'
    )

