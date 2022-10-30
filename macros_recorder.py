import json
import time
from pynput import keyboard, mouse
from screeninfo import get_monitors
from threading import Event

from find_image_on_screen import find_image_on_screen


class MacrosRecorder:
    '''Macros recorder'''
    def __init__(self):
        # Bool variables for listening and recording
        self.is_listening = False
        self.is_recording = False
        # Keyboard and mouse listeners
        self.keyboard_listener = None
        self.mouse_listener = None
        # Sequence of keyboard and mouse actions
        self.macro = []
        # A lot of currently pressed keys
        self.pressed_keys = set()
        # Event for block until wait next action
        self.wait_event = Event()
        # Last action
        self.last_action = None

    def _action_distributor(self, device, action, **kwargs):
        '''Distributes the action depending on the states'''
        if action not in ['press', 'release', 'move', 'scroll']:
            raise ValueError('Wrong action name.')
        if device == 'keyboard':
            action_dict = {
                'device': device,
                'action': action,
                'key': kwargs['key']
            }
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
        else:
            raise ValueError('Wrong device name.')

        self.last_action = action_dict
        if self.is_recording:
            self.macro.append(action_dict)

        # Call event
        self.wait_event.set()
        self.wait_event.clear()

    def wait_action(self):
        '''Wait next action'''
        # Wait event
        self.wait_event.wait()
        return self.last_action

    def remove(self, index):
        '''Remote action from macro by index'''
        del self.macro[index]

    def clear(self):
        '''Clearing macro'''
        self.macro = []

    def insert(self, other_macro_record, index=-1):
        '''Inserting in macro another macro'''
        if self.length() <= index < 0: raise ValueError('Index incorrect.')
        self.macro[index:index] = other_macro_record.macro

    def length(self):
        '''Getting count of actions on macro'''
        return len(self.macro)

    def swap(self, first, second):
        '''Swapping two actions in macro by index'''
        self.macro[first], self.macro[second] = self.macro[second], self.macro[first]

    # vvvvvvvv mouse vvvvvvvv

    def _on_move_mouse(self, x, y):
        '''Function that activated on mouse move'''
        pass

    def _on_click_mouse(self, x, y, button, is_pressed):
        '''Function that activated on mouse click'''
        self._action_distributor(
            'mouse',
            'press' if is_pressed else 'release',
            x=x,
            y=y,
            button=button
        )

    def _on_scroll_mouse(self, x, y, dx, dy):
        '''Function that activated on mouse scroll'''
        self._action_distributor(
            'mouse',
            'scroll',
            x=x,
            y=y,
            dx=dx,
            dy=dy
        )

    # vvvvvvvv keyboard vvvvvvvv

    def _on_press_keyboard(self, key):
        '''Function that activated on keyboar key press'''
        if key not in self.pressed_keys:
            self._action_distributor(
                'keyboard',
                'press',
                key=key
            )
            self.pressed_keys.add(key)

    def _on_release_keyboard(self, key):
        '''Function that activated on keyboar key release'''
        self._action_distributor(
            'keyboard',
            'release',
            key=key
        )
        self.pressed_keys.discard(key)

    # vvvvvvvv control macro vvvvvvvv

    def start_listen(self):
        '''Starting action listen'''
        assert not self.is_listening, 'Listen already start'
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_press_keyboard,
            on_release=self._on_release_keyboard
        )
        self.mouse_listener = mouse.Listener(
            on_move=self._on_move_mouse,
            on_click=self._on_click_mouse,
            on_scroll=self._on_scroll_mouse
        )

        self.is_listening = True
        self.is_recording = False
        self.pressed_keys.clear()
        self.keyboard_listener.start()
        self.mouse_listener.start()

    def stop_listen(self):
        '''Stopping action listen'''
        if self.is_listening:
            self.is_listening = False
            self.is_recording = False
            self.mouse_listener.stop()
            self.keyboard_listener.stop()

    def start_record(self):
        '''Starting macro recording'''
        assert self.is_listening, 'Listen not start'
        self.is_recording = True

    def stop_record(self):
        '''Stopping macro recording'''
        assert self.is_listening, 'Listen not start'
        self.is_recording = False

    def run(self):
        '''Running macro'''
        keyboard_controller = keyboard.Controller()
        mouse_controller = mouse.Controller()

        for m in self.macro:
            time.sleep(0.1)
            # Keyboard actions
            if m['device'] == 'keyboard':
                # Pressing keyboard key
                if m['action'] == 'press':
                    keyboard_controller.press(m['key'])
                # Releasing keyboard key
                elif m['action'] == 'release':
                    keyboard_controller.release(m['key'])

            # Mouse actions
            if m['device'] == 'mouse':
                # Moving mouse point
                # the move function in mouse controller
                # moves the pointer relative to current position
                if 'img_hover' in m:
                    x, y = find_image_on_screen(m['img_hover'])
                else:
                    x, y = m['x'], m['y']
                mouse_controller.move(
                    x - mouse_controller.position[0],
                    y - mouse_controller.position[1]
                )
                # Mouse scrolling
                if m['action'] == 'scroll':
                    mouse_controller.scroll(m['dx'], m['dy'])
                # Pressing mouse button
                elif m['action'] == 'press':
                    mouse_controller.press(m['button'])
                # Releasing mouse button
                elif m['action'] == 'release':
                    mouse_controller.release(m['button'])

    # vvvvvvvv export macro vvvvvvvv

    @staticmethod
    def _get_resolution():
        '''Getting resolution of primary monitor'''
        for m in get_monitors():
            if m.is_primary:
                return {'width': m.width, 'height': m.height}

    @staticmethod
    def _to_relative_coord(x, y):
        '''Getting relative mouse pointer coordinates from absolute'''
        resolution = MacrosRecorder.get_resolution()
        return x / resolution['width'], y / resolution['height']

    @staticmethod
    def _to_absolute_coord(x, y):
        '''Getting absolute mouse pointer coordinates from relative'''
        resolution = MacrosRecorder.get_resolution()
        return round(x * resolution['width']), round(y * resolution['height'])

    def to_json(self):
        '''Converting macro to JSON format'''
        def convert(m):
            '''Convert macro action to JSON element'''
            if 'key' in m:
                try:
                    m['key'] = m['key'].char
                except AttributeError:
                    m['key'] = str(m['key']).replace('Key.', '')
            elif 'button' in m:
                m['button'] = str(m['button']).replace('Button.', '')
            if 'x' in m and 'y' in m:
                m['x'], m['y'] = MacrosRecorder.to_relative_coord(m['x'], m['y'])
            return m

        return json.dumps([convert(t) for t in self.macro], indent=4)

    def from_json(self, json_str):
        '''Getting macro from JSON format'''
        self.clear()

        def convert(m):
            '''Convert JSON element to macro action'''
            if 'key' in m:
                if len(m['key']) == 1:
                    m['key'] = keyboard.KeyCode.from_char(m['key'])
                else:
                    m['key'] = keyboard.Key[m['key']]
            elif 'button' in m:
                m['button'] = mouse.Button[m['button']]
            if 'x' in m and 'y' in m:
                m['x'], m['y'] = MacrosRecorder.to_absolute_coord(m['x'], m['y'])
            return m

        for m in json.loads(json_str):
            self._add_action(
                device=m['device'],
                action=m['action'],
                **{k: v for k, v in convert(m).items() if k not in ['device', 'action']}
            )

    def get_action(self, index):
        '''Getting action in macro in string format'''
        if self.macro[index]['device'] == 'keyboard':
            if len(str(self.macro[index]["key"])) <= 3:
                return f'{self.macro[index]["action"]} {self.macro[index]["key"]}'
            else:
                return f'{self.macro[index]["action"]} {str(self.macro[index]["key"]).replace("Key.", "").upper()}'

        elif self.macro[index]['device'] == 'mouse':
            return_string = f'{self.macro[index]["action"]}'
            if self.macro[index]['action'] == 'scroll':
                dx_direction = {-1: ' left', 0: '', 1: ' right'}
                dy_direction = {-1: ' down', 0: '', 1: ' up'}
                return_string += f'{dx_direction[self.macro[index]["dx"]]}'\
                                 f'{dy_direction[self.macro[index]["dy"]]};'
            elif (self.macro[index]['action'] == 'press' or
                  self.macro[index]['action'] == 'release'):
                return_string += f' {str(self.macro[index]["button"]).replace("Button.", "").upper()} mouse button;'

            return_string += f' x: {self.macro[index]["x"]}'\
                             f' y: {self.macro[index]["y"]}'

            return return_string
