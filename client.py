import PySimpleGUI as sg
import os
import requests

APP_SWITCHER_WIN_TITLE = 'app_switcher12345'

#  sg.theme('DarkAmber')   # Add a touch of color
# All the stuff inside your window.
layout = [[sg.Input(key='-INPUT-', enable_events=True)],
          [sg.Text("", size=(40,1), key='-OUTPUT-')],
          [sg.Button('1', bind_return_key=True, visible=False)]]

# Create the Window
window = sg.Window(APP_SWITCHER_WIN_TITLE, layout, finalize=True)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    try:
        input_chars = values['-INPUT-']
        r = requests.get('http://localhost:8888/get', params={'input_chars': input_chars})
        wid = r.json()["id"]
        window['-OUTPUT-'].update(f'{wid}')
        os.system(f"wmctrl -i -a {wid}")
        os.system(f"wmctrl -R {APP_SWITCHER_WIN_TITLE}")
    except Exception as e:
        window['-OUTPUT-'].update(f'ERR: {e}')

    if event == sg.WINDOW_CLOSED or event == 'Quit':
        break
    
    if event == '1':
        break

window.close()
r = requests.get('http://localhost:8888/flush_visited')
