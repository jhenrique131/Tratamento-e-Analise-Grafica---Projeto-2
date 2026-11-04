import matplotlib.pyplot as plt
import tratamento_dados as td

graf_barras = td.srag_mod['sexo'].value_counts()
# print(f"\ngrafico_barras: {graf_barras}")

# print(f"\ngrafico_barras.index: {graf_barras.index}")

# O gráfico de barras é uma representação visual de dados categóricos,
# onde cada categoria é representada por uma barra, e o
# comprimento da barra indica a quantidade ou frequência da categoria.
# No caso do código fornecido, o gráfico de barras está sendo criado para
# mostrar a distribuição dos casos de SRAG (Síndrome Respiratória Aguda Grave) por sexo.

""" plt.bar(graf_barras.index, graf_barras, color=['red'])
plt.title('Distribuição de Casos de SRAG por Sexo')
plt.xlabel('Sexo')
plt.ylabel('Quantidade de Casos')
plt.show() """

#Grafico de barras horizontal
plt.barh(graf_barras.index, graf_barras, color=['red'])
plt.title('Distribuição de Casos de SRAG por Sexo')
plt.xlabel('Quantidade de Casos')
plt.ylabel('Sexo')
plt.show()