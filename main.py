"""
Chat Of Matrix - v1.0
Phase 1: Text Group Chat with Matrix Rain Effect
"""

import socket
import threading
import random
import time
from datetime import datetime

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, Line
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.widget import Widget
from kivy.properties import StringProperty, ListProperty, NumericProperty
import traceback
import sys
import os

def report_error(exc_type, exc_value, exc_traceback):
    error_text = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    # Telefonun ana dizinine error.txt yazar
    with open("/sdcard/error.txt", "w") as f:
        f.write(error_text)
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = report_error

# ─────────────────────────────────────────────
#  SERVER CONFIG
# ─────────────────────────────────────────────
SERVER_IP   = "192.168.1.76"
SERVER_PORT = 5555

# ─────────────────────────────────────────────
#  THEME CONSTANTS
# ─────────────────────────────────────────────
BLACK        = (0,    0,    0,    1)
GREEN_BRIGHT = (0,    1,    0,    1)       # #00FF00
GREEN_MID    = (0,    0.75, 0,    1)       # #00BF00
GREEN_DIM    = (0,    0.45, 0,    1)       # #007300
GREEN_GHOST  = (0,    0.25, 0,    0.55)
GREEN_PANEL  = (0,    0.08, 0,    0.85)
AMBER        = (1,    0.75, 0,    1)       # for "coming soon" tint

MATRIX_CHARS = "01アイウエオカキクケコサシスセソタチツテトナニヌネノ"

# ─────────────────────────────────────────────
#  MATRIX RAIN CANVAS WIDGET
# ─────────────────────────────────────────────
class MatrixRain(Widget):
    """Draws classic matrix rain directly on Kivy canvas."""

    COL_W  = dp(14)
    SPEED  = 0.07          # seconds per tick
    FADE   = 0.12          # alpha decay per step

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._labels = []
        self._streams = []
        self._event  = None
        self.bind(size=self._rebuild, pos=self._rebuild)

    def _rebuild(self, *_):
        self._streams = []
        if self._event:
            self._event.cancel()
        num_cols = max(1, int(self.width / self.COL_W))
        for c in range(num_cols):
            self._streams.append(self._new_stream(c))
        self._event = Clock.schedule_interval(self._tick, self.SPEED)

    def _new_stream(self, col):
        x      = self.x + col * self.COL_W
        length = random.randint(6, 22)
        speed  = random.uniform(0.8, 2.0)   # multiplier
        y_pos  = random.uniform(self.top, self.top + self.height * 1.5)
        chars  = [random.choice(MATRIX_CHARS) for _ in range(length)]
        return {"x": x, "y": y_pos, "speed": speed,
                "chars": chars, "len": length, "col": col}

    def _tick(self, dt):
        self.canvas.clear()
        with self.canvas:
            for s in self._streams:
                s["y"] -= self.COL_W * s["speed"]
                # respawn when off screen
                if s["y"] + s["len"] * self.COL_W < self.y:
                    self._streams[s["col"]] = self._new_stream(s["col"])
                    continue
                # mutate a random char each tick for glitch feel
                if random.random() < 0.25:
                    idx = random.randint(0, s["len"] - 1)
                    s["chars"][idx] = random.choice(MATRIX_CHARS)
                # draw chars top → bottom, bright head, fading tail
                for i, ch in enumerate(s["chars"]):
                    gy = s["y"] + i * self.COL_W
                    if gy > self.top or gy < self.y - self.COL_W:
                        continue
                    # brightness: head = white, rest = green fading
                    if i == 0:
                        Color(0.85, 1, 0.85, 0.95)
                    else:
                        alpha = max(0.0, 1.0 - i * self.FADE)
                        green = max(0.15, 0.9 - i * 0.06)
                        Color(0, green, 0, alpha)
                    lbl = CoreLabel(text=ch, font_size=sp(11),
                                    font_name="RobotoMono-Regular",
                                    color=(1, 1, 1, 1))
                    lbl.refresh()
                    texture = lbl.texture
                    Rectangle(texture=texture,
                               pos=(s["x"], gy),
                               size=(self.COL_W, self.COL_W))


# Kivy-native label rendering helper (avoids importing kivy.core at module level)
from kivy.core.text import Label as CoreLabel


