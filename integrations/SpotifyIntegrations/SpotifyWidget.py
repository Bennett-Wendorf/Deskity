from kivy.uix.relativelayout import RelativeLayout 
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
import threading
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dynaconf_settings import settings
from helpers.ArgHandler import Get_Args

# Logging
from logger.AppLogger import build_logger
# Build the logger object, using the argument for verbosity as the setting for debug log level
logger = build_logger(logger_name="Spotify Widget", debug=Get_Args().verbose)

from kivy.lang import Builder

Builder.load_file('./integrations/SpotifyIntegrations/kivyspotify.kv')

class SpotifyWidget(RelativeLayout):

    spotify = None

    current_title = StringProperty()
    current_album = StringProperty()
    current_artist = StringProperty()
    playing = BooleanProperty()
    track_duration = NumericProperty()
    curr_playback_time = NumericProperty()
    
    def __init__(self, **kwargs):

        # TODO: Find a way to truncate these so they don't look weird
        self.current_title = "No Song Playing"
        self.current_album = "No Song Playing"
        self.current_artist = "No Song Playing"
        self.playing = False
        self.track_duration = 100
        self.curr_playback_time = 0

        # Authorize the client
        self.spotify = self.Spotify_Auth()

        self.Start_Update_Loop()

        super(SpotifyWidget, self).__init__(**kwargs)

        Clock.schedule_interval(self.Start_Update_Loop, 5)

    def Get_Playing(self):
        logger.info("Running Get_Playing")
        current = self.spotify.current_playback()
        if(current is not None):
            self.playing = current['is_playing']
            self.current_title = current['item']['name']
            self.current_album = current['item']['album']['name']
            self.current_artist = ", ".join([str(x['name']) for x in current['item']['artists']]) 
            self.track_duration = current['item']['duration_ms']
            self.curr_playback_time = current['progress_ms']
            self.ids.album_art.source = current['item']['album']['images'][1]['url']

    def Toggle_Playback(self):
        logger.info("Running Toggle_Playback")
        try:
            if(self.playing):
                self.spotify.pause_playback()
            else:
                self.spotify.start_playback()
        except spotipy.SpotifyException as se:
            # TODO: Output message visibly to user when this is caught
            pass

    def Start_Update_Loop(self, *args):
        update_thread = threading.Thread(target=self.Get_Playing)
        update_thread.setDaemon(True)
        update_thread.start()

    def Spotify_Auth(self):
        return spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=settings.Spotify_Widget.client_id,
                                                          client_secret=settings.Spotify_Widget.client_secret,
                                                          redirect_uri='http://localhost:8888/redirect',
                                                          scope='user-library-read streaming app-remote-control user-read-playback-state'))