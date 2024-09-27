import matplotlib.pyplot as plt
import pandas as pd
import datetime

# Dados de exemplo: lista de tuplas (timestamp, consumo)
dados_consumo = [
    (datetime.datetime(2023, 10, 1, 10, 0), 120),
    (datetime.datetime(2023, 10, 1, 11, 0), 150),
    (datetime.datetime(2023, 10, 1, 12, 0), 100),
    (datetime.datetime(2023, 10, 1, 13, 0), 130),
    (datetime.datetime(2023, 10, 1, 14, 0), 170),
]

# Convertendo os dados para um DataFrame do pandas
df = pd.DataFrame(dados_consumo, columns=['Timestamp', 'Consumo'])

# Configurando o gráfico
plt.figure(figsize=(10, 5))
plt.plot(df['Timestamp'], df['Consumo'], marker='o', linestyle='-')

# Adicionando título e rótulos
plt.title('Consumo de Rede ao Longo do Tempo')
plt.xlabel('Tempo')
plt.ylabel('Consumo (MB)')

# Formatando o eixo x para mostrar datas de forma legível
plt.gcf().autofmt_xdate()

# Salvando o gráfico em um arquivo PNG
plt.savefig('consumo_rede.png')

# Fechando a figura para liberar memória
plt.close()