# ─────────────────────────────────────────────
#  REUSABLE STYLED WIDGETS
# ─────────────────────────────────────────────
def green_label(text="", font_size=sp(14), bold=False, halign="left", **kw):
    lbl = Label(
        text=text, font_size=font_size, bold=bold,
        color=GREEN_BRIGHT, halign=halign,
        markup=True, **kw
    )
    lbl.bind(size=lambda l, s: setattr(l, 'text_size', s))
    return lbl


def matrix_button(text, on_press=None, bg=GREEN_DIM,
                  fg=GREEN_BRIGHT, size_hint_y=None, height=dp(44)):
    btn = Button(
        text=text, font_size=sp(13), bold=True,
        color=fg, background_normal="",
        background_color=bg,
        size_hint_y=size_hint_y, height=height
    )
    if on_press:
        btn.bind(on_press=on_press)
    return btn


def coming_soon_popup(feature):
    content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
    content.add_widget(Label(
        text=f"[b][color=00FF00]{feature}[/color][/b]\n\n"
             "[color=FFBF00]Bu özellik geliştirme aşamasındadır.\n"
             "Chat Of Matrix v2.0'da görüşürüz! 🚀[/color]",
        markup=True, font_size=sp(14), halign="center"
    ))
    close_btn = matrix_button("[ TAMAM ]", size_hint_y=None, height=dp(44))
    content.add_widget(close_btn)

    popup = Popup(
        title="// GELİŞTİRİLME AŞAMASINDA //",
        title_color=GREEN_BRIGHT,
        content=content,
        size_hint=(0.82, 0.48),
        background_color=(0, 0.06, 0, 0.97),
        separator_color=GREEN_MID,
        auto_dismiss=True
    )
    close_btn.bind(on_press=popup.dismiss)
    return popup


