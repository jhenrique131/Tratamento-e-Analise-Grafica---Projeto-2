import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "python_para_dados"
ARQUIVO_CSV = DATA_DIR / "SRAG_2020.csv"

# CORREÇÃO: Removida a barra '/' do final do ID
DRIVER_FILE_ID = "1OtLeJ3K3RBLZGtH0ULXUxqZnJ0jgm-SK" 

# Garante que a pasta 'data' exista antes de baixar
DATA_DIR.mkdir(parents=True, exist_ok=True)

def baixar_arquivo_drive(file_id, destino):
    print(f"Iniciando o download do arquivo para: {destino}")
    
    # URL de download direto do Google Drive
    url = f"https://google.com{file_id}&confirm=t"
    
    # Faz a requisição em modo stream (ideal para arquivos grandes)
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        
        # Grava o arquivo em blocos na memória
        with open(destino, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filtra keep-alive chunks
                    f.write(chunk)
                    
    print("Download concluído com sucesso!")

# Executa o teste de download
if not ARQUIVO_CSV.exists():
    try:
        baixar_arquivo_drive(DRIVER_FILE_ID, ARQUIVO_CSV)
    except Exception as e:
        print(f"Erro ao baixar o arquivo: {e}")
else:
    print(f"O arquivo já existe em: {ARQUIVO_CSV}")
