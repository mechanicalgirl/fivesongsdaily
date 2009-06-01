import datetime
from time import strftime

from django.contrib.syndication.feeds import Feed

from fivesongs.playlist.models import Playlist

class LatestPlaylists(Feed):
    title = ""
    link = ""
    description = ""

    def items(self):
        todaysdate = datetime.datetime.now().strftime("%Y-%m-%d")
        return Playlist.objects.filter(active=True).filter(play_date__lte=todaysdate).order_by('-play_date')[:5]

