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
        iter = 1
        select_elems = select_elems[::-1]

    # Получение основных элементов дерева
    treedata = tree.TreeData
    tree_root = treedata.tree_dict['']
    # Условие перемещение:
    # если элементы не у вехнего края при перемещении вверх
    # и не у нижнего края при перемещении вниз
    index_first_element = tree_root.children.index(treedata.tree_dict[tree.IdToKey[select_elems[0]]])
    if not ((direction == 'up' and index_first_element == 0) or
            (direction == 'down' and index_first_element == len(tree_root.children)-1)):
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