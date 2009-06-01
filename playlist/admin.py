from fivesongs.playlist.models import Song, Playlist

from django.contrib import admin

class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'user', 'active',)
    list_filter = ('artist',)

class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('play_date', 'user', 'active', 'song1', 'song2', 'song3', 'song4', 'song5',)
    list_filter = ('active', 'user',)

admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(Song, SongAdmin)


