import logging
import datetime
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

from fivesongs.playlist.models import Playlist, Comment
from fivesongs.playlist.forms import CommentForm

@login_required
def show_home(request):
    """
    """
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

    return render_to_response(template_name, context, context_instance=RequestContext(request))

@login_required
def show_id(request, id, form=CommentForm):
    """
    """
    template_name = 'single.html'
    context = {}

    todaysdate = datetime.datetime.now().strftime("%Y-%m-%d")
    try:
        playlist = Playlist.objects.get(pk=id, active=True, play_date__lt=todaysdate)
    except ObjectDoesNotExist:
        playlist = None
        return HttpResponseRedirect('/')

    if str(playlist.play_date) == str(datetime.datetime.now().strftime("%Y-%m-%d")):
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

    context['playlist'] = playlist
    context['all_playlists'] = all_playlists
    context['comment_list'] = comments(request, id)
    context['commentform'] = form
    return render_to_response(template_name, context, context_instance=RequestContext(request))

@login_required
def comments(request, entry_id):
    """
    """
    if entry_id:
        try:
            comment_list = Comment.objects.filter(post=entry_id, publish=True).order_by('created_at')
            for comment in comment_list:
                comment.body = str(comment.body)
        except ObjectDoesNotExist:
            comment_list = None
    return comment_list

