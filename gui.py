import PySimpleGUI as pg

def app():
    return

layout = [
    [pg.Text('Загрузите файл безн'), pg.InputText(), pg.FileBrowse()],
    [pg.Text('Загрузите файл ИдАвтографиКарточки'), pg.InputText(), pg.FileBrowse()],
    [pg.Button('Подтвердите ввод данных', enable_events=True, key='-FUNCTION-')]
]
window = pg.Window('Автодор', layout, size=(800, 500))
while True:
    event, values = window.read()
    if event in (None, 'Exit', 'Cancel', pg.WIN_CLOSED):
        break
    if event == '-FUNCTION-':
        app()

window.close()
