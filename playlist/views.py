import logging
import time, datetime
from datetime import timedelta
from time import strftime

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string

from fivesongs.playlist.models import Song, Playlist
from fivesongs.playlist.forms import SongForm, PlaylistForm
from fivesongs.profiles.models import Avatar

@login_required
def show_home(request):
    template_name = 'home.html'
    context = {}

    todaysdate = datetime.datetime.now().strftime("%Y-%m-%d")
    try:
	playlist = Playlist.objects.get(play_date=todaysdate, active=True)
    except ObjectDoesNotExist:
	playlist = None

    try:
        all_playlists = Playlist.objects.filter(active=True).filter(play_date__lt=todaysdate).order_by('-play_date')[:4]
    except ObjectDoesNotExist:
        all_playlists = None
    
    context['playlist'] = playlist
    context['all_playlists'] = all_playlists

    return render_to_response(template_name, context, context_instance=RequestContext(request))

@login_required
def show_all(request):
    template_name = 'archive.html'
    context = {}
    per_page = 5
    page = int(request.GET.get('page', '1'))

    todaysdate = datetime.datetime.now().strftime("%Y-%m-%d")
    try:
        all_playlists = Playlist.objects.filter(active=True).filter(play_date__lt=todaysdate).order_by('-play_date')
    except ObjectDoesNotExist:
	all_playlists = None

    total_entries = all_playlists.count()
    total_pages = (total_entries/per_page)+1
    context['page_range'] = range(1, total_pages+1)

    offset = (page * per_page) - per_page
    limit = offset + per_page
    all_playlists = all_playlists[offset:limit]
    context['all_playlists'] = all_playlists
    context['today'] = todaysdate

    return render_to_response(template_name, context, context_instance=RequestContext(request))

@login_required
def show_id(request, id):
    """
    """
    template_name = 'single.html'
    context = {}

    todaysdate = datetime.date.today()
    try:
        playlist = Playlist.objects.get(pk=id, active=True, play_date__lt=todaysdate)
        last_week = todaysdate - datetime.timedelta(days=7)
        if playlist.play_date < last_week:
	    playlist.song1.filepath = None
	    playlist.song2.filepath = None
	    playlist.song3.filepath = None
	    playlist.song4.filepath = None
	    playlist.song5.filepath = None
    except ObjectDoesNotExist:
        playlist = None
        return HttpResponseRedirect('/')
    
    if playlist.play_date == todaysdate:
	template_name = 'home.html'

    try:
        all_playlists = Playlist.objects.filter(active=True).filter(play_date__lt=todaysdate).order_by('-play_date')[:4]
    except ObjectDoesNotExist:
        all_playlists = None

    if request.method == 'POST':  # new comment
        form = form(request.POST)
        logging.debug('form')
        logging.debug(form)
        if form.is_valid():
            form.post_id = entry.id
            form.publish = True
            form.save()
            return HttpResponseRedirect('/id/%s/' % entry.id)
        else:
            form = form()

    context['today'] = todaysdate
    context['playlist'] = playlist
    context['all_playlists'] = all_playlists
    return render_to_response(template_name, context, context_instance=RequestContext(request))

@login_required
def preview_id(request, id):
    template_name = 'preview.html'
    context = {}

    if request.user.is_superuser:
        try:
	    playlist = Playlist.objects.get(pk=id, active=True)
	except ObjectDoesNotExist:
	    playlist = None
	    return HttpResponseRedirect('/')
    else:
        playlist = None
        return HttpResponseRedirect('/')

    context['playlist'] = playlist
    return render_to_response(template_name, context, context_instance=RequestContext(request))

@login_required
def user_song_upload(request):
    template_name = 'song_add.html'
    context = {}
    form_class = SongForm
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
	logging.debug('******* file size ***********')
	logging.debug(request.FILES['filepath'].size)
	if request.FILES['filepath'].size < 5457045 and form.is_valid():
            song = form.save(commit=False)
            song.active = True
            song.user = request.user
            song.save()
	    return HttpResponseRedirect('/playlist/upload/success/')
	else:
	    logging.debug('********* file too large ***************')
	    return HttpResponseRedirect('/playlist/upload/error/')

@login_required
def user_playlist(request, message):
    template_name = 'playlist_save.html'
    context = {}
    form_class = PlaylistForm

    try:
        user_songs = Song.objects.filter(user=request.user)
    except ObjectDoesNotExist:
        user_songs = None
    context['song_select'] = user_songs

    try:
        user_pending_playlists = Playlist.objects.filter(user=request.user, active=False).order_by('-created_at')
    except ObjectDoesNotExist:
        user_pending_playlists = None
    context['user_pending_playlists'] = user_pending_playlists

    try:
        user_queued_playlists = Playlist.objects.filter(user=request.user, active=True).order_by('-created_at')
    except ObjectDoesNotExist:
        user_queued_playlists = None
    context['user_queued_playlists'] = user_queued_playlists

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.active = False
            playlist.user = request.user
            playlist.save()

            # notify admin of new list
            from django.core.mail import send_mail
            email_dict = {'user': request.user, 'user_id': request.user.id}
            email_dict['site'] = Site.objects.get_current()
            subject = "New playlist uploaded by " + request.user.username
            body = render_to_string('message_notification.txt', email_dict)
            sent = send_mail(subject, body, settings.ADMIN_EMAIL, [settings.ADMIN_EMAIL])
            logging.debug('SENT: %s' %sent)

        else:
            logging.debug('*************** not valid %s', form.errors)
    else:
        form = form_class()

    context['form'] = form
    context['form_song'] = SongForm()

    if message == 'error': 
	context['upload_message'] = 'Sorry, that file was too large.'
    if message == 'success': 
	context['upload_message'] = 'Your file was uploaded successfully.'
    logging.debug('*************** message **************')
    logging.debug(message)

    return render_to_response(template_name, context, context_instance=RequestContext(request))

