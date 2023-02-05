# -------------------------------------------------------------------------- #
# IMPORTAÇÕES


# tkinter
from tkinter import Tk, Frame, Label, Button, Entry, filedialog
from tkinter.messagebox import showinfo, showwarning, showerror, askyesno
from tkinter.ttk import Style, Treeview, Scrollbar

# pillow
from PIL import Image, ImageTk

# tkcalendar
from tkcalendar import DateEntry

# os
from os import getcwd

# re
from re import fullmatch

# pathlib
from pathlib import Path

# view
from view import insert_data, delete_data, update_data
from view import show_data, show_record, drop_table
from view import export_to_excel, import_from_excel

# db_create
from db_create import create_table


# -------------------------------------------------------------------------- #
# CONSTANTES E GLOBAIS


COLOR1 = '#feffff'  # Branco
COLOR2 = '#2e2d2b'  # Preto
COLOR3 = '#3fbfb9'  # Verde
COLOR4 = '#e9edf5'  # Branco + Acinzentado?


global tree
global image
global string_image
global night_light_button
global day_light_button

string_image = ''

# Regexs
'''
STRING_PATTERN era para validar as entries mas, vou deixar por enquanto.
Por exemplo xbox360, tem alfabeto e número, serial pode ser algo como
384-FF5Ba-859 e por ai vai. Emfim, acho que vai dar um trabalhão kkk.
Mais tarde devo arrumar uma ou umas regexs que validem direitinho tudo.
'''
# STRING_PATTERN = r''
NUMBER_PATTERN = r'^\d+$'

# Para iniciar no Home do usuário
# quando for carregar uma imagem
HOME = Path.home()


# -------------------------------------------------------------------------- #
# FUNÇÕES


def color_changer(button, widgets):
    """Cuida de trocar o fundo do app."""


    # Queria trocar o fundo da imagem, como faço com os widgets
    # restantes, mas, não achei forma de o fazer

    if button == 'day':
        bg = COLOR1
        fg = COLOR2
    else:
        bg = COLOR2
        fg = COLOR1

    window.configure(bg=fg)


    # Do inicio até antes dos botões
    for widget in widgets[:19]:
        widget['bg'] = bg

    # Menos os frames que não tem fg
    for widget in widgets[3:19]:
        widget['fg'] = fg

    # Botões que tem active foreground e background
    for widget in widgets[19:]:
        widget['bg'] = bg
        widget['fg'] = fg
        widget['activebackground'] = bg
        widget['activeforeground'] = fg

    for widget in (night_light_button, day_light_button):
        widget['bg'] = bg
        widget['fg'] = fg
        widget['activebackground'] = bg
        widget['activeforeground'] = fg

     # Treeview e Cabeçalho
    style.configure(
        'Treeview', background=bg,
        fieldbackground=bg, foreground=fg,
        bordercolor=fg
    )

    style.configure(
        'Treeview.Heading', background=bg,
        fieldbackground=bg, foreground=fg,
        bordercolor=fg
    )

    style.map(
        'Treeview.Heading',
        background=[('selected', bg)]
    )

    # Barra de Rolagem Vertical
    style.configure(
        'Vertical.TScrollbar', troughcolor=bg,
        background=bg, bordercolor=fg,
        arrowcolor=fg
    )
    tree = Treeview(output_frame)

    style.map(
        'Vertical.TScrollbar', background=[
            ('pressed', '!disabled', bg),
            ('active', bg)
        ]
    )

    # Barra de Rolagem Horizontal
    style.configure(
        'Horizontal.TScrollbar', troughcolor=bg,
        background=bg, bordercolor=fg,
        arrowcolor=fg
    )

    style.map(
        'Horizontal.TScrollbar', background=[
            ('pressed', '!disabled', bg),
            ('active', bg)
        ]
    )


def get_record():
    """
    Cuida de pegar o registro, para as funções
    show_image(), delete_record() e update_record().
    Ou retorna com erro se não selecionou
    nenhum registro.
    """
    global tree
    try:
        tree_data = tree.focus()
        tree_dict = tree.item(tree_data)
        tree_list = tree_dict['values']
        valueid = tree_list[0]    # id
    except IndexError:
        showwarning('', 'Tem que selecionar um registro')
        return False
    else:
        return valueid


