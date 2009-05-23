import logging
import datetime

from django.conf import settings
from django.contrib.sites.models import Site
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string

from fivesongs.contact.forms import ContactForm

def contact(request):
    context = {}
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
	    sender = request.user.email
	    topic = form.cleaned_data['topic']
	    message = form.cleaned_data['message']
	    # request.POST['message']
            from django.core.mail import send_mail
            email_dict = { 'sender': sender, 'message': message, 'date': 'today' }
            email_dict['site'] = Site.objects.get_current()
            subject = "Contact message sent from " + str(email_dict['site']) + " : " + topic
            body = render_to_string('contact_notification.txt', email_dict)
            sent = send_mail(subject, body, settings.ADMIN_EMAIL, [settings.ADMIN_EMAIL])
	    # context['sender'] = sender
	    context['message'] = message
            # return HttpResponseRedirect('/')
    else:
        form = ContactForm() # An unbound form

    logging.debug('*******************')
    logging.debug(form)

    context['form'] = form

    return render_to_response('contact.html', context, context_instance=RequestContext(request))

