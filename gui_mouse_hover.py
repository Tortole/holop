from io import BytesIO
from PIL import Image, ImageGrab
import PySimpleGUI as sg
import os
import time


def update(x0, y0, x1, y1, window, text=''):
    """
    Обновление текстовых форм
    """
    # print(repr(x0), repr(y0), repr(x1), repr(y1))
    window['-START-'].update(f'Start: ({x0}, {y0})')
    window['-STOP-'].update(f'Start: ({x1}, {y1})')
    window['-BOX-'].update(f'Box: ({abs(x1-x0+1)}, {abs(y1-y0+1)})')
    window['-TEXT-'].update(f'Text: {text}')


def set_picture(im, window, back=False):
    """
    Показ картинки в окошке
    """
    window['-GRAPH-'].set_size(im.size)
    graph = window['-GRAPH-']
    with BytesIO() as output:
        im.save(output, format="PNG")
        data = output.getvalue()
    # print(window['-GRAPH-'].get_size())
    if back:
        graph.draw_image(data=data, location=(0, im.size[1]))
    else:
        graph.draw_image(data=data, location=(0,
                                              window['-GRAPH-'].get_size()[1]))
    width, height = im.size


def update_picture(x0, y0, x1, y1, image):
    """
    Обрезка изображения
    """
    if x0 < x1 and y0 < y1:
        im = image.crop((x0, y0, x1, y1))
    elif x0 < x1 and y0 > y1:
        im = image.crop((x0, y1, x1, y0))
    elif x0 > x1 and y0 > y1:
        im = image.crop((x1, y1, x0, y0))
    elif x0 > x1 and y0 < y1:
        im = image.crop((x1, y0, x0, y1))
    else:
        im = image
    # im.show()
    return im


def make_screenshot(scale_parametr):
    """
    Скриншот страницы
    """
    image = ImageGrab.grab()
    width = int(scale_parametr*image.size[0])
    height = int(scale_parametr*image.size[1])
    im = image.resize((width, height), resample=Image.CUBIC)
    with BytesIO() as output:
        im.save(output, format="PNG")
        data = output.getvalue()
    return data, im, image, width, height


def make_cut_gui(scale_parametr=0.35):
    """
    Окошко для обрезки
    """
    data, current_image, original_screenshot, \
        width, height = make_screenshot(scale_parametr)
    layout = [
        [sg.Graph((width, height),
                  (0, 0),
                  (width, height),
                  key='-GRAPH-',
                  drag_submits=True,
                  enable_events=True,
                  background_color='green')],
        [sg.Text("Start: None", key="-START-"),
         sg.Text("Stop: None", key="-STOP-"),
         sg.Text("Box: None", key="-BOX-"),
         sg.Text("Text : None", key="-TEXT-")],
        [sg.Button('Обрезать', key="-CUT-"),
         sg.Button('Назад', key="-BACK-", visible=False),
         sg.Button('Сохранить', key="-SAVE-", visible=False)
         ],
    ]
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
    save_picture = None
    while True:
        event, values = window.read(timeout=100)
        # print(event)
        if event == sg.WINDOW_CLOSED:
            break
        elif event in ('-GRAPH-', '-GRAPH-+UP'):
            if event == '-GRAPH-':
                graph.delete_figure(figure_fix)
            if (x0, y0) == (None, None):
                x0, y0 = values['-GRAPH-']
            x1, y1 = values['-GRAPH-']
            update(x0, y0, x1, y1, window)
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
        if event == "-CUT-":
            if figure_fix is None:
                update(0, 0, 0, 0, window, 'Не выделено фигуры')
            else:
                cut_pucture = update_picture(x_f_0, y_f_0, x_f_1, y_f_1,
                                             current_image)
                set_picture(cut_pucture, window)
                save_picture = update_picture(x_f_0/scale_parametr,
                                              y_f_0/scale_parametr,
                                              x_f_1/scale_parametr,
                                              y_f_1/scale_parametr,
                                              original_screenshot)
                window["-CUT-"].update(visible=False)
                window["-BACK-"].update(visible=True)
                window["-SAVE-"].update(visible=True)
                figure_fix = None
        if event == "-BACK-":
            set_picture(original_screenshot.resize((width, height),
                                                   resample=Image.CUBIC),
                        window,
                        back=True)
            window["-CUT-"].update(visible=True)
            window["-BACK-"].update(visible=False)
            window["-SAVE-"].update(visible=False)
            figure_fix = None
        if event == "-SAVE-":
            os.makedirs("images", exist_ok=True)
            timestr = time.strftime("%Y%m%d-%H%M%S")
            filename = f"images/cut_{timestr}.png"
            save_picture.save(filename)
            break
    window.close()
    return filename
