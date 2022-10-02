from actions_track import ActionsTrack


# import PySimpleGUI as sg
#
# # help(sg.Column)
#
# test_list = list(range(20))
#
# def up_elem(button_key):
#     pass
#
# column1 = [
#     [sg.Button(f'up', key=f'up-{i}'), sg.Text(f'Scrollable {v}')] for i, v in enumerate(test_list)
# ]
#
# # column2 = [
# #     [sg.Text(f'Static{i}')] for i in range(10)
# # ]
#
# layout = [
#     [
#         sg.Column(column1, scrollable=True,  vertical_scroll_only=True, size=(1500, 600)),
#         # sg.Column(column2)
#     ]
# ]
#
# window = sg.Window(
#     'Scrollable',
#     layout,
#     # size=(2000, 1200)
# )
#
# while True:
#     event, values = window.read()
#     print(event)
#     print(values)
#     if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
#         break
#
# window.close()




# import PySimpleGUI as sg

# sg.theme('DarkAmber')   # Add a touch of color
# # All the stuff inside your window.
# layout = [  [sg.Text('Some text on Row 1')],
#             [sg.Text('Enter something on Row 2'), sg.InputText()],
#             [sg.Button('Ok'), sg.Button('Cancel')] ]

# # Create the Window
# window = sg.Window('Window Title', layout)
# # Event Loop to process "events" and get the "values" of the inputs
# while True:
#     event, values = window.read()
#     if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
#         break
#     print('You entered ', values[0])

# window.close()




# https://github.com/PySimpleGUI/PySimpleGUI/issues/3441
import PySimpleGUI as sg


def hide_header(tree):
    tree.Widget.configure(show='tree')


def key_to_id(tree, key):
    for k, v in tree.IdToKey.items():
        if v == key:
            return k
    return None


def select(tree, key=''):
    iid = key_to_id(tree, key)
    if iid:
        tree.Widget.see(iid)
        tree.Widget.selection_set(iid)


def where(tree):
    item = tree.Widget.selection()
    return '' if len(item) == 0 else tree.IdToKey[item[0]]


def move_up(tree):
    key =  where(tree)
    if key == '': return
    
    treedata = tree.TreeData
    node = treedata.tree_dict[key]
    parent_node = treedata.tree_dict[node.parent]
    index = parent_node.children.index(node)
    if index != 0:
        parent_node.children[index-1], parent_node.children[index] = (
            parent_node.children[index], parent_node.children[index-1])
        actions_tracker.switch(index-1, index)

    tree.update(values=treedata)
    select(tree, key)


def move_down(tree):
    key = where(tree)
    if key == '': return

    treedata = tree.TreeData
    node = treedata.tree_dict[key]
    parent_node = treedata.tree_dict[node.parent]
    index = parent_node.children.index(node)
    if index != len(parent_node.children)-1:
        parent_node.children[index+1], parent_node.children[index] = (
            parent_node.children[index], parent_node.children[index+1])
        actions_tracker.switch(index, index+1)

    tree.update(values=treedata)
    select(tree, key)


def load_macros(window):
    macros_file = sg.popup_get_file(
        '',
        file_types=(('TXT files ', '*.txt'),),
        no_window=True
    )
    with open(macros_file, 'r') as infile:
        actions_tracker.from_string(infile.read())
    
    treedata = sg.TreeData()
    for i in range(actions_tracker.length()):
        treedata.Insert('', i, actions_tracker.get_action(i), values=[f'key {i:0>2d}'])
    window.Element('TREE').update(values=treedata)


actions_tracker = ActionsTrack()

# fruits = [
#     "Apple", "Banana", "Cherry", "Durian", "Elderberry", "Guava", "Jackfruit",
#     "Kiwi", "Lemon", "Mango", "Orange", "Papaya", "Strawberry", "Tomato",
#     "Watermelon",
# ]

# treedata = sg.TreeData()
# for i, fruit in enumerate(fruits):
#     treedata.Insert('', i, fruit, values=[f'Fruit {i:0>2d}'])

layout = [
    [
        sg.Button('Move Up'), sg.Button('Move Down'), 
        sg.Button('Add'), sg.Button('Delete'), 
        sg.Button('Change'), sg.Button('Clear'),
    ],
    [sg.Tree(
        data=sg.TreeData(),
        key='TREE',
        headings=['Nothing'],
        select_mode=sg.TABLE_SELECT_MODE_BROWSE,
    )],
    [sg.Button('Run'), sg.Button('Load'), sg.Button('Save')],
]

window = sg.Window('Holop', layout, resizable=True, size=(500, 500), finalize=True)
window["TREE"].expand(True,True)
# tree = window['TREE']
hide_header(window['TREE'])

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    elif event == 'Move Up':
        move_up(window.Element('TREE'))
    elif event == 'Move Down':
        move_down(window.Element('TREE'))
    elif event == 'Add':
        print('Add not work yet')
    elif event == 'Delete':
        print('Delete not work yet')
    elif event == 'Change':
        print('Change not work yet')
    elif event == 'Clear':
        print('Clear not work yet')
    elif event == 'Run':
        print('Run not work yet')
    elif event == 'Load':
        load_macros(window)
    elif event == 'Save':
        print('Save not work yet')

window.close()


# import base64
# from io import BytesIO
# from PIL import Image
# import PySimpleGUI as sg

# def update(x0, y0, x1, y1):
#     """
#     Update rectangle information
#     """
#     print(repr(x0), repr(y0), repr(x1), repr(y1))
#     window['-START-'].update(f'Start: ({x0}, {y0})')
#     window['-STOP-' ].update(f'Start: ({x1}, {y1})')
#     window['-BOX-'  ].update(f'Box: ({abs(x1-x0+1)}, {abs(y1-y0+1)})')

# # Generate an image with size (400, 400)
# imgdata = base64.b64decode(sg.EMOJI_BASE64_HAPPY_LAUGH)
# image = Image.open(BytesIO(imgdata))
# im = image.resize((400, 400), resample=Image.CUBIC)
# with BytesIO() as output:
#     im.save(output, format="PNG")
#     data = output.getvalue()

# layout = [
#     [sg.Graph((400, 400), (0, 0), (400, 400), key='-GRAPH-',
#         drag_submits=True, enable_events=True, background_color='green')],
#     [sg.Text("Start: None", key="-START-"),
#      sg.Text("Stop: None",  key="-STOP-"),
#      sg.Text("Box: None",   key="-BOX-")],
# ]

# window = sg.Window("Measure", layout, finalize=True)
# graph = window['-GRAPH-']
# graph.draw_image(data=data, location=(0, 400))
# x0, y0 = None, None
# x1, y1 = None, None
# colors = ['blue', 'white']
# index = False
# figure = None
# while True:

#     event, values = window.read(timeout=100)

#     if event == sg.WINDOW_CLOSED:
#         break
#     elif event in ('-GRAPH-', '-GRAPH-+UP'):
#         if (x0, y0) == (None, None):
#             x0, y0 = values['-GRAPH-']
#         x1, y1 = values['-GRAPH-']
#         update(x0, y0, x1, y1)
#         if event == '-GRAPH-+UP':
#             x0, y0 = None, None

#     if figure:
#         graph.delete_figure(figure)
#     if None not in (x0, y0, x1, y1):
#         figure = graph.draw_rectangle((x0, y0), (x1, y1), line_color=colors[index])
#         index = not index

# window.close()