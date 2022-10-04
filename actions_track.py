import json
import time
from pynput import keyboard, mouse
from screeninfo import get_monitors

class ActionsTrack:
    def __init__(self):
        # Запущена ли прослушка клавиатуры и мыши
        self.is_listening = False
        self.is_tracking = False
        # Прослушка клавиатуры
        self.keyboard_listener = None
        # Прослушка мыши
        self.mouse_listener = None
        # Клавиша для запуска или остановки макроса
        self.hotkey_macros_write = keyboard.Key.shift_r
        # Последовательность действий клавиатуры и мыши
        self.track = []
        # Множество нажатых клавиш
        self.pressed_keys = set()

    def _add_action(self, device, action, **kwargs):
        if action not in ['press', 'release', 'move', 'scroll']:
            raise ValueError('Wrong action name.')

        if device == 'keyboard':
            self.track.append({
                'device': device,
                'action': action,
                'key': kwargs['key']
            })
        elif device == 'mouse':
            action_dict = {
                'device': device,
                'action': action,
                'x': kwargs['x'],
                'y': kwargs['y']
            }
            if action == 'press' or action == 'release':
                action_dict['button'] = kwargs['button']
            if action == 'scroll':
                action_dict['dx'] = kwargs['dx']
                action_dict['dy'] = kwargs['dy']
            self.track.append(action_dict)
        else:
            raise ValueError('Wrong device name.')

    def clear(self):
        self.track = []

    # vvvv mouse vvvv

    def on_move_mouse(self, x, y):
        if self.is_tracking:
            pass

    def on_click_mouse(self, x, y, button, is_pressed):
        if self.is_tracking:
            self._add_action(
                'mouse',
                'press' if is_pressed else 'release',
                x=x,
                y=y,
                button=button
            )

    def on_scroll_mouse(self, x, y, dx, dy):
        if self.is_tracking:
            self._add_action(
                'mouse',
                'scroll',
                x=x,
                y=y,
                dx=dx,
                dy=dy
            )

    # ^^^^ mouse ^^^^
    # vvvv keyboard vvvv

    def on_press_keyboard(self, key):
        if key == self.hotkey_macros_write:
            # nothing
            pass
        elif self.is_tracking and key not in self.pressed_keys:
            self._add_action(
                'keyboard',
                'press',
                key=key
            )
            self.pressed_keys.add(key)

    def on_release_keyboard(self, key):
        if key == self.hotkey_macros_write:
            self.is_tracking = not self.is_tracking
        elif self.is_tracking:
            self._add_action(
                'keyboard',
                'release',
                key=key
            )
            self.pressed_keys.discard(key)

    # ^^^^ keyboard ^^^^

    def start(self):
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_press_keyboard,
            on_release=self.on_release_keyboard
        )
        self.mouse_listener = mouse.Listener(
            on_move=self.on_move_mouse,
            on_click=self.on_click_mouse,
            on_scroll=self.on_scroll_mouse
        )

        self.is_listening = True # !!!
        self.is_tracking = True
        self.keyboard_listener.start()
        self.mouse_listener.start()

    def pause(self):
        self.is_tracking = False

    def unpause(self):
        self.is_tracking = True

    def stop(self):
        self.is_listening = False # !!!
        self.is_tracking = False
        self.mouse_listener.stop()
        self.keyboard_listener.stop()

    def insert(self, index, actions_track):
        if self.length() <= index < 0: raise ValueError('Index incorrect.')
        self.track[index:index] = actions_track.track

    def run(self):
        keyboard_controller = keyboard.Controller()
        mouse_controller = mouse.Controller()

        for t in self.track:
            time.sleep(0.1)
            # Действия клавиатуры
            if t['device'] == 'keyboard':
                # Нажатие клавиши клавиатуры
                if t['action'] == 'press':
                    keyboard_controller.press(t['key'])
                # Отпуск клавиши клавиатуры
                elif t['action'] == 'release':
                    keyboard_controller.release(t['key'])

            # Действия мыши
            if t['device'] == 'mouse':
                # Движение мыши
                mouse_controller.move(
                    t['x'] - mouse_controller.position[0],
                    t['y'] - mouse_controller.position[1]
                )                
                # Прокручивание колёсика
                if t['action'] == 'scroll':
                    mouse_controller.scroll(t['dx'], t['dy'])
                # Нажатие клавиши мыши
                elif t['action'] == 'press':
                    mouse_controller.press(t['button'])
                # Отпуск клавиши мыши
                elif t['action'] == 'release':
                    mouse_controller.release(t['button'])

    # mouse_buttom_to_string = {
    #     mouse.Button.left: 'l',
    #     mouse.Button.right: 'r',
    #     mouse.Button.middle: 'm'
    # }
    # string_to_mouse_button = {v: k for k, v in mouse_buttom_to_string.items()}    
    # space_key_code = '000'

    def get_resolution():        
        # Значения разрешения главного экрана
        primary_monitor_resolution = {}
        # Получение данных о разрешении монитора
        for m in get_monitors():
            if m.is_primary:
                primary_monitor_resolution['width'] = m.width
                primary_monitor_resolution['height'] = m.height
                break
        return primary_monitor_resolution
    
    def to_relative_coord(x, y):
        resolution = ActionsTrack.get_resolution()
        return x / resolution['width'], y / resolution['height']

    def to_absolute_coord(x, y):
        resolution = ActionsTrack.get_resolution()
        return round(x * resolution['width']), round(y * resolution['height'])

    def to_json(self):        
        def convert(t):
            if 'key' in t:
                try:
                    t['key'] = t['key'].char
                except AttributeError:
                    t['key'] = str(t['key']).replace('Key.', '')
            elif 'button' in t:
                t['button'] = str(t['button']).replace('Button.', '')            
            if 'x' in t and 'y' in t:
                t['x'], t['y'] = ActionsTrack.to_relative_coord(t['x'], t['y'])
            return t

        return json.dumps([convert(t) for t in self.track], indent=4)

    def from_json(self, json_str):
        self.clear()
               
        def convert(t):
            if 'key' in t:
                if len(t['key']) == 1:
                    t['key'] = keyboard.KeyCode.from_char(t['key'])
                else:
                    t['key'] = keyboard.Key[t['key']]
            elif 'button' in t:
                t['button'] = mouse.Button[t['button']]
            if 'x' in t and 'y' in t:
                t['x'], t['y'] = ActionsTrack.to_absolute_coord(t['x'], t['y'])
            return t

        for t in json.loads(json_str):
            self._add_action(
                device=t['device'],
                action=t['action'],
                **{k: v for k, v in convert(t).items() if k not in ['device', 'action']}
            )

    def length(self):
        return len(self.track)

    def switch(self, first, second):
        self.track[first], self.track[second] = self.track[second], self.track[first]

    def get_action(self, index):
        if self.track[index]['device'] == 'keyboard':
            return f'{self.track[index]["action"]} {self.track[index]["key"]}'

        elif self.track[index]['device'] == 'mouse':
            return_string = f'{self.track[index]["action"]}'\
                            f' x - {self.track[index]["x"]}'\
                            f' y - {self.track[index]["y"]}'
            if self.track[index]["action"] == 'scroll':
                return_string += f' dx - {self.track[index]["dx"]}'\
                                 f' dy - {self.track[index]["dy"]}'
            elif (self.track[index]["action"] == 'press' or 
                  self.track[index]["action"] == 'release'):                
                return_string += f' button - {self.track[index]["button"]}'

            return return_string
