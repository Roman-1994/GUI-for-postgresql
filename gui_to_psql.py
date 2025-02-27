import sys
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror, showwarning
import psycopg2
from psycopg2 import Error
import re
from tkinter import colorchooser
from tkinter.filedialog import asksaveasfilename
from tkinter.colorchooser import askcolor

connection = None
cursor = None
count_click_e_w_request = 0
count_row_history = 0
list_users = [{'имя пользователя':'user', 'пароль пользователя':'1', 'ip адрес базы данных':'1', 'порт базы данных':'1', 'имя базы данных':'1'}]

def save_user(k, user):
    if k == 1 and user not in list_users:
        list_users.append(user)
        print(list_users)
        return True
    elif k == 1 and user in list_users:
        print(list_users)
        return True
    return False

def connect_bd():
    global connection, cursor
    cred_user_bd = {'имя пользователя':e_user.get(), 'пароль пользователя':e_passwd.get(), 'ip адрес базы данных':e_host.get(), 'порт базы данных':e_port.get(), 'имя базы данных':e_database.get()}
    try:
        if all(cred_user_bd.values()):
            connection = psycopg2.connect(user=e_user.get(),
                                          # пароль, который указали при установке PostgreSQL
                                          password=e_passwd.get(),
                                          host=e_host.get(),
                                          port=e_port.get(),
                                          database=e_database.get())

            if connection:
                if save_user(state_save_user.get(), cred_user_bd):
                    showinfo(title='Дополнительная информация', message='Соединение с PostgreSQL установленно. Учетная запись сохранена.')
                else:
                    showinfo(title='Дополнительная информация', message='Соединение с PostgreSQL установленно.')
                l_help.configure(text='Соединение с БД установленно')
                b_request.configure(state='enabled')
                b_light_request.configure(state='enabled')
                b_connect.configure(state='disabled')
        
            cursor = connection.cursor()
        else:
            cred = [i for i in cred_user_bd if cred_user_bd[i] == '']
            showerror(title='Дополнительная информация', message=f'Заполните пожалуйста поля: {cred}')
    except (Exception, Error) as error:
        l_help.configure(text="Ошибка при работе с PostgreSQL")
        
        showerror(title='Дополнительная информация', message=str(error))

def disconnect_bd():
    global connection, cursor
    if connection:
        cursor.close()
        connection.close()
        showinfo(title='Дополнительная информация', message="Соединение с PostgreSQL закрыто")
        l_help.configure(text="Соединение с PostgreSQL закрыто")
        connection = None
        b_request.configure(state='disabled')
        b_light_request.configure(state='disabled')
        b_connect.configure(state='enabled')
        name_user.set(value='')
        password.set(value='')
        host.set(value='')
        port.set(value='')
        database.set(value='')
        value_connect_progress(None)
    else:
        showinfo(title='Дополнительная информация', message="Соединение с PostgreSQL не было установлено")
        l_help.configure(text='Соединение не установлено')

