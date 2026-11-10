import tratamento_dados as td
import plotly.express as px

# Quantidade de registros do  campo TP_IDADE
# print(f"Quantidade de registros do campo TP_IDADE: {td.srag_mod['TP_IDADE'].
# value_counts().sort_index()}")
# print(f"Quantidade de registros do campo idade: {td.srag_mod['idade'].
# value_counts().sort_index()}")

# Tras informações sobre a distribuição do campo idade, como média,
# mediana, desvio padrão, valores mínimo e máximo, entre outros.
# print(f"Descrição do campo idade: {td.srag_mod['idade'].describe()}")

# Registros que mais se repetem no campo idade - Moda
print(f"Moda do campo idade: {td.srag_mod['idade'].mode()}")

# Localizando idade == 1 e atribuindo zero ano a coluna idade
td.srag_mod.loc[td.srag_mod['idade'] == 1, 'idade'] = 0

# Localizando idade == 2 e atribuindo zero ano a coluna idade
td.srag_mod.loc[td.srag_mod['idade'] == 2, 'idade'] = 0

print(f"Descrição do campo idade: {td.srag_mod['idade'].describe()}")