# ─────────────────────────────────────────────
#  LOGIN SCREEN
# ─────────────────────────────────────────────
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = FloatLayout()

        # Matrix rain background
        self.rain = MatrixRain(size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        root.add_widget(self.rain)

        # Dark overlay panel
        panel = BoxLayout(
            orientation="vertical",
            padding=dp(30), spacing=dp(18),
            size_hint=(0.88, None), height=dp(340),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        with panel.canvas.before:
            Color(*GREEN_PANEL)
            self._panel_bg = Rectangle()
        panel.bind(pos=self._update_bg, size=self._update_bg)

        # Title
        title = Label(
            text="[b][color=00FF00]C H A T   O F   M A T R I X[/color][/b]",
            markup=True, font_size=sp(22),
            size_hint_y=None, height=dp(50)
        )
        subtitle = Label(
            text="[color=007300]// v1.0 — Encrypted Group Channel //[/color]",
            markup=True, font_size=sp(11),
            size_hint_y=None, height=dp(24)
        )

        # Separator
        sep = Widget(size_hint_y=None, height=dp(1))
        with sep.canvas:
            Color(*GREEN_DIM)
            Line(points=[0, 0, 10000, 0], width=dp(1))

        # Nickname input
        nick_lbl = green_label(
            text="[b]> NİCKNAME GİR:[/b]",
            markup=True, font_size=sp(13),
            size_hint_y=None, height=dp(28)
        )
        self.nick_input = TextInput(
            hint_text="ör: Neo, Morpheus, Trinity...",
            hint_text_color=(0, 0.4, 0, 1),
            foreground_color=GREEN_BRIGHT,
            cursor_color=GREEN_BRIGHT,
            background_color=(0, 0.05, 0, 1),
            font_size=sp(15),
            multiline=False,
            size_hint_y=None, height=dp(46),
            padding=[dp(10), dp(12)]
        )
        self.nick_input.bind(on_text_validate=self._do_connect)

        # Status line
        self.status_lbl = Label(
            text="", markup=True,
            font_size=sp(11), color=GREEN_MID,
            size_hint_y=None, height=dp(22)
        )

        # Connect button
        conn_btn = matrix_button(
            "[ MATRİSE GİR ]",
            on_press=self._do_connect,
            bg=(0, 0.28, 0, 1), fg=GREEN_BRIGHT,
            size_hint_y=None, height=dp(50)
        )

        for w in [title, subtitle, sep, nick_lbl,
                  self.nick_input, self.status_lbl, conn_btn]:
            panel.add_widget(w)

        root.add_widget(panel)
        self.add_widget(root)

    def _update_bg(self, inst, _):
        self._panel_bg.pos  = inst.pos
        self._panel_bg.size = inst.size

    def _do_connect(self, *_):
        nick = self.nick_input.text.strip()
        if not nick:
            self.status_lbl.text = "[color=FF4444]> Lütfen bir nickname gir.[/color]"
            return
        if len(nick) > 20:
            self.status_lbl.text = "[color=FF4444]> Max 20 karakter.[/color]"
            return
        self.status_lbl.text = f"[color=00BF00]> {SERVER_IP}:{SERVER_PORT} bağlanılıyor...[/color]"
        app = App.get_running_app()
        app.nickname = nick
        threading.Thread(target=self._connect_thread, daemon=True).start()

    def _connect_thread(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((SERVER_IP, SERVER_PORT))
            sock.settimeout(None)
            App.get_running_app().sock = sock
            Clock.schedule_once(self._on_connected)
        except Exception as e:
            Clock.schedule_once(lambda dt: self._on_error(str(e)))

    def _on_connected(self, dt):
        app = App.get_running_app()
        # Send nickname handshake
        try:
            app.sock.sendall((app.nickname + "\n").encode("utf-8"))
        except Exception:
            pass
        self.status_lbl.text = "[color=00FF00]> Bağlantı kuruldu! Kanal açılıyor...[/color]"
        Clock.schedule_once(lambda dt: setattr(
            self.manager, "current", "chat"), 0.6)

    def _on_error(self, msg):
        self.status_lbl.text = f"[color=FF4444]> HATA: {msg}[/color]"


# ─────────────────────────────────────────────
#  BUBBLE WIDGET
# ─────────────────────────────────────────────
class MessageBubble(BoxLayout):
    def __init__(self, sender, text, ts, is_own=False, is_system=False, **kw):
        super().__init__(orientation="vertical",
                         size_hint_y=None, padding=dp(6),
                         spacing=dp(2), **kw)

        if is_system:
            lbl = Label(
                text=f"[color=007300][i]{text}[/i][/color]",
                markup=True, font_size=sp(11),
                size_hint_y=None,
                halign="center"
            )
            lbl.bind(texture_size=lambda l, s: setattr(l, 'height', s[1] + dp(4)))
            lbl.bind(size=lambda l, s: setattr(l, 'text_size', (s[0], None)))
            self.add_widget(lbl)
            self.bind(minimum_height=self.setter("height"))
            return

        align = "right" if is_own else "left"
        bg    = (0, 0.18, 0, 0.9) if is_own else (0, 0.1, 0, 0.9)
        border_color = GREEN_MID if is_own else GREEN_DIM

        inner = BoxLayout(
            orientation="vertical",
            size_hint_x=0.78,
            padding=dp(8), spacing=dp(3)
        )
        with inner.canvas.before:
            Color(*bg)
            self._bg = Rectangle()
            Color(*border_color)
            self._border = Line(width=dp(0.8))
        inner.bind(pos=self._upd, size=self._upd)

        nick_color = "00FF00" if is_own else "00BF00"
        header = Label(
            text=f"[b][color={nick_color}]{sender}[/color][/b]  "
                 f"[color=005500][size=10]{ts}[/size][/color]",
            markup=True, font_size=sp(11),
            size_hint_y=None, height=dp(18), halign="left"
        )
        header.bind(size=lambda l, s: setattr(l, 'text_size', s))

        body = Label(
            text=f"[color=00FF00]{text}[/color]",
            markup=True, font_size=sp(13),
            size_hint_y=None, halign="left"
        )
        body.bind(texture_size=lambda l, s: setattr(l, 'height', s[1] + dp(4)))
        body.bind(size=lambda l, s: setattr(l, 'text_size', (s[0], None)))

        inner.add_widget(header)
        inner.add_widget(body)
        inner.bind(minimum_height=inner.setter("height"))

        wrapper = BoxLayout(size_hint_y=None)
        if is_own:
            wrapper.add_widget(Widget())
        wrapper.add_widget(inner)
        if not is_own:
            wrapper.add_widget(Widget())
        wrapper.bind(minimum_height=wrapper.setter("height"))

        self.add_widget(wrapper)
        self.bind(minimum_height=self.setter("height"))

    def _upd(self, inst, _):
        self._bg.pos    = inst.pos
        self._bg.size   = inst.size
        x, y, w, h = inst.x, inst.y, inst.width, inst.height
        self._border.rectangle = (x, y, w, h)


# ─────────────────────────────────────────────
#  CHAT SCREEN
# ─────────────────────────────────────────────
class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._recv_thread = None

        root = FloatLayout()

        # Subtle background rain (low opacity)
        self.rain = MatrixRain(size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        root.add_widget(self.rain)

        # Dark overlay so chat is readable
        overlay = Widget(size_hint=(1, 1))
        with overlay.canvas:
            Color(0, 0, 0, 0.82)
            self._ov_rect = Rectangle()
        overlay.bind(size=lambda w, s: setattr(self._ov_rect, 'size', s),
                     pos= lambda w, p: setattr(self._ov_rect, 'pos',  p))
        root.add_widget(overlay)

        # Main column
        main = BoxLayout(
            orientation="vertical",
            size_hint=(1, 1),
            padding=[dp(0), dp(0)], spacing=0
        )

        # ── TOP BAR ──
        topbar = BoxLayout(
            size_hint_y=None, height=dp(52),
            padding=[dp(10), dp(6)], spacing=dp(8)
        )
        with topbar.canvas.before:
            Color(0, 0.1, 0, 0.97)
            self._tb_rect = Rectangle()
        topbar.bind(pos=self._upd_rect("_tb_rect"),
                    size=self._upd_rect("_tb_rect"))

        self.title_lbl = Label(
            text="[b][color=00FF00]CHAT OF MATRIX[/color][/b]  "
                 "[color=005500]// GRUP KANALI[/color]",
            markup=True, font_size=sp(13),
            size_hint_x=1, halign="left"
        )
        self.title_lbl.bind(size=lambda l, s: setattr(l, 'text_size', s))

        # Placeholder action buttons (top-right)
        for icon, feat in [("📷", "Fotoğraf Gönder"),
                            ("🎙️", "Sesli Mesaj"),
                            ("📞", "Sesli Arama"),
                            ("🎥", "Görüntülü Arama")]:
            btn = Button(
                text=icon, font_size=sp(18),
                size_hint=(None, None), size=(dp(36), dp(36)),
                background_normal="", background_color=(0, 0.15, 0, 1)
            )
            btn.bind(on_press=lambda b, f=feat:
                     coming_soon_popup(f).open())
            topbar.add_widget(btn)

        topbar.add_widget(self.title_lbl)
        main.add_widget(topbar)

        # ── CONNECTION STATUS BAR ──
        self.conn_bar = Label(
            text="[color=007300]> Bağlantı bekleniyor...[/color]",
            markup=True, font_size=sp(10),
            size_hint_y=None, height=dp(20),
            halign="center"
        )
        with self.conn_bar.canvas.before:
            Color(0, 0.05, 0, 1)
            self._cb_rect = Rectangle()
        self.conn_bar.bind(pos=self._upd_rect("_cb_rect"),
                           size=self._upd_rect("_cb_rect"))
        main.add_widget(self.conn_bar)

        # ── SCROLL / MESSAGE AREA ──
        self.scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False, do_scroll_y=True,
            bar_color=GREEN_DIM,
            bar_inactive_color=(0, 0.2, 0, 0.5)
        )
        self.msg_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None, spacing=dp(4),
            padding=[dp(6), dp(6)]
        )
        self.msg_box.bind(minimum_height=self.msg_box.setter("height"))
        self.scroll.add_widget(self.msg_box)
        main.add_widget(self.scroll)

        # ── INPUT ROW ──
        input_row = BoxLayout(
            size_hint_y=None, height=dp(54),
            padding=[dp(8), dp(6)], spacing=dp(6)
        )
        with input_row.canvas.before:
            Color(0, 0.08, 0, 0.97)
            self._ir_rect = Rectangle()
        input_row.bind(pos=self._upd_rect("_ir_rect"),
                       size=self._upd_rect("_ir_rect"))

        self.msg_input = TextInput(
            hint_text="> mesajını yaz...",
            hint_text_color=(0, 0.35, 0, 1),
            foreground_color=GREEN_BRIGHT,
            cursor_color=GREEN_BRIGHT,
            background_color=(0, 0.06, 0, 1),
            font_size=sp(14),
            multiline=False,
            size_hint=(1, None), height=dp(42),
            padding=[dp(10), dp(10)]
        )
        self.msg_input.bind(on_text_validate=self._send_msg)

        send_btn = matrix_button(
            "GÖNDER", on_press=self._send_msg,
            bg=(0, 0.28, 0, 1), fg=GREEN_BRIGHT,
            size_hint_y=None, height=dp(42)
        )
        send_btn.size_hint_x = None
        send_btn.width = dp(90)

        input_row.add_widget(self.msg_input)
        input_row.add_widget(send_btn)
        main.add_widget(input_row)

        root.add_widget(main)
        self.add_widget(root)

    # ── helpers ──
    def _upd_rect(self, attr):
        def _cb(inst, val):
            r = getattr(self, attr)
            r.pos  = inst.pos
            r.size = inst.size
        return _cb

    def on_enter(self):
        app = App.get_running_app()
        self.title_lbl.text = (
            f"[b][color=00FF00]CHAT OF MATRIX[/color][/b]  "
            f"[color=005500]// {app.nickname} @ GRUP KANALI[/color]"
        )
        self.conn_bar.text = (
            f"[color=00FF00]> Bağlandı: {SERVER_IP}:{SERVER_PORT}[/color]"
        )
        self._add_system(f"Hoş geldin, {app.nickname}! Kanal: MATRIX-1")
        # Start receive thread
        self._recv_thread = threading.Thread(
            target=self._recv_loop, daemon=True)
        self._recv_thread.start()

    def _add_system(self, text):
        Clock.schedule_once(lambda dt: self._insert_bubble(
            "", text, "", is_system=True))

    def _insert_bubble(self, sender, text, ts, is_own=False, is_system=False):
        bubble = MessageBubble(
            sender=sender, text=text, ts=ts,
            is_own=is_own, is_system=is_system
        )
        self.msg_box.add_widget(bubble)
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0), 0.1)

    def _send_msg(self, *_):
        text = self.msg_input.text.strip()
        if not text:
            return
        app  = App.get_running_app()
        full = f"{text}\n"
        try:
            app.sock.sendall(full.encode("utf-8"))
            ts  = datetime.now().strftime("%H:%M")
            self._insert_bubble(app.nickname, text, ts, is_own=True)
            self.msg_input.text = ""
        except Exception as e:
            self._add_system(f"GÖNDERME HATASI: {e}")

    def _recv_loop(self):
        app  = App.get_running_app()
        buf  = ""
        while True:
            try:
                data = app.sock.recv(4096)
                if not data:
                    Clock.schedule_once(lambda dt: self._add_system(
                        "Sunucu bağlantısı kesildi."))
                    break
                buf += data.decode("utf-8", errors="replace")
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    ts = datetime.now().strftime("%H:%M")
                    # Try to split "NICK: message" format
                    if ": " in line:
                        sender, msg = line.split(": ", 1)
                        is_own = (sender.strip() == app.nickname)
                        if not is_own:
                            Clock.schedule_once(lambda dt, s=sender, m=msg, t=ts:
                                self._insert_bubble(s, m, t, is_own=False))
                    else:
                        Clock.schedule_once(lambda dt, l=line:
                            self._add_system(l))
            except Exception as e:
                Clock.schedule_once(lambda dt, err=str(e):
                    self._add_system(f"BAĞLANTI HATASI: {err}"))
                break


# ─────────────────────────────────────────────
#  APP
# ─────────────────────────────────────────────
class ChatOfMatrixApp(App):
    nickname = StringProperty("Anonim")
    sock     = None

    def build(self):
        Window.clearcolor = (0, 0, 0, 1)
        self.title = "Chat Of Matrix"

        sm = ScreenManager(transition=FadeTransition(duration=0.4))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(ChatScreen(name="chat"))
        return sm

    def on_stop(self):
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass


if __name__ == "__main__":
    ChatOfMatrixApp().run()
