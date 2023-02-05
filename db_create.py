# -------------------------------------------------------------------------- #
# IMPORTAÇÕES


# sqlite3
import sqlite3


# -------------------------------------------------------------------------- #
# CONEXÃO

connection = sqlite3.connect('data.db')


# -------------------------------------------------------------------------- #
# TABELA


def create_table():
    """Cuida de criar a tabela."""
    with connection:
        cursor = connection.cursor()
        cursor.execute(
            '''
                create table if not exists inventario(
                    id integer primary key,
                    nome text not null,
                    descricao text not null,
                    unidades decimal not null,
                    marca text not null,
                    data date,
                    valor decimal not null,
                    serie text,
                    local_da_imagem text
                )
            '''
        )