def create_request():
    global count_click_e_w_request, count_row_history
    
    windows_reguest = Toplevel(root)
    windows_reguest.title('Запрос к базе данных')
    
    windows_reguest.iconphoto(False, file)
    
    def request_bd(request):
        global count_row_history
        count_row_history += 1
        try:
            list_w_request_history.insert(0, str(count_row_history)+': '+str(request))
            type_request = str(request).split()[0].lower()
            if  type_request == 'select':
                cursor.execute(request)
                result = list(cursor.fetchall())
                result_var = Variable(value=(lambda: result if len(result) > 0 else '0_строк_соответствуют_условиям_запроса')())
                list_w_answer.configure(listvariable=result_var)
            elif type_request in ['update', 'delete', 'insert']:
                cursor.execute(request)
                dict_word = {'update':'обновлено', 'delete':'удалено', 'insert':'добавлено'}
                count_row = cursor.rowcount
                count_row_var = Variable(value=str(count_row)+(lambda: f"_Запись_успешно_{dict_word[type_request]}" if count_row > 0 else f"_Записей_{dict_word[type_request]}")())
                list_w_answer.configure(listvariable=count_row_var)
            elif type_request in ['create', 'drop', 'alter']:
                cursor.execute(request)
                table_cr_dr_al = {'create': 'создана', 'drop': 'удалена', 'alter': 'изменена'}
                count_table_var = Variable(value=(f'Таблица {table_cr_dr_al[type_request]}', ))
                list_w_answer.configure(listvariable=count_table_var)
            elif type_request == 'текст':
                err_mes_var = Variable(value=('Введите корректный запрос', ))
                list_w_answer.configure(listvariable=err_mes_var)
            else:
                cursor.execute(request)
            
            l_w_help.configure(text="")
            
        except (Exception, Error) as error:
            l_w_help.configure(text="Ошибка при написании запроса: "+str(error))
            err_mes_var = Variable(value=('Введите корректный запрос', ))
            list_w_answer.configure(listvariable=err_mes_var)

        connection.commit()
    
    def clear_e_w_request(event):
        global count_click_e_w_request
        if count_click_e_w_request == 0:
            e_w_request.delete(0, END)
            e_w_request.configure(foreground='#000000')
        count_click_e_w_request += 1
    
    def delete_history():
        del_his = list_w_request_history.curselection()
        j = 0
        if del_his:
            for i in del_his:
                list_w_request_history.delete(i-j)
                j += 1
        else:
            showinfo(title='Дополнительная информация', message="Не выбран элемент для удаления")
    
    def active_button(event):
        if list_w_request_history.curselection():
            b_w_delete_history.configure(state='enabled')
    
    def save_history_new():
        list_save_history = list(map(lambda x : x + '\n', list_w_request_history.get(0, list_w_request_history.size())))
        if len(list_save_history) > 0:
            filename = asksaveasfilename(initialdir='/home/localadm')
            if filename:
                with open(filename, '+at', encoding='utf-8') as f:
                    f.writelines(list_save_history)
                showinfo(title='Дополнительная информация', message=f"История сохранена в файле {filename}")
        else:
            showerror(title='Дополнительная информация', message=f"История не может быть пустой")
    
    def save_history():
        windows_save_history = Toplevel(root)
        windows_save_history.title('Сохранение истории')
    
        windows_save_history.iconphoto(False, file)
        
        def last_save_history():
            list_save_history = list(map(lambda x : x + '\n', list_w_request_history.get(0, list_w_request_history.size())))
            if len(list_save_history) > 0:
                with open(e_wsh_path.get(), '+at', encoding='utf-8') as f:
                    f.writelines(list_save_history)
                showinfo(title='Дополнительная информация', message=f"История сохранена в файле {e_wsh_path.get()}")
            else:
                showerror(title='Дополнительная информация', message=f"История не может быть пустой")
            windows_save_history.destroy()
        
        l_wsh_path = ttk.Label(windows_save_history, text='Введите место сохранения и имя файла')
        l_wsh_path.pack()
        
        e_wsh_path = Entry(windows_save_history)
        e_wsh_path.pack()
        
        b_wsh = ttk.Button(windows_save_history, text='Сохранить', command=last_save_history)
        b_wsh.pack()
        
        l_wsh_help = ttk.Label(windows_save_history, text='Внимание! Если вы укажите только имя файла, то файл сохранится в папке проекта!', font=('Arial', 10), wraplength=250)
        l_wsh_help.pack()
        
        windows_save_history.grab_set()
    
    l_w_request = ttk.Label(windows_reguest, text='Введите запрос:')
    l_w_request.pack()
    
    e_w_request = ttk.Entry(windows_reguest, width=150, foreground='#C1CDCD')
    e_w_request.pack()
    e_w_request.insert(0, 'Текст запроса')
        
    b_w_clear_request = ttk.Button(windows_reguest, text='Очистить запрос', command=lambda: e_w_request.delete(0, END))
    b_w_clear_request.pack()
    
    b_w_request = ttk.Button(windows_reguest, text='Выполнить запрос', command=lambda: request_bd(e_w_request.get()))
    b_w_request.pack()
    
    l_w_help = Label(windows_reguest, text='Результат:')
    l_w_help.pack(expand=YES)
    
    list_w_answer = Listbox(windows_reguest, listvariable='', height=8, width=150)
    list_w_answer.pack()
    
    l_w_help = Label(windows_reguest, text='История запросов:')
    l_w_help.pack(expand=YES)
    
    list_w_request_history = Listbox(windows_reguest, height=8, width=150, selectmode=MULTIPLE)
    list_w_request_history.pack()
    
    b_w_delete_history = ttk.Button(windows_reguest, text='Удалить выбранный элемент', command=delete_history, state='disabled')
    b_w_delete_history.pack()
    
    b_w_save_history = ttk.Button(windows_reguest, text='Сохранить историю', command=save_history)
    b_w_save_history.pack()
    
    b_wsh_new = ttk.Button(windows_reguest, text='Сохранить историю как', command=save_history_new)
    b_wsh_new.pack()
    
    l_w_help = Label(windows_reguest, text='')
    l_w_help.pack(expand=YES)
    
    e_w_request.bind('<ButtonPress-1>', clear_e_w_request)
    list_w_request_history.bind('<Enter>', active_button)
    
    windows_reguest.grab_set()
    count_click_e_w_request = 0
    count_row_history = 0

