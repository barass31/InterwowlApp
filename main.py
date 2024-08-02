import pyttsx3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from playsound import playsound
import threading

class IntervalApp(App):
    def build(self):
        self.intervals = []
        self.current_interval_index = 0
        self.timer_running = False
        self.time_left = 0

        self.layout = BoxLayout(orientation='vertical')

        # Set background color (primary color)
        with self.layout.canvas.before:
            Color(0.2, 0.6, 0.8, 1)  # Blue background
            self.rect = Rectangle(size=(800, 600), pos=self.layout.pos)
            self.layout.bind(size=self.update_rect, pos=self.update_rect)

        # Create input fields
        self.duration_input = TextInput(hint_text='Czas w sekundach', multiline=False, background_color=(0.9, 0.9, 0.9, 1), foreground_color=(0, 0, 0, 1))
        self.description_input = TextInput(hint_text='Opis (opcjonalnie)', multiline=False, background_color=(0.9, 0.9, 0.9, 1), foreground_color=(0, 0, 0, 1))

        self.layout.add_widget(self.duration_input)
        self.layout.add_widget(self.description_input)

        # Create buttons with complementary colors
        self.add_button = Button(text='Dodaj', background_color=(0.8, 0.2, 0.2, 1))  # Red
        self.add_button.bind(on_press=self.add_interval)
        self.layout.add_widget(self.add_button)

        self.start_button = Button(text='Start', background_color=(0.8, 0.2, 0.2, 1))  # Red
        self.start_button.bind(on_press=self.start_timer)
        self.layout.add_widget(self.start_button)
        self.start_button.disabled = True  # Disable start button until intervals are added

        self.stop_button = Button(text='Stop', background_color=(0.8, 0.2, 0.2, 1))  # Red
        self.stop_button.bind(on_press=self.stop_timer)
        self.stop_button.disabled = True  # Disable stop button initially
        self.layout.add_widget(self.stop_button)

        self.finish_timer_button = Button(text='Zakończ', background_color=(0.8, 0.2, 0.2, 1))  # Red
        self.finish_timer_button.bind(on_press=self.finish_timer)
        self.finish_timer_button.disabled = True  # Disable finish timer button initially
        self.layout.add_widget(self.finish_timer_button)

        # Create labels
        self.intervals_label = Label(text='Interwały:', color=(1, 1, 1, 1))  # White text
        self.layout.add_widget(self.intervals_label)

        self.timer_label = Label(text='Timer: 00:00', color=(1, 1, 1, 1))  # White text
        self.layout.add_widget(self.timer_label)

        self.engine = pyttsx3.init()

        return self.layout

    def update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

    def add_interval(self, instance):
        duration = self.duration_input.text
        description = self.description_input.text
        if duration.isdigit():
            if description.strip() == "":
                description = "Bez opisu"
            self.intervals.append((int(duration), description))
            self.update_intervals_label()
            self.duration_input.text = ''
            self.description_input.text = ''
            self.start_button.disabled = False  # Enable start button when at least one interval is added

    def update_intervals_label(self):
        intervals_text = 'Interwały:\n'
        for duration, description in self.intervals:
            intervals_text += f'{description}: {duration} sek\n'
        self.intervals_label.text = intervals_text

    def start_timer(self, instance):
        if self.intervals and not self.timer_running:
            self.start_button.disabled = True
            self.stop_button.disabled = False
            self.finish_timer_button.disabled = False
            if self.time_left == 0 and self.current_interval_index < len(self.intervals):
                self.time_left, _ = self.intervals[self.current_interval_index]
            self.timer_running = True
            Clock.schedule_interval(self.update_timer, 1)
            self.read_description()

    def start_next_interval(self):
        if self.current_interval_index < len(self.intervals):
            self.time_left, description = self.intervals[self.current_interval_index]
            self.timer_running = True
            Clock.schedule_interval(self.update_timer, 1)
            self.read_description()
        else:
            self.timer_running = False
            self.timer_label.text = 'Timer: Zakończono'
            self.stop_button.disabled = True
            self.finish_timer_button.disabled = True
            self.start_button.text = 'Start'
            self.start_button.disabled = False

    def update_timer(self, dt):
        if self.time_left > 0:
            self.time_left -= 1
            minutes, seconds = divmod(self.time_left, 60)
            self.timer_label.text = f'Timer: {minutes:02}:{seconds:02}'
        else:
            Clock.unschedule(self.update_timer)
            self.play_beep()
            self.current_interval_index += 1
            if self.current_interval_index < len(self.intervals):
                self.start_next_interval()
            else:
                self.timer_running = False
                self.timer_label.text = 'Timer: Zakończono'
                self.stop_button.disabled = True
                self.finish_timer_button.disabled = True
                self.start_button.text = 'Start'
                self.start_button.disabled = False

    def stop_timer(self, instance):
        if self.timer_running:
            Clock.unschedule(self.update_timer)
            self.timer_running = False
            self.start_button.text = 'Wznów'
            self.start_button.disabled = False

    def finish_timer(self, instance):
        Clock.unschedule(self.update_timer)
        self.timer_running = False
        self.time_left = 0
        self.current_interval_index = 0
        self.timer_label.text = 'Timer: Zakończono'
        self.start_button.text = 'Start'
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.finish_timer_button.disabled = True

    def play_beep(self):
        threading.Thread(target=lambda: playsound('beep.mp3')).start()

    def read_description(self):
        if self.current_interval_index < len(self.intervals):
            description = self.intervals[self.current_interval_index][1]
            threading.Thread(target=lambda: self.engine.say(description)).start()
            self.engine.runAndWait()

if __name__ == '__main__':
    IntervalApp().run()
