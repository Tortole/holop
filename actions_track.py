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
                action_dict['key'] = kwargs['key']
            if action == 'scroll':
                action_dict['dx'] = kwargs['dx']
                action_dict['dy'] = kwargs['dy']
            self.track.append(action_dict)
        else:
            raise ValueError('Wrong device name.')

    # vvvv mouse vvvv

    def on_move_mouse_track(self, x, y):
        if self.is_tracking:
            pass

    def on_click_mouse_track(self, x, y, button, is_pressed):
        if self.is_tracking:
            self._add_action(
                'mouse',
                'press' if is_pressed else 'release',
                x=x,
                y=y,
                key=button
            )


    def on_scroll_mouse_track(self, x, y, dx, dy):
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

    def on_press_keyboard_track(self, key):
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

    def on_release_keyboard_track(self, key):
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
            on_press=self.on_press_keyboard_track,
            on_release=self.on_release_keyboard_track
        )
        self.mouse_listener = mouse.Listener(
            on_move=self.on_move_mouse_track,
            on_click=self.on_click_mouse_track,
            on_scroll=self.on_scroll_mouse_track
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
                    mouse_controller.press(t['key'])
                # Отпуск клавиши мыши
                elif t['action'] == 'release':
                    mouse_controller.release(t['key'])

    mouse_buttom_to_string = {
        mouse.Button.left: 'l',
        mouse.Button.right: 'r',
        mouse.Button.middle: 'm'
    }
    string_to_mouse_button = {v: k for k, v in mouse_buttom_to_string.items()}    
    space_key_code = '000'

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

    def coord_to_string(x, y):
        resolution = ActionsTrack.get_resolution()
        return f'{x / resolution["width"]:.2f}{y / resolution["height"]:.2f}'

    def string_to_coord(str_coord):
        resolution = ActionsTrack.get_resolution()
        return round(float(str_coord[:4]) * resolution['width']), \
            round(float(str_coord[4:]) * resolution['height'])

    def key_to_string(key):
        try:
            return key.char
        except AttributeError:
            if key == keyboard.Key.space:
                return ActionsTrack.space_key_code
            return f'{str(key.value)[1:-1]:0>3}'

    def string_to_key(string):
        if len(string) > 1:
            if string == ActionsTrack.space_key_code:
                return keyboard.Key.space
            else:
                return keyboard.KeyCode.from_vk(int(string))
        else:
            return string

    def to_string(self):
        list_str = []
        for t in self.track:
            if t['device'] == 'mouse':
                if t['action'] == 'press':
                    list_str.append(
                        f'm'
                        f'{ActionsTrack.coord_to_string(t["x"], t["y"])}'
                        f'p'
                        f'{ActionsTrack.mouse_buttom_to_string[t["key"]]}'
                    )
                elif t['action'] == 'release':
                    list_str.append(
                        f'm'
                        f'{ActionsTrack.coord_to_string(t["x"], t["y"])}'
                        f'r'
                        f'{ActionsTrack.mouse_buttom_to_string[t["key"]]}'
                    )
                elif t['action'] == 'scroll':
                    list_str.append(
                        f'm'
                        f'{ActionsTrack.coord_to_string(t["x"], t["y"])}'
                        f's'
                        f'{t["dx"]:+}{t["dy"]:+}'
                    )
                elif t['action'] == 'move':
                    list_str.append(
                        f'm'
                        f'{ActionsTrack.coord_to_string(t["x"], t["y"])}'
                        f'm'
                    )

            elif t['device'] == 'keyboard':
                if t['action'] == 'press':
                    list_str.append(
                        f'kp'
                        f'{ActionsTrack.key_to_string(t["key"])}'
                    )
                elif t['action'] == 'release':
                    list_str.append(
                        f'kr'
                        f'{ActionsTrack.key_to_string(t["key"])}'
                    )
        
        return '--'.join(list_str)

    def from_string(self, track_str):
        self.track = []
        list_actions = track_str.split('--')
        for l_a in list_actions:
            # Действия клавиатуры
            if l_a[0] == 'k':
                key = ActionsTrack.string_to_key(l_a[2:])

                # Нажатие клавиши клавиатуры
                if l_a[1] == 'p':
                    self._add_action('keyboard', 'press', key=key)
                # Отпуск клавиши клавиатуры
                elif l_a[1] == 'r':
                    self._add_action('keyboard', 'release', key=key)

            # Действия мыши
            elif l_a[0] == 'm':
                position_dx, position_dy = ActionsTrack.string_to_coord(l_a[1:9])

                # Прокручивание колёсика
                if l_a[9] == 's':
                    dx = int(l_a[10:12])
                    dy = int(l_a[12:14])
                    self._add_action(
                        'mouse',
                        'scroll',
                        x=position_dx,
                        y=position_dy,
                        dx=dx,
                        dy=dy
                    )
                # Нажатие клавиши мыши
                elif l_a[9] == 'p':
                    self._add_action(
                        'mouse',
                        'press',
                        x=position_dx,
                        y=position_dy,
                        key=ActionsTrack.string_to_mouse_button[l_a[10]]
                    )
                # Отпуск клавиши мыши
                elif l_a[9] == 'r':
                    self._add_action(
                        'mouse',
                        'release',
                        x=position_dx,
                        y=position_dy,
                        key=ActionsTrack.string_to_mouse_button[l_a[10]]
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
                return_string += f' key - {self.track[index]["key"]}'

            return return_string
