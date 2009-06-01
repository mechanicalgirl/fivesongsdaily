import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseNotFound, Http404, HttpResponse, HttpResponseRedirect
from django import forms
from django.shortcuts import render_to_response
from django.template import RequestContext

from fivesongs.profiles.models import UserProfile, Avatar
from fivesongs.profiles.forms import UserProfileForm

@login_required
def searchband(request, bandname):
    """
    """
    template_name = 'search_results.html'
    context ={}
    try:
	profiles = UserProfile.objects.filter(visible=True, active=True, favorite_bands__contains=bandname)
    except ObjectDoesNotExist:
	profiles = None
    context['results'] = profiles
    context['band'] = bandname
    return render_to_response(template_name, context, context_instance=RequestContext(request))

@login_required
def view(request, username):
    """
    View the profile if it exists; return the create template if it doesn't.
    If the username in the request doesn't match the logged in user, return an error page.
    """
    template_name = 'view_profile.html'
    context = {}

    try:
	requested_user = User.objects.get(username=username)
        profile = UserProfile.objects.get(user=requested_user.id, active=True)
    except ObjectDoesNotExist:
	context['error_message'] = 'That user does not exist.'
        profile = None

    logging.debug(profile)

    permission = has_permission(request.user, request.user.username, username)
    if permission is True:
	logging.debug('**** OK - viewing your own profile')
	if not profile:
	    logging.debug('***** you havent created a profile yet, redir to edit')
	    return HttpResponseRedirect('/profile/edit/%s/' % request.user.username)
    else:
	if profile and profile.visible:
	    logging.debug('***** this user has allowed their profile to be visible to other users')
	    template_name = 'view_another_users_profile.html'
        else:
	    logging.debug('***** its not your profile, and the user has not made it visible to all')
	    context['error_message'] = 'You do not have permission to view this profile.'

    if profile:
	try:
	    avatar = Avatar.objects.get(user=requested_user.id)
	except ObjectDoesNotExist:
	    avatar = None
	context['avatar'] = avatar

	try:
	    favorite_bands = profile.favorite_bands
	except ObjectDoesNotExist:
	    favorite_bands = None

	if favorite_bands:
	    bands = []
	    band_list = favorite_bands.split (',')
	    for band in band_list:
		bands.append(band.strip())
	    context['bands'] = bands	

    context['profile'] = profile

    return render_to_response(template_name, context, context_instance=RequestContext(request))

@login_required
def edit(request, username):
    """
    Edit a user profile if it exists; create a new one if it doesn't.
    """
    context = {}
    template_name = 'edit_profile.html'
    form_class = UserProfileForm

    permission = has_permission(request.user, request.user.username, username)
    if permission is not True:
	context['error_message'] = 'You do not have permission to create/edit this profile.'

    try:
	profile = UserProfile.objects.get(user=request.user.id, active=True)
    except ObjectDoesNotExist:
        profile = None

    if request.method == 'POST':
        update_user = User.objects.get(username='%s' %username)
        update_user.email = request.POST['email']
        if profile:
            form = form_class(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                if update_user.email: update_user.save()
                profile = form.save(commit=False)
		profile.active = True
                profile.save()
                logging.debug('first save')
                logging.debug(profile.save())		
		# form.save()
                return HttpResponseRedirect('/profile/%s/' % request.user.username)
        else:
            form = form_class(request.POST)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user_id = request.user.id
		profile.active = True
                profile.save()
		logging.debug('save')
		logging.debug(profile.save())
                return HttpResponseRedirect('/profile/%s/' % request.user.username)
    else:
        form = form_class(instance=profile)
        form.email = request.user.email

    context['form'] = form
    context['profile'] = profile

    return render_to_response(template_name, context, context_instance=RequestContext(request))

def has_permission(request_user, request_username, username):
    """
    Username in the request must match the logged in user.
    """
    if cmp(request_username, username) != 0:
        return False
    return True