def insert_record(entries):
    """Cuida da inserção de items na tabela."""
    global image, string_image

    # Nem todos os campos são obrigatórios, "not null"
    # apenas estes que verificamos aqui.
    if entries[0] == '' or entries[1] == '' or \
            entries[2] == '' or entries[3] == '' or entries[5] == '':
        showerror(
            'Erro',
            'Campos: Nome, Descrição, Unidades,'
            ' Marca/Modelo e Valor são OBRIGATÓRIOS'
        )
        return

    # Valida Unidades e Valor (entries[2] e [5])
    if fullmatch(NUMBER_PATTERN, entries[2]) is None or \
            fullmatch(NUMBER_PATTERN, entries[5]) is None:
        showerror(
            'Erro',
            'Apenas digitos em Unidades e Valor.'
        )
        return

    # Pra quê entrar com um item se tem 0 unidades..??
    if int(entries[2]) < 1:
        showerror('Erro', 'Unidades tem que ser 1 ou maior')
        return

    '''
    Aqui, anexa o caminho da imagem,
    string_image, para enviar uma unica lista
    para a função insert_data
    '''
    entries.append(string_image)

    insert_data(entries)
    showinfo('Sucesso', 'Itens inseridos com sucesso')

    reset_widgets(
        [
            name_entry, description_entry,
            unit_number_entry, model_entry,
            aquisition_date_entry, value_entry,
            serial_entry
        ]
    )

    show_table()


def update_record(entries):
    """Cuida de atualizar um registro."""
    global image

    def on_submit():
        """Cuida de submeter as mudanças."""
        updated_entries = list()
        n = 0
        '''
        Não sabemos o que você quer atualizar, se tudo
        ou apenas alguns itens. Então, se um campo estiver
        vazio, nós usamos o valor antigo que está em old_record
        se não usamos o que você digitou..
        '''
        for entry in entries:
            if entry.get() == '':
                updated_entries.append(old_record[n])
            else:
                updated_entries.append(entry.get())
            n += 1

        # Valida unidades e valor (updated_entries[2] e [5])
        # -> str() senão dá erro
        if fullmatch(NUMBER_PATTERN, str(updated_entries[2])) is None or \
                fullmatch(NUMBER_PATTERN, str(updated_entries[5])):
            showerror('Erro', 'Apenas digitos em Unidades e Valor.')
            return

        if int(updated_entries[2]) < 1:
            showerror('Erro', 'Unidades tem que ser 1 ou maior')
            return

        updated_entries.append(image)
        updated_entries.append(updateid)
        update_data(updated_entries)

        showinfo('Sucesso', 'Dados atualizados com sucesso')

        reset_widgets(entries)

        # Agora restaura o botão ao estado original
        load_button['state'] = 'active'
        insert_button['text'] = 'ADICIONAR'
        insert_button['command'] = lambda: insert_record(
            [
                name_entry.get(), description_entry.get(),
                unit_number_entry.get(), model_entry.get(),
                aquisition_date_entry.get(), value_entry.get(),
                serial_entry.get()
            ]
        )

        show_table()

    updateid = get_record()
    if updateid is False:
        return
    else:
        old_record = show_record([updateid])[1:]
        image = old_record[7]
        old_record = old_record[0:7]

        # Aqui, desabilito o botão 'Carregar', porque não sei
        # como carregar uma nova imagem dentro desta função sem dar erro.
        load_button['state'] = 'disabled'

        # Chamo a função reset_widgets, senão as datas
        # ficam coladas: 11/11/202111/11/2020
        reset_widgets(entries)

        # Para não ter que criar um novo botão..
        insert_button['text'] = 'SUBMETER'
        insert_button['command'] = on_submit


def delete_record():
    """Cuida de deletar um registro."""

    deleteid = get_record()
    if deleteid is False:
        return
    else:
        delete_data(str(deleteid))
        showinfo('Sucesso', 'Registro deletado com sucesso')

        show_table()


def get_image(item):
    """Cuida de pegar a imagem."""
    global image, string_image
    filetypes = [
        ('arquivo de imagem', '*.jpeg'),
        ('arquivo de imagem', '*.jpg'),
        ('arquivo de imagem', '*.png')
    ]

    # Função chamada ao pressionar botão 'load_button'
    if item == '':

        '''
         Se for abrir a imagem e fechar a caixa de diálogo
         sem chegar a pegar a imagem dá um monte de mensagem
         feia demais..
        '''
        try:
            image = filedialog.askopenfilename(
                title='Imagem',
                filetypes=filetypes,
                initialdir=HOME
            )
            string_image = image
            image = Image.open(image)
        except Exception as err:
            pass
            return

    # Função chamada a partir de função show_image()
    else:
        image = Image.open(item)


    image = image.resize((200, 200))
    image = ImageTk.PhotoImage(image)

    image_label = Label(
        input_frame, image=image,
        bg=COLOR1
    )
    image_label.place(x=850, y=10)


