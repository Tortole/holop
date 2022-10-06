from actions_track import ActionsTrack

# https://github.com/PySimpleGUI/PySimpleGUI/issues/3441
import PySimpleGUI as sg


def key_to_tree_id(tree, key):
    for k, v in tree.IdToKey.items():
        if v == key:
            return k
    return None


# Поднимает или опускает выбранные элементы
def elements_elevator(tree, direction):
    # Список выбранных элементов
    select_elems = tree.Widget.selection()
    # Если ни один элемент не выбран, то выход
    if len(select_elems) == 0:
        return

    if direction == 'up':
        iter = -1
    elif direction == 'down':
        # len(parent_node.children)-1
        iter = 1
        select_elems = select_elems[::-1]

    # Получение основных элементов дерева
    treedata = tree.TreeData
    tree_root = treedata.tree_dict['']
    # Условие перемещение:
    # если элементы не у вехнего края при перемещении вверх
    # и не у нижнего края при перемещении вниз
    if tree_root.children.index(treedata.tree_dict[tree.IdToKey[select_elems[0]]]) not in [0, len(tree_root.children)-1]:
        # Перемещение всех выбранных элементов
        for s_e in select_elems:
            # Получение отмеченного элемента
            elem = treedata.tree_dict[tree.IdToKey[s_e]]
            index = tree_root.children.index(elem)
            # Перемещение этого элемента
            tree_root.children[index], tree_root.children[index+iter] =\
                tree_root.children[index+iter], tree_root.children[index]
            actions_tracker.switch(index, index+iter)

    # Ключи элементов в дереве, которые потом нужно будет выделить
    key_to_select = [tree.IdToKey[s_e] for s_e in select_elems]
    # Обновление дерева
    tree.update(values=treedata)
    # Выделение элементов в дереве, ранее выбранных пользователем
    tree_ids = [key_to_tree_id(tree, key) for key in key_to_select]
    if tree_ids:
        tree.Widget.see(tree_ids[0])
        tree.Widget.selection_set(tree_ids)


def load_macros(tree):
    macros_file = sg.popup_get_file(
        '',
        file_types=(('JSON files ', '*.json'),),
        no_window=True
    )
    with open(macros_file, 'r') as infile:
        actions_tracker.from_json(infile.read())
    
    treedata = sg.TreeData()
    for i in range(actions_tracker.length()):
        treedata.Insert('', i, actions_tracker.get_action(i), values=[])
    tree.update(values=treedata)


actions_tracker = ActionsTrack()

layout = [
    [
        # sg.Button('Up'), sg.Button('Down'), 
        sg.Button('Move Up'), sg.Button('Move Down'), 
        sg.Button('Add'), sg.Button('Delete'), 
        sg.Button('Change'), sg.Button('Clear'),
    ],
    [sg.Tree(
        data=sg.TreeData(),
        key='Track tree',
        headings=['Nothing'],
        # select_mode=sg.TABLE_SELECT_MODE_BROWSE,
    )],
    [sg.Button('Run'), sg.Button('Load'), sg.Button('Save')],
    # [sg.Button('Run'), sg.Button('Record')],
]

window = sg.Window('Holop', layout, resizable=True, size=(1000, 1000), finalize=True)
window['Track tree'].expand(True,True)
# Hide titles of columns
window['Track tree'].Widget.configure(show='tree')

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    elif event == 'Move Up':
        # move_up(window['Track tree'])
        elements_elevator(window['Track tree'], 'up')
    elif event == 'Move Down':
        # move_down(window['Track tree'])
        elements_elevator(window['Track tree'], 'down')
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
        load_macros(window['Track tree'])
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