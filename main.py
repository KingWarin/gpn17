import os
import kivy
import subprocess
kivy.require('1.10.1')

from kivy.app import App
from kivy.adapters.models import SelectableDataItem
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.listview import ListView, ListItemButton
from kivy.uix.screenmanager import ScreenManager, Screen


def getContents():
    cwd = os.getcwd()
    content = os.listdir(cwd)
    directories = []
    files = []
    for item in content:
        if not item.startswith('.'):
            if os.path.isfile(cwd + '/' + item):
                files.append(item)
            else:
                directories.append(item)
    content = []
    for d in directories:
        content.append({'name': d, 'content_type': 'dir'})
    for f in files:
        content.append({'name': f, 'content_type': 'file'})
    return content


class ContentItem(SelectableDataItem):
    def __init__(self, name, content_type, is_selected=False, **kwargs):
        super(ContentItem, self).__init__(is_selected=is_selected, **kwargs)
        self.name = name
        self.content_type = content_type
        self.is_selected = is_selected


class ContentItemButton(ListItemButton):
    def __init__(self, content_type, **kwargs):
        super(ContentItemButton, self).__init__(**kwargs)
        self.on_press = self.handler_function
        self.content_type = content_type

    def handler_function(self):
        if self.content_type == 'dir':
            os.chdir(os.getcwd() + '/' + self.text)
            content = getContents()
            if not sm.has_screen(self.text):
                sm.add_widget(MenuScreen(name=self.text, contents=content, last_screen=sm.current))
            sm.current = self.text
        else:
            if not sm.has_screen(self.text):
                sm.add_widget(PlayScreen(name=self.text, display=output, last_screen=sm.current, compact=(output==4)))
            sm.current = self.text


class PlayScreen(Screen):
    def __init__(self, display=4, last_screen=None, compact=False, **kwargs):
        super(PlayScreen, self).__init__(**kwargs)
        screen = GridLayout(cols=2)
        compactScreen = GridLayout(rows=2)
        compactRow = GridLayout(cols=8, size_hint_y=None, height=100)

        self.display = str(display)

        def toggle_play(instance):
            self.proc.stdin.write('p')

        def back_callback(instance):
            self.proc.stdin.write('q')
            sm.current = last_screen
            sm.remove_widget(sm.get_screen(self.name))

        def vol_up(instance):
            self.proc.stdin.write('+')

        def vol_down(instance):
            self.proc.stdin.write('-')

        def ffwd(instance):
            self.proc.stdin.write('>')

        def jumpfwd(instance):
            self.proc.stdin.write('\x1B[C')

        def jumprwd(instance):
            self.proc.stdin.write('\x1B[D')

        def rwd(instance):
            self.proc.stdin.write('<')

        playbutton = Button(text='Play/Pause')
        backbutton = Button(text='back')
        fwdbutton = Button(text='FWD')
        rwdbutton = Button(text='RWD')
        jfwdbutton = Button(text='Jump+')
        jrwdbutton = Button(text='Jump-')
        volupbutton = Button(text='Vol+')
        voldownbutton = Button(text='Vol-')

        playbutton.bind(on_press=toggle_play)
        backbutton.bind(on_press=back_callback)
        fwdbutton.bind(on_press=ffwd)
        rwdbutton.bind(on_press=rwd)
        jfwdbutton.bind(on_press=jumpfwd)
        jrwdbutton.bind(on_press=jumprwd)
        volupbutton.bind(on_press=vol_up)
        voldownbutton.bind(on_press=vol_down)

        if not compact:
            screen.add_widget(playbutton)
            screen.add_widget(backbutton)
            screen.add_widget(rwdbutton)
            screen.add_widget(fwdbutton)
            screen.add_widget(jrwdbutton)
            screen.add_widget(jfwdbutton)
            screen.add_widget(volupbutton)
            screen.add_widget(voldownbutton)
            self.add_widget(screen)
        else:
            compactRow.add_widget(playbutton)
            compactRow.add_widget(backbutton)
            compactRow.add_widget(rwdbutton)
            compactRow.add_widget(fwdbutton)
            compactRow.add_widget(jrwdbutton)
            compactRow.add_widget(jfwdbutton)
            compactRow.add_widget(volupbutton)
            compactRow.add_widget(voldownbutton)
            compactScreen.add_widget(Label(text='', size_hint_y=None, height=380))
            compactScreen.add_widget(compactRow)
            self.add_widget(compactScreen)

    def on_enter(self):
