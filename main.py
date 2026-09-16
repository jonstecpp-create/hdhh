import threading
from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.graphics import Color, Rectangle
from kivy.uix.asyncimage import AsyncImage
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
import yt_dlp


class ColoredBoxLayout(BoxLayout):

  def __init__(self, bg_color=(0.07, 0.07, 0.07, 1), **kwargs):
    super().__init__(**kwargs)
    with self.canvas.before:
      Color(*bg_color)
      self.rect = Rectangle(size=self.size, pos=self.pos)
    self.bind(size=self._update_rect, pos=self._update_rect)

  def _update_rect(self, instance, value):
    self.rect.size = instance.size
    self.rect.pos = instance.pos


class SpotifyApp(App):

  def build(self):
    self.current_sound = None
    self.is_playing = False

    main_layout = ColoredBoxLayout(
        orientation='vertical', bg_color=(0.07, 0.07, 0.07, 1)
    )

    # 1. Bar Pencarian Atas
    header = ColoredBoxLayout(
        orientation='horizontal',
        size_hint_y=None,
        height=60,
        padding=10,
        spacing=10,
        bg_color=(0.1, 0.1, 0.1, 1),
    )
    self.search_input = TextInput(
        hint_text='Cari lagu atau artis...',
        multiline=False,
        background_color=(0.15, 0.15, 0.15, 1),
        foreground_color=(1, 1, 1, 1),
        hint_text_color=(0.6, 0.6, 0.6, 1),
        cursor_color=(0.11, 0.72, 0.33, 1),
    )
    btn_search = Button(
        text='Cari',
        size_hint_x=None,
        width=80,
        background_normal='',
        background_color=(0.11, 0.72, 0.33, 1),
        color=(0, 0, 0, 1),
        bold=True,
    )
    btn_search.bind(on_press=self.start_search)
    header.add_widget(self.search_input)
    header.add_widget(btn_search)
    main_layout.add_widget(header)

    # 2. Area Scroll Daftar Lagu
    self.scroll_view = ScrollView()
    self.results_list = BoxLayout(
        orientation='vertical', size_hint_y=None, spacing=8, padding=10
    )
    self.results_list.bind(minimum_height=self.results_list.setter('height'))
    self.scroll_view.add_widget(self.results_list)
    main_layout.add_widget(self.scroll_view)

    # 3. Mini Player Spotify (Bawah)
    self.mini_player = ColoredBoxLayout(
        orientation='horizontal',
        size_hint_y=None,
        height=70,
        padding=8,
        spacing=10,
        bg_color=(0.15, 0.15, 0.15, 1),
    )
    self.player_thumb = AsyncImage(
        source='', size_hint_x=None, width=54, allow_stretch=True
    )

    info_box = BoxLayout(orientation='vertical', padding=[5, 2])
    self.player_title = Label(
        text='Pilih lagu untuk diputar',
        bold=True,
        font_size=13,
        color=(1, 1, 1, 1),
        text_size=(200, None),
        shorten=True,
        halign='left',
        valign='middle',
    )
    self.player_artist = Label(
        text='SpotYt Player',
        font_size=11,
        color=(0.6, 0.6, 0.6, 1),
        text_size=(200, None),
        shorten=True,
        halign='left',
        valign='middle',
    )
    info_box.add_widget(self.player_title)
    info_box.add_widget(self.player_artist)

    self.btn_control = Button(
        text='▶',
        size_hint_x=None,
        width=50,
        background_normal='',
        background_color=(0.11, 0.72, 0.33, 1),
        color=(0, 0, 0, 1),
        bold=True,
    )
    self.btn_control.bind(on_press=self.toggle_play)

    self.mini_player.add_widget(self.player_thumb)
    self.mini_player.add_widget(info_box)
    self.mini_player.add_widget(self.btn_control)
    main_layout.add_widget(self.mini_player)

    return main_layout

  def start_search(self, instance):
    query = self.search_input.text.strip()
    if not query:
      return
    self.results_list.clear_widgets()
    self.results_list.add_widget(
        Label(
            text='Mencari di YouTube...',
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None,
            height=50,
        )
    )
    threading.Thread(
        target=self.fetch_results, args=(query,), daemon=True
    ).start()

  def fetch_results(self, query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'skip_download': True,
    }
    try:
      with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f'ytsearch6:{query}', download=False)
        videos = []
        for entry in info.get('entries', []):
          if entry:
            videos.append({
                'title': entry.get('title', 'Unknown Title'),
                'artist': entry.get('uploader', 'Unknown Artist'),
                'thumb': entry.get('thumbnail', ''),
                'webpage_url': entry.get('webpage_url', ''),
            })
        Clock.schedule_once(lambda dt: self.render_results(videos))
    except Exception:
      Clock.schedule_once(
          lambda dt: self.show_error('Gagal mengambil data lagu.')
      )

  def show_error(self, msg):
    self.results_list.clear_widgets()
    self.results_list.add_widget(
        Label(text=msg, color=(1, 0.3, 0.3, 1), size_hint_y=None, height=50)
    )

  def render_results(self, videos):
    self.results_list.clear_widgets()
    if not videos:
      self.show_error('Lagu tidak ditemukan.')
      return

    for video in videos:
      card = ColoredBoxLayout(
          orientation='horizontal',
          size_hint_y=None,
          height=65,
          padding=5,
          spacing=10,
          bg_color=(0.12, 0.12, 0.12, 1),
      )
      thumb = AsyncImage(
          source=video['thumb'], size_hint_x=None, width=55, allow_stretch=True
      )

      info = BoxLayout(orientation='vertical', padding=[2, 2])
      title_lbl = Label(
          text=video['title'],
          bold=True,
          font_size=12,
          color=(1, 1, 1, 1),
          text_size=(220, None),
          shorten=True,
          halign='left',
          valign='middle',
      )
      artist_lbl = Label(
          text=video['artist'],
          font_size=10,
          color=(0.6, 0.6, 0.6, 1),
          text_size=(220, None),
          shorten=True,
          halign='left',
          valign='middle',
      )
      info.add_widget(title_lbl)
      info.add_widget(artist_lbl)

      btn_play = Button(
          text='▶',
          size_hint_x=None,
          width=45,
          background_normal='',
          background_color=(0.11, 0.72, 0.33, 0.8),
          color=(0, 0, 0, 1),
          bold=True,
      )
      v_data = video
      btn_play.bind(on_press=lambda inst, v=v_data: self.play_song(v))

      card.add_widget(thumb)
      card.add_widget(info)
      card.add_widget(btn_play)
      self.results_list.add_widget(card)

  def play_song(self, video):
    self.player_thumb.source = video['thumb']
    self.player_title.text = video['title']
    self.player_artist.text = video['artist']
    self.btn_control.text = '❚❚'
    self.is_playing = True

    threading.Thread(
        target=self._get_audio_and_play,
        args=(video['webpage_url'],),
        daemon=True,
    ).start()

  def _get_audio_and_play(self, url):
    ydl_opts = {'format': 'bestaudio/best', 'quiet': True}
    try:
      with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info.get('url')
        if audio_url:
          if self.current_sound:
            self.current_sound.stop()
          self.current_sound = SoundLoader.load(audio_url)
          if self.current_sound:
            self.current_sound.play()
    except Exception as e:
      print('Play error:', e)

  def toggle_play(self, instance):
    if not self.current_sound:
      return
    if self.is_playing:
      self.current_sound.stop()
      self.btn_control.text = '▶'
      self.is_playing = False
    else:
      self.current_sound.play()
      self.btn_control.text = '❚❚'
      self.is_playing = True


if __name__ == '__main__':
  SpotifyApp().run()
