from django import forms

# 未使用


class ChoiceForm(forms.Form):
    choice_form = forms.BooleanField(required=False)

    def __init__(self, choice, lable, *args, **kwargs):
        super(ChoiceForm, self).__init__(*args, **kwargs)
        if choice.has_extra_data:
            pass
        self.choice_form.label = lable