def show_image():
    """Cuida de mostrar a imagem do item selecionado."""
    global image, string_image

    imageid = get_record()
    if imageid is False:
        return
    else:
        record = show_record([imageid])
        image = record[8]

        # Lembre-se que não obrigo
        # a escolher uma imagem.
        if image == '':
            showinfo(
                '',
                'Item selecionado nao tem imagem registrada'
            )
        else:
            get_image(image)


def show_table():
    """Cuida de mostrar a tabela."""
    global tree

    # Cabeçalho
    table_header = [
        '#Item', 'Nome', 'Descrição',
        'Unidades', 'Marca/Modelo',
        'Data de Aquisição', 'Valor',
        'Serial'
    ]

    tree = Treeview(
        output_frame,
        selectmode='extended',
        columns=table_header,
        show='headings'
    )

    datalist = show_data()

    # Barra de rolagem vertical
    vsb = Scrollbar(
        output_frame,
        orient='vertical',
        command=tree.yview
    )

    # Barra de rolagem horizontal
    hsb = Scrollbar(
        output_frame,
        orient='horizontal',
        command=tree.xview
    )

    # Configura posicionamento no frame
    tree.configure(
        yscrollcommand=vsb.set,
        xscrollcommand=hsb.set
    )
    tree.grid(row=0, column=0, sticky='nsew')
    vsb.grid(row=0, column=1, sticky='ns')
    hsb.grid(row=1, column=0, sticky='ew')
    output_frame.grid_rowconfigure(0, weight=12)

    # Posicionamento do cabelhalho
    h = [75, 150, 210, 100, 150, 160, 150, 150]
    n = 0

    for item in table_header:
        tree.heading(item, text=item, anchor='center')
        # ajusta a largura da coluna as strings
        tree.column(item, width=h[n], anchor='center')
        n += 1

    # Coloca os itens na tabela
    for item in datalist:
        tree.insert('', 'end', values=item)

    # Aqui, podemos ter 100 unidades de um item
    # então somamos tudo.
    values = 0
    quantity = 0

    for item in datalist:
        # item[6] -> valor, item[3] -> unidades
        values += item[6] * item[3]
        quantity += item[3]

    total_label['text'] = f'R${values:,.2f}'
    quantity_label['text'] = f'{quantity}'


def export_excel():
    """Cuida de exportar a tabela para arquivo excel."""
    global tree

    if not tree.get_children():
        showinfo('', 'Tabela não tem dados para serem importados')
        return
    else:
        export_to_excel()


def import_excel():
    """Cuida de pegar o arquivo Excel para inserir na tabela."""
    global tree

    # Se a tabela já tem dados. Apagar ou não?
    if tree.get_children():
        if askyesno(
            'Subescrever',
            'Tabela já contem dados. Deseja deletar tabela atual?'
        ):
            drop_table()
            show_table()
        else:
            return

    # Esta pegando apenas do diretorio atual
    # O diretorio do script
    cwd = getcwd()
    filetypes = [('excel files', '*.xlsx')]
    excel_file = filedialog.askopenfilename(
        title='Arquivo Excel',
        initialdir=cwd,
        filetypes=filetypes
    )

    # Se abrir a caixa de seleção e fechar sem selecionar
    # dá erro muito feio!
    try:
        import_from_excel(excel_file)
    except Exception as err:
        pass
        return
    else:
        show_table()


def reset_widgets(widgets):
    """
    Cuida de resetar os entries
    depois de inserções/atualizações.
    """
    for widget in widgets:
        widget.delete(0, 'end')


# -------------------------------------------------------------------------- #
# JANELA


# Cria tabela se não existe, não faz nada
# se já existe ok?.
create_table()

window = Tk()
window.title('')
window.geometry('1162x600')
window.configure(bg=COLOR2)
window.resizable(0, 0)

style = Style(window)
style.theme_use('clam')


# -------------------------------------------------------------------------- #
# FRAMES


title_frame = Frame(
    window, width=1162,
    height=50, bg=COLOR1,
    relief='raised'
)
title_frame.grid(
    row=0, column=0,
    sticky='nsew', pady=1
)

