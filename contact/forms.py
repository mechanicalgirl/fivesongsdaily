from django import forms

class ContactForm(forms.Form):

    TOPIC_CHOICES = (
	('', ''),
        ('PLY', 'Suggest A Playlist'),
        ('BUG', 'Report A Bug'),
        ('OTR', 'Other'),
    )

    topic = forms.CharField(label='Topics', max_length=3, widget=forms.Select(choices=TOPIC_CHOICES))
    message = forms.CharField(label='Your Message', widget=forms.Textarea, error_messages={'required': 'Please enter a message.'})

