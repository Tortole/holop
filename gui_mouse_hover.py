import base64
from io import BytesIO
from PIL import Image
import PySimpleGUI as sg
import pyautogui as pag
import cv2
import numpy as np
import os
import time


def update(x0, y0, x1, y1, text=''):
    """
    Update rectangle information
    """
    print(repr(x0), repr(y0), repr(x1), repr(y1))
    window['-START-'].update(f'Start: ({x0}, {y0})')
    window['-STOP-' ].update(f'Start: ({x1}, {y1})')
    window['-BOX-'].update(f'Box: ({abs(x1-x0+1)}, {abs(y1-y0+1)})')
    window['-TEXT-'].update(f'Text: {text}')


def set_picture(im, back=False):
    window['-GRAPH-'].set_size(im.size)
    with BytesIO() as output:
        im.save(output, format="PNG")
        data = output.getvalue()
    print(window['-GRAPH-'].get_size())
    if back:
        graph.draw_image(data=data, location=(0, im.size[1]))
    else:
        graph.draw_image(data=data, location=(0, window['-GRAPH-'].get_size()[1]))
    width, height = im.size
    
    
def update_picture(x0, y0, x1, y1, image):
    if x0<x1 and y0<y1:
        im = image.crop((x0, y0, x1, y1))
    elif x0<x1 and y0>y1:
        im = image.crop((x0, y1, x1, y0))
    elif x0>x1 and y0>y1:
        im = image.crop((x1, y1, x0, y0))
    elif x0>x1 and y0<y1:
        im = image.crop((x1, y0, x0, y1))
    else:
        im = image
    #im.show()
    set_picture(im)
    return im


def make_screenshot(width, height):
    image = pag.screenshot()
    im = image.resize((width, height), resample=Image.CUBIC)
    with BytesIO() as output:
        im.save(output, format="PNG")
        data = output.getvalue()
    return data, im
    
# Generate an image with size (400, 400)
# imgdata = base64.b64decode(sg.EMOJI_BASE64_HAPPY_LAUGH)

# image = Image.open(BytesIO(imgdata))
# image_data = cv2.cvtColor(np.array(imgdata), cv2.COLOR_RGB2BGR)
# image = Image.open(imgdata)
# image = cv2.cvtColor(np.array(imgdata), cv2.COLOR_RGB2BGR)

#im = cv2.resize(image, (400, 400))
width, height = 1300, 700
layout = [
    [sg.Graph((width, height), (0, 0), (width, height), key='-GRAPH-',
        drag_submits=True, enable_events=True, background_color='green')],
    [sg.Text("Start: None", key="-START-"),
     sg.Text("Stop: None",  key="-STOP-"),
     sg.Text("Box: None",   key="-BOX-"),
     sg.Text("Text : None",   key="-TEXT-"),],
    [sg.Button('Обрезать', key="-CUT-"),
     sg.Button('Назад', key="-BACK-", visible=False),
     sg.Button('Сохранить', key="-SAVE-", visible=False)
     ],
]
data, original_screenshot = make_screenshot(width, height)
current_image = original_screenshot
window = sg.Window("Measure", layout, finalize=True)
graph = window['-GRAPH-']
graph.draw_image(data=data, location=(0, height))
x0, y0 = None, None
x1, y1 = None, None
x_f_0, y_f_0 = None, None
x_f_1, y_f_1 = None, None
colors = ['blue', 'white']
index = False
figure = None
figure_fix = None
cut_pucture = None
while True:

    event, values = window.read(timeout=100)
    print(event)
    if event == sg.WINDOW_CLOSED:
        break
    
    elif event in ('-GRAPH-', '-GRAPH-+UP'):
        if event == '-GRAPH-':
            graph.delete_figure(figure_fix)
        if (x0, y0) == (None, None):
            x0, y0 = values['-GRAPH-']
        
        x1, y1 = values['-GRAPH-']
        update(x0, y0, x1, y1)
        
        if event == '-GRAPH-+UP':
            graph.delete_figure(figure_fix)
            x_f_0, y_f_0, x_f_1, y_f_1 = x0, height-y0, x1, height-y1
            figure_fix = graph.draw_rectangle((x0, y0), (x1, y1), 
                                              line_color=colors[index])
            x0, y0 = None, None
            
    if figure:
        graph.delete_figure(figure)
    if None not in (x0, y0, x1, y1):
        figure = graph.draw_rectangle((x0, y0), (x1, y1), 
                                      line_color=colors[index])
        index = not index
    if event=="-CUT-":
        if figure_fix is None:
            update(0, 0, 0, 0, 'Не выделено фигуры')
        else:
            cut_pucture = update_picture(x_f_0, y_f_0, x_f_1, y_f_1, 
                                         current_image)
            window["-CUT-"].update(visible=False)
            window["-BACK-"].update(visible=True)
            window["-SAVE-"].update(visible=True)
            figure_fix = None
    if event=="-BACK-":
        set_picture(original_screenshot, back=True)
        window["-CUT-"].update(visible=True)
        window["-BACK-"].update(visible=False)
        window["-SAVE-"].update(visible=False)
        figure_fix = None
    if event=="-SAVE-":
        os.makedirs("images", exist_ok=True)
        timestr = time.strftime("%Y%m%d-%H%M%S")
        cut_pucture.save(f"images/cut_{timestr}.png")
        break
        
    

window.close()