import tkinter as tk

from tkinter import ttk, filedialog
from apiparser import *


def app():
    SD = first_data_entry.get()
    ED = second_data_entry.get()
    file_id = second_entry.get()
    file_benz = entry.get()
    get_devices()
    get_stage(SD, ED)
    get_api_data(get_stage(SD, ED))
    get_id_and_serial()
    get_total_value(get_stage(SD, ED))
    get_id_card(file_id)
    get_benz_file(file_benz)
    from_api_to_sql_tank(get_api_data(get_stage(SD, ED)))
    from_api_to_sql_id_serial(get_id_and_serial())
    from_api_to_sql_tank_total(get_total_value(get_stage(SD, ED)))
    request_sql_from_api()
    request_sql_from_api_total()
    connect.commit()
    connect.close()
    print('Очеты готовы!')


def select_file_benz():
    file_path = filedialog.askopenfilename()
    return entry.insert(0, file_path)


def select_file_id():
    file_path = filedialog.askopenfilename()
    return second_entry.insert(0, file_path)


root = tk.Tk()
root.title('Автодор')
root.geometry("600x300+400+200")
button = ttk.Button(text='Загрузите файл Бенза', command=select_file_benz)
button.place(x=20, y=30, height=25, width=250)
entry = ttk.Entry(root)
entry.place(x=280, y=30, height=23, width=300)
second_button = ttk.Button(text='Загрузите файл Ид автограф и карточки', command=select_file_id)
second_button.place(x=20, y=60, height=25, width=250)
second_entry = ttk.Entry()
second_entry.place(x=280, y=60, height=23, width=300)
text = tk.Label(text='Введите начало периода по заправкам')
text.place(x=20, y=100)
first_data_entry = ttk.Entry(root)
first_data_entry.place(x=250, y=100)
second_text = tk.Label(text='Введите конец периода по заправкам')
second_text.place(x=20, y=130)
second_data_entry = ttk.Entry(root)
second_data_entry.place(x=250, y=130)
lbl = ttk.Label(text='Пример ввода даты: 20231101')
lbl.place(x=400, y=130)
done_button = ttk.Button(root, text='Готово', command=app)
done_button.place(x=250, y=170)
root.mainloop()
