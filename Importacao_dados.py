# Extração dos dados para o banco PostgreSQL

"""Fase 1 - Extracao e carga da camada Raw.

1. Executa o cria_banco.sql (cria o banco e as tabelas raw/silver).
2. Baixa o arquivo do Google Drive (.zip ou .csv).
3. Le o CSV em blocos e carrega na tabela raw_srag_2020.

Uso:
    python extracao_dados.py              # cria o banco/tabelas só se não existirem
    python extracao_dados.py --recriar    # roda o cria_banco.sql de novo (DROP TABLE!)
"""
import logging
import re
import shutil
import sys
import zipfile

import gdown
import pandas as pd
import psycopg2
from psycopg2 import sql

import config
from banco import conectar, executar, inserir_em_lote

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("extracao_dados")

ARQUIVO_SQL = config.BASE_DIR / "cria_banco.sql"
TABELA_RAW = "raw_srag_2020"


# ------------------------------------------------------------ cria_banco ----
def ler_sql():
    """Le o cria_banco.sql e separa o nome do banco do restante do script.

    Os comandos `CREATE DATABASE` e `\\c` do SQL são do psql e não funcionam
    via psycopg2: o CREATE DATABASE é executado à parte e o `\\c` é descartado.
    """
    texto = ARQUIVO_SQL.read_text(encoding="utf-8")
    achou = re.search(r"CREATE\s+DATABASE\s+(\w+)\s*;", texto, re.IGNORECASE)
    if not achou:
        raise ValueError("CREATE DATABASE não encontrado no cria_banco.sql")
    nome_banco = achou.group(1)

    texto = re.sub(r"CREATE\s+DATABASE\s+\w+\s*;", "", texto,
                   flags=re.IGNORECASE)
    linhas = [l for l in texto.splitlines() if not l.strip().startswith("\\")]
    return nome_banco, "\n".join(linhas)


def criar_banco(nome_banco):
    """Cria o banco (se não existir). Retorna True se ele foi criado agora."""
    cfg = dict(config.DB_CONFIG)
    cfg["database"] = "postgres"  # banco de manutenção
    conn = psycopg2.connect(**cfg)
    conn.autocommit = True  # CREATE DATABASE não roda dentro de transação
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s",
                        (nome_banco,))
            if cur.fetchone():
                log.info("Banco '%s' já existe", nome_banco)
                return False
            cur.execute(sql.SQL("CREATE DATABASE {}")
                        .format(sql.Identifier(nome_banco)))
            log.info("Banco '%s' criado", nome_banco)
            return True
    finally:
        conn.close()


def tabela_existe(conn, tabela):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (tabela,))
        return cur.fetchone()[0] is not None


def preparar_banco(recriar=False):
    """Executa o cria_banco.sql (banco + tabelas)."""
    nome_banco, script = ler_sql()
    # O SQL define o banco; garante que conectar() use o mesmo
    config.DB_CONFIG["database"] = nome_banco

    criar_banco(nome_banco)
    conn = conectar()
    try:
        if recriar or not tabela_existe(conn, TABELA_RAW):
            log.info("Executando %s ...", ARQUIVO_SQL.name)
            with conn.cursor() as cur:
                cur.execute(script)
            conn.commit()
            log.info("Tabelas criadas")
        else:
            log.info("Tabela '%s' já existe (use --recriar para refazer)",
                     TABELA_RAW)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# --------------------------------------------------------------- download ----
def baixar_csv():
    """Baixa o arquivo do Drive e devolve o caminho do CSV."""
    destino = config.ARQUIVO_CSV
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    if destino.exists():
        log.info("CSV já existe em %s, pulando download", destino)
        return destino

    baixado = config.DATA_DIR / "download_drive.tmp"
    url = f"https://google.com{config.DRIVER_FILE_ID}"
    log.info("Baixando arquivo do Google Drive...")
    if not gdown.download(url, str(baixado), quiet=False):
        raise RuntimeError("Falha no download (o arquivo precisa estar "
                           "compartilhado como 'Qualquer pessoa com o link')")

    if zipfile.is_zipfile(baixado):
        with zipfile.ZipFile(baixado) as zf:
            por_nome = {n.split("/")[-1].lower(): n for n in zf.namelist()}
            interno = por_nome.get(destino.name.lower())
            if interno is None:
                raise FileNotFoundError(f"{destino.name} não está no .zip")
            destino.write_bytes(zf.read(interno))
        baixado.unlink()
    else:
        shutil.move(str(baixado), str(destino))
    return destino


# ------------------------------------------------------------------ carga ----
def colunas_da_tabela(conn, tabela):
    with conn.cursor() as cur:
        cur.execute("SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = %s ORDER BY ordinal_position",
                    (tabela,))
        return [r[0] for r in cur.fetchall()]


def carregar_raw(conn, csv_path):
    """TRUNCATE + carga em blocos do CSV na tabela raw."""
    colunas = colunas_da_tabela(conn, TABELA_RAW)

    # Casa as colunas do CSV com as da tabela pelo NOME (ignora a ordem)
    cabecalho = pd.read_csv(csv_path, sep=config.CSV_SEP,
                            encoding=config.CSV_ENCODING, nrows=0).columns
    por_nome = {c.strip().lower(): c for c in cabecalho}
    faltando = [c for c in colunas if c not in por_nome]
    if faltando:
        raise ValueError(f"Colunas da tabela ausentes no CSV: {faltando}")

    executar("SET datestyle TO 'ISO, MDY'", conn=conn)
    executar(sql.SQL("TRUNCATE TABLE {}").format(sql.Identifier(TABELA_RAW)),
             conn=conn)

    blocos = pd.read_csv(
        csv_path, sep=config.CSV_SEP, encoding=config.CSV_ENCODING,
        dtype=str, keep_default_na=False,
        usecols=[por_nome[c] for c in colunas], chunksize=config.CHUNK_SIZE,
    )
    total = 0
    for bloco in blocos:
        bloco.columns = [c.strip().lower() for c in bloco.columns]
        bloco = bloco[colunas].apply(lambda s: s.str.strip())
        if "obes_imc" in bloco:  # decimal com vírgula
            bloco["obes_imc"] = bloco["obes_imc"].str.replace(",", ".",
                                                              regex=False)

        # --- ALTERADO AQUI: Limpeza robusta contra strings de texto nulo ---
        bloco = bloco.astype(object)
        bloco = bloco.where((bloco != "") & (
            bloco != "None") & (bloco != "nan"), None)

        linhas = list(bloco.itertuples(index=False, name=None))
        total += inserir_em_lote(conn, TABELA_RAW, colunas, linhas)
        log.info("%s: %d linhas...", TABELA_RAW, total)
    conn.commit()
    log.info("%s: %d linhas carregadas", TABELA_RAW, total)
    return total


def main():
    recriar = "--recriar" in sys.argv
    try:
        preparar_banco(recriar)
        csv_path = baixar_csv()
    except Exception:
        log.exception("Falha ao preparar o banco ou baixar os dados")
        return 1

    conn = conectar()
    try:
        carregar_raw(conn, csv_path)
    except Exception:
        conn.rollback()
        log.exception("Falha ao carregar %s", TABELA_RAW)
        return 1
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