input_frame = Frame(
    window, width=1162,
    height=300, bg=COLOR1,
    relief='flat'
)
input_frame.grid(
    row=1, column=0,
    sticky='nsew', pady=0
)

output_frame = Frame(
    window, width=1015,
    height=250, bg=COLOR1,
    relief='flat'
)
output_frame.grid(
    row=2, column=0,
    sticky='nsew', pady=0
)


# -------------------------------------------------------------------------- #
# CONFIGURANDO APARÊNCIA DA TREEVIEW


# Treeview e Cabeçalho
style.configure(
    'Treeview', background=COLOR1,
    fieldbackground=COLOR1, foreground=COLOR2,
    bordercolor=COLOR2
)

style.configure(
    'Treeview.Heading', background=COLOR1,
    fieldbackground=COLOR1, foreground=COLOR2,
    bordercolor=COLOR2
)

style.map(
    'Treeview.Heading',
    background=[('selected', COLOR1)]
)


# Barra de Rolagem Vertical
style.configure(
    'Vertical.TScrollbar', troughcolor=COLOR1,
    background=COLOR1, bordercolor=COLOR2,
    arrowcolor=COLOR2
)

style.map(
    'Vertical.TScrollbar', background=[
        ('pressed', '!disabled', COLOR1),
        ('active', COLOR1)
    ]
)


# Barra de Rolagem Horizontal
style.configure(
    'Horizontal.TScrollbar', troughcolor=COLOR1,
    background=COLOR1, bordercolor=COLOR2,
    arrowcolor=COLOR2
)

style.map(
    'Horizontal.TScrollbar', background=[
        ('pressed', '!disabled', COLOR1),
        ('active', COLOR1)
    ]
)


# -------------------------------------------------------------------------- #
# CONFIGURANDO TITLE_FRAME


# Logo
logo = Image.open('Icones/clipboard.png')
logo = logo.resize((45, 45))
logo = ImageTk.PhotoImage(logo)

logo_label = Label(
    title_frame, image=logo,
    compound='left', bg=COLOR1
)
logo_label.place(x=10, y=0)

# Título
title = Label(
    title_frame, text='Inventário',
    font=('Roboto 25 bold'), justify='left',
    anchor='nw', bg=COLOR1, fg=COLOR2
)
title.place(x=70, y=5)


# -------------------------------------------------------------------------- #
# CONFIGURANDO INPUT_FRAME


# --- Inputs --- #


# Nome
name_label = Label(
    input_frame, text='Nome:',
    height=1, anchor='nw',
    font=('Roboto 10 bold'),
    bg=COLOR1, fg=COLOR2
)
name_label.place(x=10, y=20)

name_entry = Entry(
    input_frame,
    font=('Roboto 10'),
    justify='center',
    relief='flat',
    bd=0, borderwidth=0
)
name_entry.place(x=130, y=20)

# Descrição
description_label = Label(
    input_frame, text='Descrição:',
    height=1, anchor='nw',
    font=('Roboto 10 bold'),
    bg=COLOR1, fg=COLOR2
)
description_label.place(x=10, y=50)

description_entry = Entry(
    input_frame,
    font=('Roboto 10'),
    justify='center',
    relief='flat',
    bd=0, borderwidth=0
)
description_entry.place(x=130, y=50)

# Número de Unidades
unit_number_label = Label(
    input_frame, text='Nº Unidades:',
    height=1, anchor='nw',
    font=('Roboto 10 bold'),
    bg=COLOR1, fg=COLOR2
)
unit_number_label.place(x=10, y=80)

unit_number_entry = Entry(
    input_frame,
    font=('Roboto 10'),
    justify='center',
    relief='flat',
    bd=0, borderwidth=0
)
unit_number_entry.place(x=130, y=80)

# Modelo
model_label = Label(
    input_frame, text='Marca/Modelo:',
    height=1, anchor='nw',
    font=('Roboto 10 bold'),
    bg=COLOR1, fg=COLOR2
)
model_label.place(x=10, y=110)

model_entry = Entry(
    input_frame,
    font=('Roboto 10'),
    justify='center',
    relief='flat',
    bd=0, borderwidth=0,
)
model_entry.place(x=130, y=110)

# Data
aquisition_date_label = Label(
    input_frame, text='Data de Aquisição:',
    height=1, anchor='nw',
    font=('Roboto 10 bold'),
    bg=COLOR1, fg=COLOR2
)
aquisition_date_label.place(x=10, y=140)