def check_host_ip_addr(address):
    result = str(address).split('.')
    if (len(result) == 4 and all(i.isdigit() for i in result) and all(0 <= int(i) <= 255 for i in result)):
        err_host_ip.set('')
        return True
    else:
        err_host_ip.set('Некорректный ip адрес')
        return False

def check_port_bd(port):
    if str(port) == '00':
        err_port.set('Некорректный порт')
        return False
    if str(port).isdigit() and int(port) <= 65535:
        err_port.set('')
        return True
    elif port == '':
        err_port.set('')
        return True
    else:
        err_port.set('Некорректный порт')
        return False

def check_name(*args):
    
    if name_user.get() == '':
        check_name_user.set('')
    elif name_user.get() in ['localadm', 'postgres']:
        check_name_user.set('Корректный логин')
    else:
        check_name_user.set('Некорректный логин')

def create_light_request():
    windows_light_request = Toplevel(root)
    windows_light_request.title('Упрощенный запрос к базе данных')
    
    windows_light_request.iconphoto(False, file)
    
    requests = ['SELECT', 'UPDATE', 'DELETE', 'INSERT', 'CREATE', 'ALTER', 'DROP']
    template_request = {'SELECT':'SELECT (2) FROM (1) WHERE (3) GROUP BY (5) ORDER BY (4)', 
                        'UPDATE':'UPDATE (1) SET (3) WHERE (4)', 
                        'DELETE':'DELETE  FROM (1) WHERE (4)', 
                        'INSERT':'INSERT INTO (1)(6) VALUES(6)', 
                        'CREATE':'CREATE TABLE (1)(7)', 
                        'ALTER':'ALTER TABLE (1) (8)', 
                        'DROP':'DROP TABLE IF EXISTS (1)'
                        }
    
    def choice_request():
        value_e_wl_request.set(template_request[value_request.get()])
        
    def light_request_bd(request):
        print(request)
        try:
            type_request = str(request).split()[0].lower()
            if  type_request == 'select':
                cursor.execute(request)
                result = list(cursor.fetchall())
                result_var = Variable(value=(lambda: result if len(result) > 0 else '0_строк_соответствуют_условиям_запроса')())
                list_wl_answer.configure(listvariable=result_var)
            elif type_request in ['update', 'delete', 'insert']:
                cursor.execute(request)
                dict_word = {'update':'обновлено', 'delete':'удалено', 'insert':'добавлено'}
                count_row = cursor.rowcount
                count_row_var = Variable(value=str(count_row)+(lambda: f"_Запись_успешно_{dict_word[type_request]}" if count_row > 0 else f"_Записей_{dict_word[type_request]}")())
                list_wl_answer.configure(listvariable=count_row_var)
            elif type_request in ['create', 'drop', 'alter']:
                cursor.execute(request)
                table_cr_dr_al = {'create': 'создана', 'drop': 'удалена', 'alter': 'изменена'}
                count_table_var = Variable(value=(f'Таблица {table_cr_dr_al[type_request]}', ))
                list_wl_answer.configure(listvariable=count_table_var)
            elif type_request == 'текст':
                err_mes_var = Variable(value=('Введите корректный запрос', ))
                list_wl_answer.configure(listvariable=err_mes_var)
            else:
                cursor.execute(request)
            
        except (Exception, Error) as error:
            err_mes_var = Variable(value=('Введите корректный запрос'+str(error), ))
            list_wl_answer.configure(listvariable=err_mes_var)
    
        connection.commit()
    
    l_wl_request = ttk.Label(windows_light_request, text='Выберите тип запроса')
    l_wl_request.pack()
    
    value_request = StringVar()
    value_e_wl_request = StringVar()
    
    for request in requests:
        rbn_request = ttk.Radiobutton(windows_light_request, text=request, value=request, variable=value_request, command=choice_request)
        rbn_request.pack()
    
    e_wl_request = ttk.Entry(windows_light_request, textvariable=value_e_wl_request, width=150)
    e_wl_request.pack()
        
    b_wl_request = ttk.Button(windows_light_request, text='Выполнить запрос', command=lambda: light_request_bd(e_wl_request.get()))
    b_wl_request.pack()
    
    list_wl_answer = Listbox(windows_light_request, listvariable='', height=8, width=150)
    list_wl_answer.pack()
    
    windows_light_request.grab_set()

