import time
import PySimpleGUI as sg

from macros_recorder import MacrosRecorder


def key_to_tree_id(tree, key):
    '''Get id of tree element'''
    for k, v in tree.IdToKey.items():
        if v == key:
            return k
    return None


def tree_elements_move(tree, direction):
    '''Up or down tree elements'''
    # List of selected tree elements
    selected_elements = tree.Widget.selection()
    # If no one element selected then exit
    if len(selected_elements) == 0:
        return

    # Determine direction of the selected elements list iteration
    if direction == 'up':
        iter = -1
        # selected_elements = selected_elements
    elif direction == 'down':
        iter = 1
        selected_elements = selected_elements[::-1]

    # Getting the main elements of the tree
    treedata = tree.TreeData
    tree_root = treedata.tree_dict['']
    # Moving condition:
    # if the elements are not at the top edge when moving up
    # and not at the bottom edge when moving down
    index_first_element = tree_root.children.index(treedata.tree_dict[tree.IdToKey[selected_elements[0]]])
    if not ((direction == 'up' and index_first_element == 0) or
            (direction == 'down' and index_first_element == len(tree_root.children)-1)):
        # Moving all selected elements
        for s_e in selected_elements:
            # Getting current selected element
            node = treedata.tree_dict[tree.IdToKey[s_e]]
            index = tree_root.children.index(node)
            # Moving this element in tree
            tree_root.children[index], tree_root.children[index+iter] =\
                tree_root.children[index+iter], tree_root.children[index]
            # and swap in macro
            macro_record.swap(index, index+iter)

    # Keys of elements in tree that will then need to be selected
    key_to_select = [tree.IdToKey[s_e] for s_e in selected_elements]
    # Update elements in tree
    tree.update(values=treedata)
    # Selection of elements in tree previously selected by user
    tree_ids = [key_to_tree_id(tree, key) for key in key_to_select]
    if tree_ids:
        tree.Widget.see(tree_ids[0])
        tree.Widget.selection_set(tree_ids)


def add_macro(tree):
    '''Record and add new macro'''
    # Run new key tracker
    new_macros = MacrosRecorder()
    new_macros.start()
    # Waiting for stop key tracking
    while new_macros.is_recording:
        pass
    # Add new key to existing macros
    macro_record.insert(new_macros)
    treedata = tree.TreeData
    treedata_len = len(tree.IdToKey)
    for i in range(new_macros.length()):
        treedata.Insert('', i+treedata_len, new_macros.get_action(i), values=[])
    tree.update(values=treedata)

def delete_macro_actions(tree):
    '''Delete selected actions in macro'''
    # List of selected tree elements
    selected_elements = tree.Widget.selection()
    # If no one element selected then exit
    if len(selected_elements) == 0:
        return

    # Getting tree data
    treedata = tree.TreeData

    # Deleting selected tree elements
    for s_e in selected_elements:
        node = treedata.tree_dict[tree.IdToKey[s_e]]
        parent_node = treedata.tree_dict[node.parent]
        index = parent_node.children.index(node)
        macro_record.remove(index)
        parent_node.children.remove(node)
    tree.update(values=treedata)


def clear_macro(tree):
    '''Clearing macro record'''
    macro_record.clear()
    tree.update(values=sg.TreeData())


def run_macro():
    '''Running macro record with delay'''
    time.sleep(4)
    macro_record.run()


def load_macro(tree):
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
        macro_record.from_json(infile.read())
    treedata = sg.TreeData()
    for i in range(macro_record.length()):
        treedata.Insert('', i, macro_record.get_action(i), values=[])
    tree.update(values=treedata)


def save_macro(tree):
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
        outfile.write(macro_record.to_json())


# Macro
macro_record = MacrosRecorder()

# Creating pysimplegui window
layout = [
    [
        sg.Button('Move Up'), sg.Button('Move Down'), 
        sg.Button('Add'), sg.Button('Delete'), 
        # sg.Button('Change'),
        sg.Button('Clear'),
    ],
    [sg.Tree(
        data=sg.TreeData(),
        key='Macros tree',
        headings=['Nothing'],
        # select_mode=sg.TABLE_SELECT_MODE_BROWSE,
    )],
    [sg.Button('Run'), sg.Button('Load'), sg.Button('Save')],
]
window = sg.Window('Holop', layout, resizable=True, size=(700, 700), finalize=True)
window['Macros tree'].expand(True, True)
# Hide titles of columns
window['Macros tree'].Widget.configure(show='tree')

# Window event handling until it close
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    elif event == 'Move Up':
        tree_elements_move(window['Macros tree'], 'up')
    elif event == 'Move Down':
        tree_elements_move(window['Macros tree'], 'down')
    elif event == 'Add':
        add_macro(window['Macros tree'])
    elif event == 'Delete':
        delete_macro_actions(window['Macros tree'])
    # elif event == 'Change':
    #     print('Change not work yet')
    elif event == 'Clear':
        clear_macro(window['Macros tree'])
    elif event == 'Run':
        run_macro()
    elif event == 'Load':
        load_macro(window['Macros tree'])
    elif event == 'Save':
        save_macro(window['Macros tree'])

window.close()
