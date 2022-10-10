import base64
from io import BytesIO
from PIL import Image
import PySimpleGUI as sg

def update(x0, y0, x1, y1):
    """
    Update rectangle information
    """
    print(repr(x0), repr(y0), repr(x1), repr(y1))
    window['-START-'].update(f'Start: ({x0}, {y0})')
    window['-STOP-' ].update(f'Start: ({x1}, {y1})')
    window['-BOX-'  ].update(f'Box: ({abs(x1-x0+1)}, {abs(y1-y0+1)})')

# Generate an image with size (400, 400)
imgdata = base64.b64decode(sg.EMOJI_BASE64_HAPPY_LAUGH)
image = Image.open(BytesIO(imgdata))
im = image.resize((400, 400), resample=Image.CUBIC)
with BytesIO() as output:
    im.save(output, format="PNG")
    data = output.getvalue()

layout = [
    [sg.Graph((400, 400), (0, 0), (400, 400), key='-GRAPH-',
        drag_submits=True, enable_events=True, background_color='green')],
    [sg.Text("Start: None", key="-START-"),
     sg.Text("Stop: None",  key="-STOP-"),
     sg.Text("Box: None",   key="-BOX-")],
]

window = sg.Window("Measure", layout, finalize=True)
graph = window['-GRAPH-']
graph.draw_image(data=data, location=(0, 400))
x0, y0 = None, None
x1, y1 = None, None
colors = ['blue', 'white']
index = False
figure = None
while True:

    event, values = window.read(timeout=100)

    if event == sg.WINDOW_CLOSED:
        break
    elif event in ('-GRAPH-', '-GRAPH-+UP'):
        if (x0, y0) == (None, None):
            x0, y0 = values['-GRAPH-']
        x1, y1 = values['-GRAPH-']
        update(x0, y0, x1, y1)
        if event == '-GRAPH-+UP':
            x0, y0 = None, None

    if figure:
        graph.delete_figure(figure)
    if None not in (x0, y0, x1, y1):
        figure = graph.draw_rectangle((x0, y0), (x1, y1), line_color=colors[index])
        index = not index

window.close()