def value_connect_progress(event):
    progress = 0
    if e_database.get() != '':
        progress += 20
    if e_port.get() != '':
        progress += 20
    if e_host.get() != '':
        progress += 20
    if e_passwd.get() != '':
        progress += 20
    if e_user.get() != '':
        progress += 20
    value_progress.set(value=progress)
    if progress == 100:
        l_progress_connect['text'] = 'Все поля заполнены! Можно подключаться к БД'
        c_save_user.configure(state=ACTIVE)
    else:
        l_progress_connect['text'] = ''
        c_save_user.configure(state=DISABLED)

def auto_user(event):
    for user in list_users:
        if name_user.get() in user.values():
            password.set(value=user['пароль пользователя'])
            host.set(value=user['ip адрес базы данных'])
            port.set(value=user['порт базы данных'])
            database.set(value=user['имя базы данных'])

def root_exit():
    root.destroy()

def aqua_background():
    root.configure(bg='#00FFFF')
    
def banana_background():
    root.configure(bg='#E3CF57')

def cadetblue_background():
    root.configure(bg='#5F9EA0')

def font_changed(font=None, color=None):
    for i in [l_user, l_passwd, l_host, l_port, l_database]:
        i['font'] = font
        i['foreground'] = color
    
def select_font():
    root.tk.call('tk', 'fontchooser', 'configure', '-font', l_user['font'], '-command', root.register(font_changed))
    root.tk.call('tk', 'fontchooser', 'show')

def select_color_font():
    result = colorchooser.askcolor()
    font_changed(color=result[1])

root = Tk()
root.title('connect_to_psql')

err_host_ip = StringVar()
err_port = StringVar()
name_user = StringVar()
password = StringVar()
host = StringVar()
port = StringVar()
database = StringVar()
check_name_user = StringVar()
value_progress = IntVar(value=0)
state_save_user = IntVar()

file = PhotoImage(file='1.png')
root.iconphoto(False, file)

root_menu = Menu()

file_menu = Menu()

file_menu.add_command(label='Дополнительное подключение')
file_menu.add_separator()
file_menu.add_command(label='Выход', command=root_exit)

