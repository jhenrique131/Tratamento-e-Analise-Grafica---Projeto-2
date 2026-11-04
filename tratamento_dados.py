import numpy as np
import pandas as pd
srag_sp = pd.read_csv('E:/0 - Portifolio/python/Tratamento_AnaliseGrafica_Projeto2/python_para_dados/SRAG_2020.csv',
                      sep=';', encoding='utf-8')
# print(srag_sp.head(5))
# print(f"\nsrag_sp.info(): {srag_sp.info()}")
# print(f"\nsrag_sp.describe(): {srag_sp.describe()}")
# print(f"\nsrag_sp.isnull().sum(): {srag_sp.isnull().sum()}")
# print(f"\nsrag_sp.shape: {srag_sp.shape}")

# 1 - Excluindo colunas que não serão utilizadas na análise
# Criaando lista com as colunas que serão excluídas, a partir da coluna 50 até a 132

# lista = list(srag_sp.columns[50:132])
# print(f"\nLista de colunas a serem excluídas: {lista}")

lista = list(range(50, 133))
# print(f"\nLista de colunas a serem excluídas: {lista}")

# Excluindo as colunas da lista
srag_mod = srag_sp.drop(srag_sp.columns[lista], axis=1)
# print(f"\nsrag_mod.head(): {srag_mod.head(5)}")

# print(f"\nsrag_mod.shape: {srag_mod.shape}")

# Excluindo colunas que não servem para a análise.
srag_mod.drop(columns=['COD_IDADE',
                       'ID_PAIS',
                       'CO_PAIS',
                       'SG_UF',
                       'ID_RG_RESI',
                       'CO_RG_RESI',
                       'CO_MUN_RES'], inplace=True)
# print(f"\nsrag_mod.shape: {srag_mod}")
# print(f"\nsrag_mod.shape: {srag_mod.shape}")

# 2 - Renomeando colunas para facilitar a análise
srag_mod = srag_mod.rename(columns={'DT_NOTIFIC': 'data',
                                    'CS_SEXO': 'sexo',
                                    'NU_IDADE_N': 'idade',
                                    'CS_RACA': 'raca'})
# print(f"\nsrag_mod.head(): {srag_mod.head(5)}")

# 3 - Analisando os tipos de variáveis do DataFrame
# print(f"\nsrag_mod.dtypes: {srag_mod.dtypes}")

# 4 - Convertendo o tipo, de object para data - cast
srag_mod['data'] = srag_mod['data'].astype('datetime64[ns]')
# print(f"\nsrag_mod.dtypes: {srag_mod.dtypes}")

# Analisando valores nulos
#print(f"\nsrag_mod.isnull().sum(): {srag_mod.isnull().sum()}")

#Contagem das classificações de raça
#Quantidade de registros por raça, ordenados pelo índice (código da raça)
#print(f"\nsrag_mod['raca'].value_counts().sort_index(): {srag_mod['raca'].value_counts().sort_index()}")

#Preenchendo valores nulos da coluna 'raca' com o valor 9 (Ignorado)
srag_mod['raca'].fillna(9, inplace=True)
#print(f"\nsrag_mod['raca'].value_counts().sort_index(): {srag_mod['raca'].value_counts().sort_index()}")

#Contagem das classificações de CS_ZONA
#Quantidade de registros por zona, ordenados pelo índice (código da zona)
#print(f"\nsrag_mod['CS_ZONA'].value_counts().sort_index():{srag_mod['CS_ZONA'].
    #  value_counts().sort_index()}")

#Preenchendo valores nulos da coluna 'CS_ZONA' com o valor 9 (Ignorado)
srag_mod['CS_ZONA'].fillna(9, inplace=True)
#print(f"\nsrag_mod['CS_ZONA'].value_counts().sort_index(): {srag_mod['CS_ZONA'].
 #     value_counts().sort_index()}")


#Substituindo as classificações numéricas por palavras, para facilitar a análise
srag_mod['raca'] = srag_mod['raca'].replace({1: 'Branca', 
                                             2: 'Preta', 
                                             3: 'Amarela', 
                                             4: 'Parda', 
                                             5: 'Indígena', 
                                             9: 'Ignorado'})
#print(f"\nsrag_mod['raca'].value_counts(): {srag_mod['raca'].
     # value_counts().sort_index()}")

#A mesma substituição será feita para a coluna 'CS_ZONA'
srag_mod['CS_ZONA'] = srag_mod['CS_ZONA'].replace({1: 'Urbana',
                                                2: 'Rural', 
                                                3: 'Periurbana', 
                                                9: 'Ignorado'})
#print(f"\nsrag_mod['CS_ZONA'].value_counts(): {srag_mod['CS_ZONA'].
      value_counts().sort_index()}")














