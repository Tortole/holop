import time

from actions_track import ActionsTrack

# https://github.com/PySimpleGUI/PySimpleGUI/issues/3441
import PySimpleGUI as sg


def key_to_tree_id(tree, key):
    for k, v in tree.IdToKey.items():
        if v == key:
            return k
    return None


# Поднимает или опускает выбранные элементы
def nodes_elevator(tree, direction):
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
            node = treedata.tree_dict[tree.IdToKey[s_e]]
            index = tree_root.children.index(node)
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


def add_macros(tree):
    ''''''
    # Run new key tracker
    new_macros = ActionsTrack()
    new_macros.start()
    # Waiting for stop key tracking
    while new_macros.is_tracking:
        pass
    # Add new key to existing macros
    actions_tracker.insert(new_macros)
    treedata = tree.TreeData
    treedata_len = len(tree.IdToKey)
    for i in range(new_macros.length()):
        treedata.Insert('', i+treedata_len, new_macros.get_action(i), values=[])
    tree.update(values=treedata)

def delete_selected(tree):
    # Список выбранных элементов
    select_elems = tree.Widget.selection()
    # Если ни один элемент не выбран, то выход
    if len(select_elems) == 0:
        return

    # Получение основных элементов дерева
    treedata = tree.TreeData

    # Удаление выбранных элементов
    for s_e in select_elems:
        node = treedata.tree_dict[tree.IdToKey[s_e]]
        parent_node = treedata.tree_dict[node.parent]
        index = parent_node.children.index(node)
        actions_tracker.remove(index)
        parent_node.children.remove(node)

    # Обновление дерева
    tree.update(values=treedata)


def clear_tree(tree):
    actions_tracker.clear()
    tree.update(values=sg.TreeData())


def run_tracker():
    time.sleep(4)
    actions_tracker.run()


def load_macros(tree):
    '''Load macros file with browse dialog'''
    # User choose file
    macros_file = sg.popup_get_file(
        '',
        file_types=(('JSON files ', '*.json'),),
        no_window=True
    )
    # If file not chosen
    if macros_file == '':
        return
    # Read file and fill tree
    with open(macros_file, 'r') as infile:
        actions_tracker.from_json(infile.read())
    treedata = sg.TreeData()
    for i in range(actions_tracker.length()):
        treedata.Insert('', i, actions_tracker.get_action(i), values=[])
    tree.update(values=treedata)


def save_macros(tree):
    '''Save macros to file with browse dialog'''
    # Chose path to save file and its name
    save_file = sg.popup_get_file(
        '',
        file_types=(('JSON files ', '*.json'),),
        no_window=True,
        save_as=True
    )
    # Save
    with open(save_file, 'w') as outfile:
        outfile.write(actions_tracker.to_json())


actions_tracker = ActionsTrack()

layout = [
    [
        sg.Button('Move Up'), sg.Button('Move Down'), 
        sg.Button('Add'), sg.Button('Delete'), 
        # sg.Button('Change'),
        sg.Button('Clear'),
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
        nodes_elevator(window['Track tree'], 'up')
    elif event == 'Move Down':
        nodes_elevator(window['Track tree'], 'down')
    elif event == 'Add':
        add_macros(window['Track tree'])
    elif event == 'Delete':
        delete_selected(window['Track tree'])
    # elif event == 'Change':
    #     print('Change not work yet')
    elif event == 'Clear':
        clear_tree(window['Track tree'])
    elif event == 'Run':
        run_tracker()
    elif event == 'Load':
        load_macros(window['Track tree'])
    elif event == 'Save':
        save_macros(window['Track tree'])

window.close()