color_menu = Menu()

background_color_menu = Menu()

background_color_menu.add_command(label='Aqua', command=aqua_background)
background_color_menu.add_command(label='Banana', command=banana_background)
background_color_menu.add_command(label='Cadetblue', command=cadetblue_background)

color_menu.add_command(label='Шрифта', command=select_color_font)
color_menu.add_cascade(label='Фона', menu=background_color_menu)

def new_color_background():
    (triple, hexstr) = askcolor()
    if hexstr:
        root.configure(bg=hexstr)

color_menu.add_command(label='Фона new', command=new_color_background) #command=lambda: root.configure(bg=[askcolor()[1]])()) - Выполняется, но с ошибкой

view_menu = Menu()
    
view_menu.add_cascade(label='Цвет', menu=color_menu)
view_menu.add_command(label='Шрифт', command=select_font)

root_menu.add_cascade(label='Файл', menu=file_menu)
root_menu.add_cascade(label='Вид', menu=view_menu)
root_menu.add_cascade(label='О программе')


l_user = ttk.Label(root, text='Введите имя пользователя:')
l_user.pack()

e_user = ttk.Entry(root, textvariable=name_user)
e_user.pack()

name_user.trace_add('write', check_name)

l_check_name = ttk.Label(root, textvariable=check_name_user)
l_check_name.pack()

l_passwd = ttk.Label(root, text='Введите пароль пользователя:')
l_passwd.pack()

e_passwd = ttk.Entry(root, show='*', textvariable=password)
e_passwd.pack()

l_host = ttk.Label(root, text='Введите ip базы данных:')
l_host.pack()

check_host_ip = (root.register(check_host_ip_addr), '%P')

e_host = ttk.Entry(root, validate='focusout', validatecommand=check_host_ip, textvariable=host)
e_host.pack()

l_host_err = ttk.Label(root, foreground='red', textvariable=err_host_ip, wraplength=200)
l_host_err.pack()

l_port = ttk.Label(root, text='Введите порт подключения:')
l_port.pack()

check_port = (root.register(check_port_bd), '%P')

e_port = ttk.Entry(root, validate='key', validatecommand=check_port, textvariable=port)
e_port.pack()

l_port_err = ttk.Label(root, foreground='red', textvariable=err_port, wraplength=200)
l_port_err.pack()

l_database = ttk.Label(root, text='Введите имя базы данных:')
l_database.pack()

e_database = ttk.Entry(root, textvariable=database)
e_database.pack()

c_save_user = ttk.Checkbutton(root, text='Запомнить меня', state=DISABLED, variable=state_save_user)#, command=(lambda: print('HELLO')))
c_save_user.pack()

b_connect = ttk.Button(root, text='Установить соединение', command=connect_bd)
b_connect.pack()

b_disconnect = ttk.Button(root, text='Разорвать соединение', command=disconnect_bd)
b_disconnect.pack()

b_request = ttk.Button(root, text='Выполнить запрос', command=lambda: create_request(), state='disabled')
b_request.pack()

b_light_request = ttk.Button(root, text='Выполнить упрощенный запрос', command=lambda: create_light_request(), state='disabled')
b_light_request.pack()

p_connect = ttk.Progressbar(root, orient='horizontal', maximum=100, variable=value_progress)
p_connect.pack()

l_progress_connect = ttk.Label(root, text='', wraplength=200, justify=CENTER)
l_progress_connect.pack()

l_help = ttk.Label(root, text='', wraplength=200)
l_help.pack(expand=YES)
    
e_user.bind('<FocusOut>', value_connect_progress)
e_user.bind('<KeyRelease>', auto_user)
e_passwd.bind('<FocusOut>', value_connect_progress)
e_host.bind('<FocusOut>', value_connect_progress)
e_port.bind('<FocusOut>', value_connect_progress)
e_database.bind('<FocusOut>', value_connect_progress)

ttk.Style().theme_use('classic')
root.config(menu=root_menu, cursor='heart')
root.mainloop()
