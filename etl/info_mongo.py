

def saveToMongo(df, col, workload, interface=None):
    df2 = df[["ts", "exp", "cicle", workload]].rename(columns={workload: 'value'})
    df2["workload"] = workload
    if interface is not None:
        df2["interface"] = interface
    getDatabase("metrics")[col].insert_many(df2.to_dict("records"))
    
    
# def plotBoxPlot(df, title, output, hue="priority", ylabel="Consumo (Mbps)", ylimit=200):
#     print(f"Plotando gráfico BoxPlot de {title}")
#     plt.figure(figsize=(10, 5))
#     sns.set_style("whitegrid")
#     ax = sns.boxplot(data=df, x="exp", y="value", hue=hue, palette="Set3", linewidth=1)
#     #ax.tick_params(axis='y', direction="inout", length=25)
#     if ylimit > 200:
#         ax.yaxis.set_major_locator(MultipleLocator(ylimit / 10))
#         ax.yaxis.set_minor_locator(MultipleLocator(ylimit / 50))
#     else:
#         ax.yaxis.set_major_locator(MultipleLocator(20))
#         ax.yaxis.set_minor_locator(MultipleLocator(4))
        
#     ax.grid(which='major', color='#CCCCCC', linestyle='--')
#     ax.grid(which='minor', color='#CCCCCC', linestyle=':')
#     ax.set_ylim([0, ylimit])
#     legend = plt.legend(title="Slice", loc="best", fontsize=11, framealpha=0.7, edgecolor="black", frameon=True)
    
#     percentiles = df.groupby(['exp', 'priority'])['value'].quantile([0.25, 0.5, 0.75]).unstack(level=1)
#     #print(value_q1_exp1 = percentiles.loc['1 0.25', ('open5gs-upf-1')])
#     #percentiles.columns = ["Q1", "Median", "Q3"]
    
#     #for i in percentiles.index:
#     for (exp, percentil), value in percentiles['open5gs-upf-1'].items():
#         if percentil == 0.25:
#             quartil_1 = value
#         elif percentil == 0.5:
#             mediana = value
#         elif percentil == 0.75:
#             quartil_3 = value
            
            
#         # print(quartil_1)
#         # mediana   = percentiles.loc[i, "Median"]
#         # quartil_3 = percentiles.loc[i, "Q3"]
#         # #print(percentiles.loc[i, "Q1"])
#         # # Posição x para o boxplot atual (i+1, já que os boxplots começam em x=1, 2, 3,...)
#             x_position = exp - 1.35
#             y_m_offset = (quartil_3 + quartil_1) / 2
#             # # Anotações para Q1, Mediana e Q3
#             ax.text(x_position, quartil_1 - 3, f'q1: {quartil_1:.1f}', verticalalignment='center', color='#111111', fontsize=8)
#             ax.text(x_position, y_m_offset, f'{mediana:.1f}', verticalalignment='center', color='#222222', fontsize=8)
#             ax.text(x_position, quartil_3 + 3, f'q3: {quartil_3:.1f}', verticalalignment='center', color='#333333', fontsize=8)
            
#     # for (exp, percentil), value in percentiles['others'].items():
#     #     if percentil == 0.25:
#     #         quartil_1 = value
#     #     elif percentil == 0.5:
#     #         mediana = value
#     #     elif percentil == 0.75:
#     #         quartil_3 = value
#     #         x_position = exp - 0.90
#     #         y_m_offset = (quartil_3 + quartil_1) / 2
#     #         # # Anotações para Q1, Mediana e Q3
#     #         ax.text(x_position, quartil_1 - 3, f'q1: {quartil_1:.1f}', verticalalignment='center', color='#111111', fontsize=8)
#     #         ax.text(x_position, y_m_offset, f'{mediana:.1f}', verticalalignment='center', color='#222222', fontsize=8)
#     #         ax.text(x_position, quartil_3 + 3, f'q3: {quartil_3:.1f}', verticalalignment='center', color='#333333', fontsize=8)

#     # Gráfico de disperção
#     #ax = sns.stripplot(x = "exp", y ="value", hue="priority" ,data = df)  
    
#     plt.title(title, loc="center", fontsize=20)
#     plt.xlabel("Experimentos", fontsize=14)
#     plt.ylabel(ylabel, fontsize=14)


#     # Salvando o gráfico em um arquivo pdf
#     plt.savefig(f"boxplot\\{output}.pdf".replace(" ", "_").lower(), bbox_inches='tight')
#     plt.savefig(f"boxplot\\{output}.png".replace(" ", "_").lower(), bbox_inches='tight')
#     #plt.add_Trace(go.Bar(x=df['workload'], y=df['avg'], name='avg'))

#     plt.close()