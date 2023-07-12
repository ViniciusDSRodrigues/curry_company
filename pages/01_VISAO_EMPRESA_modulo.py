import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import plotly.express as px
import streamlit as st
from datetime import datetime
from PIL import Image

st.set_page_config(page_title='Visão Empresa',page_icon="📊",layout='wide')

#------------- FUNÇÕES ---------------

#- FUNÇÃO DE GRÁFICO DE ENTREGAS POR DIA
def order_metric(df_final):
    # Seleção das linhas
    base_graph_bar = df_final.loc[:, ['ID', 'Order_Date']].groupby(['Order_Date']).count().reset_index()
    # Desenhar o gráfico de Linhas
    fig = px.bar(base_graph_bar, x='Order_Date', y='ID').update_layout(yaxis=dict(title='Quantity_Deliveries'))

    return fig

#- FUNÇÃO DE GRÁFICO DE ENTREGAS POR TIPO DE TRÁFEGO POR DIA
def traffic_order_share(df_final):
    base_graphic_pizza = df_final.loc[:, ['ID', 'Road_traffic_density']].groupby(
        ['Road_traffic_density']).count().reset_index()
    base_graphic_pizza = base_graphic_pizza.loc[base_graphic_pizza['Road_traffic_density'] != 'NaN', :]
    base_graphic_pizza['Percent_Entregas'] = base_graphic_pizza['ID'] / (base_graphic_pizza['ID'].sum())

    fig = px.pie(base_graphic_pizza, values='Percent_Entregas', names='Road_traffic_density',hover_data={'ID': True},
                 labels={'ID': 'Qtde_Entregas'})
    st.dataframe(base_graphic_pizza)

    return fig

#- FUNÇÃO DE GRÁFICO DE ENTREGAS POR TIPO DE TRÁFEGO E TIPO DE CIDADE POR DIA
def traffic_order_city(df_final):
    base_graph_bolha = df_final.loc[:, ['City', 'ID', 'Road_traffic_density']].groupby(
        ['City', 'Road_traffic_density']).count().reset_index()
    fig = px.scatter(base_graph_bolha, x='City', y='Road_traffic_density', size='ID', color='City')
    return fig

#- FUNÇÃO DE GRÁFICO DE QTDE DE ENTREGAS SEMANAL
def order_by_week(df_final):
    df_final['Week_of_Year'] = df_final['Order_Date'].dt.strftime('%U')
    base_graph_line = df_final.loc[:, ['ID', 'Week_of_Year']].groupby(['Week_of_Year']).count().reset_index()
    fig = px.line(base_graph_line, y='ID', x='Week_of_Year').update_layout(yaxis=dict(title='Quantity_Deliveries'))
    return fig

#- FUNÇÃO DE GRÁFICO DA MÉDIA DE ENTREGAS SEMANAIS POR ENTREGADOR
def order_share_by_week(df_final):
    qtde_entregas_week = df_final.loc[:, ['ID', 'Week_of_Year']].groupby(['Week_of_Year']).count().reset_index()
    qtde_entregadores_week = df_final.loc[:, ['Delivery_person_ID', 'Week_of_Year']].groupby(
        ['Week_of_Year']).nunique().reset_index()
    df_aux = pd.merge(qtde_entregas_week, qtde_entregadores_week, how='inner')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    fig = px.line(df_aux, x='Week_of_Year', y='order_by_deliver')
    return fig

#- FUNÇÃO DE GRÁFICO DE MAPAS
def country_maps(df_final):
    base_graph_map = df_final.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude',
                                          'Delivery_location_longitude']].groupby(
        ['City', 'Road_traffic_density']).median().reset_index()
    mapa = folium.Map()
    for index, info in base_graph_map.iterrows():
        if info['Delivery_location_latitude'] > 10.000:
            folium.Marker([info['Delivery_location_latitude'], info['Delivery_location_longitude']],
                         popup=info[['City', 'Road_traffic_density']]).add_to(mapa)
            #pus esse elif p a distancia media existir dentro da india, se não saiíra da india.
        else:
            pass

    #TODO: Essa função traz regiões por médias de latitude x longitude e o pop-up mostra as mesmas
    #TODO: com as infos de cidade, a densidade e a ''posição do DF''
    #TODO: um ''st.dataframe(base_graph_map)'' pode mostrar melhor, cada linha
    #TODO: é uma info do POP_UP c sua densidade, local da cidade (média das latitude x longitude) uma especie de
    #TODO: concentraçaõ de transito do lugar e a cidade propriamente dita.
    #TODO: e sua posição do DF tbm aparece.

    #st.dataframe(base_graph_map)
    folium_static(mapa, width= 1024,height=600)

#FUNÇÃO AUXILIAR QUE LIMPA ESPAÇOS
def clean_space(texto):
    texto_novo = texto.strip()
    return texto_novo

