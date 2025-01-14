import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Alignment
import datetime

def scrape_mercadolivre(url):
    # Função para fazer scraping da página do Mercado Livre e extrair dados dos produtos em promoção
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    products = soup.find_all('li', {'class': 'promotion-item'})  # Encontrar todos os produtos em promoção

    data = []
    for product in products:
        discount_elements = product.find_all('span', {'class': 'promotion-item__discount-text'})
        for discount_element in discount_elements:
            discount_text = discount_element.text.strip()
            discount_match = re.search(r'(\d+)', discount_text)
            if discount_match:
                discount_percentage = int(discount_match.group(1))
                if discount_percentage >= 15:
                    # Extrair nome e preço do produto
                    name = product.find('p', {'class': 'promotion-item__title'}).text.strip()
                    price = product.find('span', {'class': 'andes-money-amount__fraction'}).text.strip()
                    # Limpar e formatar os dados antes de adicionar à lista
                    name = re.sub(r'\s+', ' ', name)  # Remover espaços excessivos
                    price = re.sub(r'[^\d,]', '', price)  # Manter apenas dígitos e vírgulas
                    data.append([name, price, discount_percentage])
                    break
    return data

all_data = []

# Coletar dados de várias páginas do Mercado Livre
for i in range(1, 20):
    url = f'https://www.mercadolivre.com.br/ofertas?container_id=MLB779362-1&page={i}'
    data = scrape_mercadolivre(url)
    all_data.extend(data)  # Adicionar dados de cada página à lista principal

# Ordenar a lista de dados em ordem alfabética pelo nome do produto
sorted_data = sorted(all_data, key=lambda x: x[0])

# Criar DataFrame com os dados coletados
df = pd.DataFrame(sorted_data, columns=['Nome do Produto', 'Preço', 'Desconto'])

# Exibir número total de registros e mostrar as primeiras amostras do dataset
num_registros = len(df)
print(f'Número de registros: {num_registros}')
print('Amostras do dataset:')
print(df.head())

# Escrever dados no arquivo CSV com um delimitador melhor
date_today = datetime.date.today().strftime("%d_%m_%Y")
file_name_csv = f"ISMAEL_DIEGO_FELIPE_UERBERT_{date_today}.csv"
df.to_csv(file_name_csv, index=False)

# Criar e formatar o arquivo Excel
wb = Workbook()
ws = wb.active
ws.title = "ISMAEL_DIEGO_FELIPE_UERBERT"

# Adicionar os dados ao arquivo Excel
for r in dataframe_to_rows(df, index=False, header=True):
    ws.append(r)

# Ajustar o espaçamento das colunas e a formatação das células no arquivo Excel
for col in ws.columns:
    max_length = 0
    column = col[0].column_letter  # Obter a letra da coluna
    for cell in col:
        try:
            if len(str(cell.value)) > max_length:
                max_length = len(cell.value)
        except:
            pass
    adjusted_width = (max_length + 2)  # Ajustar largura da coluna
    ws.column_dimensions[column].width = adjusted_width  # Definir largura da coluna no Excel

# Alinhar o texto das células ao centro no arquivo Excel
for row in ws.iter_rows():
    for cell in row:
        cell.alignment = Alignment(horizontal='center', vertical='center')

# Salvar o arquivo Excel
wb.save("ISMAEL_DIEGO_FELIPE_UERBERT.xlsx")

# Calcular estatísticas descritivas dos descontos dos produtos
mean_discount = df['Desconto'].mean()
median_discount = df['Desconto'].median()
std_dev_discount = df['Desconto'].std()
min_discount = df['Desconto'].min()
max_discount = df['Desconto'].max()
variance_discount = df['Desconto'].var()
cv_discount = std_dev_discount / mean_discount  # Coeficiente de variação
quantiles = df['Desconto'].quantile([0.25, 0.5, 0.75])  # Quartis
iqr_discount = quantiles[0.75] - quantiles[0.25]  # Intervalo interquartil

# Imprimir estatísticas calculadas
print(f'Média do desconto: {mean_discount}')
print(f'Mediana do desconto: {median_discount}')
print(f'Desvio padrão do desconto: {std_dev_discount}')
print(f'Desconto mínimo: {min_discount}')
print(f'Desconto máximo: {max_discount}')
print(f'Variância do desconto: {variance_discount}')
print(f'Coeficiente de variação do desconto: {cv_discount}')
print(f'Intervalo interquartil (IQR) do desconto: {iqr_discount}')
print('Quartis:')
print(quantiles)

# Preparar dados para o boxplot
stats_data = {
    'Média': mean_discount,
    'Mediana': median_discount,
    'Desvio Padrão': std_dev_discount,
    'Variância': variance_discount,
    'Coeficiente de Variação': cv_discount,
    'IQR': iqr_discount,
    'Mínimo': min_discount,
    'Máximo': max_discount
}

stats_df = pd.DataFrame(list(stats_data.items()), columns=['Estatística', 'Valor'])

# Criar o boxplot dos descontos
plt.figure(figsize=(12, 8))
plt.boxplot(df['Desconto'], vert=False, patch_artist=True, boxprops=dict(facecolor='skyblue', color='blue'))
plt.title('Boxplot dos Descontos dos Produtos')
plt.xlabel('Desconto (%)')
plt.grid(True)

# Adicionar os valores no boxplot
for stat in stats_data:
    plt.text(x=stats_data[stat], y=1, s=f"{stats_data[stat]:.2f}", horizontalalignment='center')

plt.show()

# Criar o gráfico de barras para as estatísticas calculadas
plt.figure(figsize=(12, 8))
bars = plt.barh(stats_df['Estatística'], stats_df['Valor'], color='skyblue')
plt.title('Medidas de Dispersão e Distribuição dos Descontos')
plt.xlabel('Valor')
plt.grid(True, axis='x')

# Adicionar os valores no gráfico de barras
for bar in bars:
    plt.text(bar.get_width(), bar.get_y() + bar.get_height()/2, f'{bar.get_width():.2f}', va='center')

plt.show()