aquisition_date_entry = DateEntry(
    input_frame, width=18, font=('Roboto 10'),
    justify='center', relief='flat', bd=0,
    borderwidth=0, year=2023, background='darkgray',
    foreground='black', selectbackground='darkgray'
)
aquisition_date_entry.place(x=130, y=140)

# Valor da compra
value_label = Label(
    input_frame, text='Valor da compra:',
    height=1, anchor='nw',
    font=('Roboto 10 bold'),
    bg=COLOR1, fg=COLOR2
)
value_label.place(x=10, y=170)

value_entry = Entry(
    input_frame,
    font=('Roboto 10'),
    justify='center',
    relief='flat',
    bd=0, borderwidth=0
)
value_entry.place(x=130, y=170)

# Número de série
serial_label = Label(
    input_frame, text='Serial do Produto:',
    height=1, anchor='nw',
    font=('Roboto 10 bold'),
    bg=COLOR1, fg=COLOR2
)
serial_label.place(x=10, y=200)

serial_entry = Entry(
    input_frame,
    font=('Roboto 10'),
    justify='center',
    relief='flat',
    bd=0, borderwidth=0
)
serial_entry.place(x=130, y=200)


# --- Botões --- #


# Carregar Item
load_label = Label(
    input_frame, text='Imagem do Item:',
    height=1, anchor='nw',
    font=('Roboto 10 bold'),
    bg=COLOR1, fg=COLOR2
)
load_label.place(x=10, y=235)


'''
Aqui, a função é get_image(''), porque vai ser chamada em duas instâncias.
Aqui no botão onde ainda não escolhemos a imagem e a função abre o diálogo
para escolhermos, e em outra função onde já escolhemos a imagem e então
passamos para a função get_image() e a função simplesmente pega a imagem
Então, dentro da função, verifico se o parâmetro passado é '', vazio, ou
o caminho da imagem.
'''
load_button = Button(
    input_frame, text='CARREGAR',
    anchor='center', compound='center',
    font=('Roboto 8 bold'), width=23,
    bg=COLOR1, fg=COLOR2, overrelief='ridge',
    activebackground=COLOR1, activeforeground=COLOR2,
    command=lambda: get_image('')
)
load_button.place(x=130, y=230)

# Adicionar
add_img = Image.open('Icones/add.png')
add_img = add_img.resize((15, 15))
add_img = ImageTk.PhotoImage(add_img)

insert_button = Button(
    input_frame, text='ADICIONAR', image=add_img,
    anchor='nw', compound='left',
    font=('Roboto 8 bold'),
    bg=COLOR1, fg=COLOR2, overrelief='ridge',
    activebackground=COLOR1, activeforeground=COLOR2,
    command=lambda: insert_record(
        [
            name_entry.get(), description_entry.get(),
            unit_number_entry.get(), model_entry.get(),
            aquisition_date_entry.get(), value_entry.get(),
            serial_entry.get()
        ]
    )
)
insert_button.place(x=345, y=20)

# Atualizar
update_img = Image.open('Icones/update.png')
update_img = update_img.resize((15, 15))
update_img = ImageTk.PhotoImage(update_img)

update_button = Button(
    input_frame, text='ATUALIZAR', image=update_img,
    anchor='nw', compound='left',
    font=('Roboto 8 bold'),
    bg=COLOR1, fg=COLOR2, overrelief='ridge',
    activebackground=COLOR1, activeforeground=COLOR2,
    command=lambda: update_record(
        [
            name_entry, description_entry,
            unit_number_entry, model_entry,
            aquisition_date_entry, value_entry,
            serial_number_entry
        ]
    )
)
update_button.place(x=345, y=60)

# Deletar
delete_img = Image.open('Icones/delete.png')
delete_img = delete_img.resize((15, 15))
delete_img = ImageTk.PhotoImage(delete_img)

delete_button = Button(
    input_frame, text='DELETAR    ',
    image=delete_img, anchor='nw',
    compound='left', font=('Roboto 8 bold'),
    bg=COLOR1, fg=COLOR2, overrelief='ridge',
    activebackground=COLOR1, activeforeground=COLOR2,
    command=delete_record
)
delete_button.place(x=345, y=100)


# Exportar para Planilha
export_excel_img = Image.open('Icones/excel.png')
export_excel_img = export_excel_img.resize((15, 15))
export_excel_img = ImageTk.PhotoImage(export_excel_img)

