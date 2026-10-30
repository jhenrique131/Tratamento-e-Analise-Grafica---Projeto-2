# Conexões e função do PostgreSQL
import uuid
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
import config


def conectar():
    # Abre conexão com o PostgreSQL
    return psycopg2.connect(**config.DB_CONFIG)


def get_engine():
    # Mapeia as classes python para tabelas do banco de dados
    # e realiza operações
    from sqlalchemy import create_engine
    from sqlalchemy.engine import URL

    cfg = config.DB_CONFIG
    url = URL.create(
        username=cfg["user"],
        password=cfg["password"],
        host=cfg["host"],
        port=int(cfg["port"]),
        database=cfg["database"]

    )
    return create_engine(url)


def executar(comando, params=None, conn=None):
    # Sem 'conn', abre uma conexão própria e faz commit
    # Com 'conn', apenas executa

    propria = conn is None
    conn = conn or conectar
    try:
        with conn.cursor() as cur:
            cur.execute(comando, params)
            linhas = cur.rowcount
        if propria:
            conn.commit()
        return linhas
    except Exception:
        if propria:
            conn.rollback()
        raise
    finally:
        if propria:
            conn.close()


def inserir_em_lote(conn, tabela, colunas, linhas, on_conflict="", page_size=5000):
    """
   Insere em lote no PostgreSQL.

   `tabela` é o nome da tabela.
   `colunas` é uma lista de nomes de colunas.
   `linhas` é uma lista de tuplas com os valores a serem inseridos.
   """