#        self.proc = subprocess.Popen(["mplayer", self.name], stdin=subprocess.PIPE)
        self.proc = subprocess.Popen(["omxplayer", '-o', 'both', '-b', '--display', self.display, self.name], stdin=subprocess.PIPE)


class SettingsScreen(Screen):
    def __init__(self, last_screen, **kwargs):
        super(Screen, self).__init__(**kwargs)

        # Back Button
        def back_callback(self):
            sm.current = last_screen

        backButton = Button(text='back', size_hint_y=None, height=70)
        backButton.bind(on_press=back_callback)

        # Display output checkbox
        def change_output(self, value):
            global output
            if value:
                output = 5
            else:
                output = 4

        row = GridLayout(cols=2, size_hint_y=None, height=70)
        checkbox = CheckBox()
        checkbox.bind(active=change_output)
        row.add_widget(Label(text='Video2HDMI'))
        row.add_widget(checkbox)

        # Settings grid
        screen = GridLayout(rows=4)
        screen.add_widget(row)

        # Finally add back button
        screen.add_widget(backButton)
        self.add_widget(screen)


class MenuScreen(Screen):
    def __init__(self, contents, last_screen=None, hide_back=None, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        content_data_items = [ContentItem(c['name'], c['content_type']) for c in contents]
        content_data_converter = lambda row_index, selectable: {
                'text': selectable.name,
                'content_type': selectable.content_type,
                'size_hint_y': None,
                'height': 50
            }
        self.contents = ListAdapter(
                data=content_data_items,
                args_converter=content_data_converter,
                selection_mode='single',
                allow_empty_selection=False,
                cls=ContentItemButton
            )

        screen = GridLayout(
                rows=4
            )
        def back_callback(self):
            sm.current = last_screen
            os.chdir(os.getcwd() + '/..')

        def change_output(self, value):
            global output
            if value:
                output = 5
            else:
                output = 4

        def off_callback(self):
            app.stop()

        backbutton = Button(text='back')
        backbutton.bind(on_press=back_callback)

        # Settings checkbox
        row = GridLayout(cols=2, size_hint_y=None, height=70)
        checkbox = CheckBox()
        checkbox.bind(active=change_output)
        row.add_widget(Label(text='Video2HDMI'))
        row.add_widget(checkbox)

        # Settings Button
        def settings_callback(self):
            if not sm.has_screen('Settings'):
                sm.add_widget(SettingsScreen(name='Settings', last_screen=sm.current))
            sm.current = 'Settings'

        settings = Button(text='Settings', size_hint_y=None, height=50)
        settings.bind(on_press=settings_callback)

        # PowerOff Button
        offbutton = Button(text='Turn Off', size_hint_y=None, height=50)
        offbutton.bind(on_press=off_callback)
        list_view = ListView(adapter=self.contents)

        # Title
        screen.add_widget(Label(text='MediaCenter', size_hint_y=None, height=70))
        screen.add_widget(list_view)

        if not hide_back:
            screen.add_widget(backbutton)
        else:
            screen.add_widget(settings)
            screen.add_widget(offbutton)
        self.add_widget(screen)


sm = ScreenManager()
output = 4


class Media(App):
    def __init__(self, contents, **kwargs):
        global app
        super(Media, self).__init__(**kwargs)
        app = self
        self.raw_contents = contents

    def build(self):
        sm.add_widget(MenuScreen(name='home', contents=self.raw_contents, last_screen=sm.current, hide_back=True))
        return sm


if __name__ == '__main__':
    os.chdir(os.path.expanduser('~'))
    content = getContents()
    Media(content).run()

