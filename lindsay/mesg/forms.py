from django import forms
from mesg.models import Message, Division, SubDivision

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

    # NOTE: TDWTF worthy, make generic category model
    choices = []
    for division in Division.objects.all():
        choices.append( ('division_' + str(division.pk), division.name))
        for subdivision in division.subdivisions.all():
            choices.append(
                    (
                        'subdivision_' + str(subdivision.pk),
                        '----' + division.name + subdivision.name
                    )
            )

    category = forms.ChoiceField(
            choices=choices,
            label='Category'
    )