def clean_df(df_final):
    """ESTA FUNÇÃO EXECUTA LIMPEZA NO DF

      TIPOS DE LIMPEZA:
      - REMOÇÃO DOS DADOS NaN
      - MUDANÇA DO TIPO DA COLUNA DE DADOS
      - REMOÇÃO DOS ESPAÇOS DAS VARIÁVEIS DE TEXTO
      - FORMATAÇÃO DA COLUNA DE DATAS
      - LIMPEZA DA COLUNA DE TEMPO (REMOÇÃO DO TEXTO ''MIN()'' DA VARIÁVEL NUMÉRICA)

      INPUT: DF
      OUTPUT: DF LIMPO

    """
    # Excluindo algumas colunas com 'NaN '
    df_final = df_final.loc[df['Road_traffic_density'] != 'NaN ', :]
    df_final = df_final.loc[df['Delivery_person_Age'] != 'NaN ', :]
    df_final = df_final.loc[df['multiple_deliveries'] != 'NaN ', :]
    df_final = df_final.loc[df['City'] != 'NaN ', :]
    df_final = df_final.loc[df['Festival'] != 'NaN ', :]

    # Covertendo a coluna Age para número
    df_final['Delivery_person_Age'] = df_final['Delivery_person_Age'].astype(float)

    # Convertendo a coluna Ratings para número decimal
    df_final['Delivery_person_Ratings'] = df_final['Delivery_person_Ratings'].astype(float)

    # Convertendo a coluna Date para Data
    df_final['Order_Date'] = pd.to_datetime(df_final['Order_Date'], format='%d-%m-%Y')

    # Convertendo a coluna multiple_deliveries para número
    df_final['multiple_deliveries'] = df_final['multiple_deliveries'].astype(int)

    # Excluindo espaço vazios da coluna ID. *FUNÇÃO CRIADA ACIMA PARA FAZER ISSO.
    # df_final['ID'] = df_final['ID'].apply(clean_space)
    # df_final['Delivery_person_ID'] = df_final['Delivery_person_ID'].apply(clean_space)
    # Road_traffic_density
    for i, linha in enumerate(df_final):
        texto = str(df_final.iloc[0, i])
        if texto[-1] == ' ':
            #print('A coluna {} tem espaços. Eles serão removidos.'.format(df_final.columns[i]))
            df_final[df_final.columns[i]] = df_final[df_final.columns[i]].apply(clean_space)

    # Limpando '(min)' da coluna de time taken
    df_final['Time_taken(min)'] = df_final['Time_taken(min)'].apply(
        lambda texto_cortado: texto_cortado.split(' ')[1]).astype(
        int)
    return df_final

# --------------------------------- INÍCIO DA ESTRUTURA LÓGICA DO CÓDIGO ---------------------------------------

#Importar arquivo
df = pd.read_csv(r'train.csv')
#Limpeza do código
df_final = clean_df(df)


# ----------------------------------------------- VISÃO EMPRESA ----------------------------------------------- #

 # =====================================
 #            Barra Lateral
 # =====================================
st.header('Marketplace - Visão Cliente')
image_path = "data-science_file.png"
image = Image.open(image_path)
st.sidebar.image(image,width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider('Até qual valor?',
                  value=datetime(2022,4,13),
                  min_value=datetime(2022,2,11),
                  max_value=datetime(2022,4,6),
                  format='DD-MM-YYYY')

## TODO:posso criar outra variavel com barra p usuario selecionar e assim ter mínimo e a outra serviria p ser
## TODO:a data fim e ai faria um filtro de inicio a partir da data inicial e o mesmo para a data fim la embaixo na linha 89.
## TODO: O filtro lá é só de data menor. Fzr um IF p verificar se o filtro ta correto tbm.
## TODO: Isso só se necessário mesmo.


st.sidebar.markdown("""----""")

traffic_options = st.sidebar.multiselect('Quais as condições do trânsito',['Low','Medium','High','Jam'],
                                         default=['Low','Medium','High','Jam'])

st.sidebar.markdown("""----""")
st.sidebar.markdown("""### Powered by Vinicius Rodrigues""")

## ===== FILTRO DE DATAS =====
filtro_linhas = df_final['Order_Date'] < date_slider
df_final = df_final.loc[filtro_linhas, :]

## ===== FILTRO DE TRÂNSITO =====

filtro_linhas_02 = df_final['Road_traffic_density'].isin(traffic_options)
df_final = df_final.loc[filtro_linhas_02,:]
st.dataframe(df_final)
# =====================================
#        layout no Streamlit
# =====================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])

with tab1:
    with st.container():
        # ====== Order Metric
        fig = order_metric(df_final)
        st.markdown('##  Entregas por dia')
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown("""-----""")
        col1, col2 = st.columns(2)
        with col1:
            fig = traffic_order_share(df_final)
            st.header('Entregas por tipo de tráfego')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.header('Entregas por tipo de trafégo por cidade')
            fig = traffic_order_city(df_final)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("""-----""")
with tab2:
    with st.container():
        st.markdown('## Entregas por semana')
        fig = order_by_week(df_final)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("""-----""")
    with st.container():
        st.markdown('## Média de entregas por entregador semanal')
        fig = order_share_by_week(df_final)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("""-----""")
with tab3:
    st.markdown('## Mapa de entregas ')
    country_maps(df_final)
    st.markdown("""-----""")