to_excel_button = Button(
    input_frame, text='EXPORTAR ',
    image=export_excel_img, anchor='nw',
    compound='left', font=('Roboto 8 bold'),
    bg=COLOR1, fg=COLOR2, overrelief='ridge',
    activebackground=COLOR1, activeforeground=COLOR2,
    command=export_excel
)
to_excel_button.place(x=345, y=140)


# Importar de Planilha
import_excel_img = Image.open('Icones/excel.png')
import_excel_img = import_excel_img.resize((15, 15))
import_excel_img = ImageTk.PhotoImage(import_excel_img)

from_excel_button = Button(
    input_frame, text='IMPORTAR ',
    image=import_excel_img, anchor='nw',
    compound='left', font=('Roboto 8 bold'),
    bg=COLOR1, fg=COLOR2, overrelief='ridge',
    activebackground=COLOR1, activeforeground=COLOR2,
    command=import_excel
)
from_excel_button.place(x=345, y=180)

# Vêr Imagem
visualize_img = Image.open('Icones/eye.png')
visualize_img = visualize_img.resize((15, 15))
visualize_img = ImageTk.PhotoImage(visualize_img)

visualize_button = Button(
    input_frame, text='VÊR ITEM   ',
    image=visualize_img, anchor='nw',
    compound='left', font=('Roboto 8 bold'),
    bg=COLOR1, fg=COLOR2, overrelief='ridge',
    activebackground=COLOR1, activeforeground=COLOR2,
    command=show_image
)
visualize_button.place(x=345, y=228)


# --- Labels quantitade e valor total --- #

# Valor total
total_label = Label(
    input_frame, text='', width=16,
    height=2, anchor='center',
    font=('Roboto 17 bold'),
    bg=COLOR3, fg=COLOR1
)
total_label.place(x=500, y=30)

total_item_label = Label(
    input_frame, font=('Roboto 10 bold'),
    text='Valor Total de Todos os Itens',
    height=1, anchor='center', width=26,
    bg=COLOR3, fg=COLOR1
)
total_item_label.place(x=500, y=20)

# Quantidade
quantity_label = Label(
    input_frame, text='',
    height=2, anchor='center', width=16,
    font=('Roboto 17 bold'),
    bg=COLOR3, fg=COLOR1
)
quantity_label.place(x=500, y=130)

quantity_item_label = Label(
    input_frame, font=('Roboto 10 bold'),
    text='Quantidade Total de Itens',
    height=1, anchor='center', width=26,
    bg=COLOR3, fg=COLOR1
)
quantity_item_label.place(x=500, y=120)


# -------------------------------------------------------------------------- #
# TROCA FUNDO DO APP


# Esta lista gigante é para enviar ás funções
# que vão trocar as cores dos widgets.
widgets = [
    title_frame, output_frame, input_frame,
    logo_label, title, name_label, name_entry,
    unit_number_label, unit_number_entry, description_label,
    description_entry, model_label, model_entry,
    aquisition_date_label, value_label, value_entry, serial_label,
    serial_entry, load_label, load_button, insert_button,
    update_button, delete_button, to_excel_button,
    from_excel_button, visualize_button
]

'''
Aqui, queria fazer como se vê nas páginas dos sites, Um botão
apenas, e quando clicar nele trocava a imagem e os fundos
mas não consegui descobrir como se faz kk, então, temos dois
botões e duas funções kk.
'''
# Cor escura
night_img = Image.open('Icones/night-mode.png')
night_img = night_img.resize((35, 35))
night_img = ImageTk.PhotoImage(night_img)

night_light_button = Button(
    title_frame, image=night_img,
    relief='raised', overrelief='ridge',
    bg=COLOR1, activebackground=COLOR1,
    bd=0, borderwidth=0, command=lambda: color_changer('night', widgets)
)
night_light_button.place(x=1060, y=5)


# Cor clara
day_img = Image.open('Icones/day-mode.png')
day_img = day_img.resize((35, 35))
day_img = ImageTk.PhotoImage(day_img)

day_light_button = Button(
    title_frame, image=day_img,
    relief='raised', overrelief='ridge',
    bg=COLOR1, activebackground=COLOR1,
    bd=0, borderwidth=0, command=lambda: color_changer('day', widgets)
)
day_light_button.place(x=1105, y=5)


# -------------------------------------------------------------------------- #
# LOOP


show_table()
window.mainloop()
