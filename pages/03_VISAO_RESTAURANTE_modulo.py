from datetime import datetime
import pandas as pd
import numpy as np
import folium
import plotly.express as px
import plotly.colors
import streamlit as st
import plotly.graph_objects as go
import plotly.offline as pyo
from PIL import Image
from haversine import haversine

st.set_page_config(page_title='Visão Restaurante',page_icon="🍛",layout='wide')

#------------- FUNÇÕES ---------------

#FUNÇÃO GRÁFICO DE BARRAS DA MÉDIA E DO DESVIO PADRÃO DE TEMPO DE ENTREGA POR CIDADE
def avg_std_time_graph(df_final):
    """NESTE GRÁFICO O DESVIO PADRÃO É MOSTRADO NO PARÂMETRO 'ERROR',
    ONDE MOSTRA-SE O QUE 'FOGE' DA MÉDIA EM TAL CIDADE. """
    df_aux = df_final.loc[:, ['Time_taken(min)', 'City']].groupby(['City']).agg(
        {'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['Time_Taken_Mean', 'Time_Taken_std']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control', x=df_aux['City']
                         , y=df_aux['Time_Taken_Mean'],
                         error_y=dict(type='data', array=df_aux['Time_Taken_std'])))
    fig.update_layout(barmode='group')
    fig.update_layout(height=580)
    return fig

#FUNÇÃO CÁLCULO MÉDIO DE DISTÂNCIA
def distance(df_final,fig=False):
    """ (fig = true plota um gráfico do mesmo do tempo medio por cidade)
    """
    columns = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude',
               'Delivery_location_longitude']

    df_final['distance_km'] = df_final.apply(lambda linha: '{:.2f}'.format(
        (haversine((linha[columns[0]], linha[columns[1]]),
                   (linha[columns[2]], linha[columns[3]])))), axis=1).astype(float)
    if fig == False:
        avg_distance = np.round(df_final['distance_km'].mean(), 2)
        return avg_distance
    else:
        avg_distance = df_final.loc[:, ['City', 'distance_km']].groupby(['City']).mean().reset_index()
        fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance_km'],
                                 pull=[0.007, 0.007, 0.007],marker=dict(colors=['#FF6347', '#00FA9A', '#1E90FF'])
                                 )])
        fig.update_layout(height=500)
        return fig

#FUNÇÃO GRÁFICO DE PIZZA DE DESVIO PADRÃO E MÉDIA DE TEMPO DE ENTREGA POR CIDADE E TIPO DE TRÁFEGO

def avg_std_time_on_traffic(df_final):
    """ESSA FUNÇÃO MOSTRA UM GRÁFICO QUE POSSUI O TEMPO DE ENTREGA ATRAVÉS DOS TIPOS DE TRAFEGOS, SUAS MÉDIAS E DESVIO PADRÕES
    E AS COLORE DE VERMELHO P AZUL A PARTIR DO NIVEL (TOP) DE DESVIO PADRÃO.
    AO PASSAR O MOUSE VEMOS OS VALORES DA MÉDIA E DESVIO PADRÃO TBM"""
    df_aux = df_final.loc[:, ['Time_taken(min)', 'City', 'Road_traffic_density']].groupby(
        ['City', 'Road_traffic_density']).agg(
        {'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['Time_Taken_Mean', 'Time_Taken_std']
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='Time_Taken_Mean',
                      color='Time_Taken_std',
                      color_continuous_scale='RdBu',
                      color_continuous_midpoint=np.average(df_aux['Time_Taken_std']))
    fig.update_layout(height=550)
    return fig

#FUNÇÃO CÁLCULO MÉDIO/DESVIO PADRÃO DAS ENTREGAS
def avg_std_time_delivery(df_final,op=None,festival=None):
    """ O argumento OP tem que receber um valor, seja 'std' - desvio padrão
    ou 'avg' - media. O que será calculado é o tempo médio das entregas e fornecido
    ou o desvio padrão ou média do mesmo."""
    df_aux = df_final.loc[df_final['Festival'] == festival, ['Time_taken(min)', 'Festival']].groupby(
       ['Festival']).agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['Time_Taken_Mean', 'Time_Taken_std']
    df_aux = df_aux.reset_index()
    if op == 'avg':
        media_or_std_festival = np.round(df_aux['Time_Taken_Mean'],2)
    elif op == 'std':
        media_or_std_festival = np.round(df_aux['Time_Taken_std'], 2)
    else:
        media_or_std_festival = None
    return media_or_std_festival


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


# ----------------------------------------------- VISÃO RESTAURANTE ----------------------------------------------- #



 # =====================================
 #            Barra Lateral
 # =====================================

st.header('Marketplace - Visão Restaurantes')
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
lista_weather = df_final['Weatherconditions'].unique()
weather_options = st.sidebar.multiselect('Quais as condições do clima',lista_weather,
                                         default=lista_weather)

st.sidebar.markdown("""----""")
st.sidebar.markdown("""### Powered by Vinicius Rodrigues""")

## ===== FILTRO DE DATAS =====
filtro_linhas = df_final['Order_Date'] < date_slider
df_final = df_final.loc[filtro_linhas, :]

## ===== FILTRO DE TRÂNSITO =====

filtro_linhas_02 = df_final['Road_traffic_density'].isin(traffic_options)
df_final = df_final.loc[filtro_linhas_02,:]


## ===== FILTRO DE CLIMA =====

filtro_linhas_03 = df_final['Weatherconditions'].isin(weather_options)
df_final = df_final.loc[filtro_linhas_03,:]

#######################

st.dataframe(df_final)

# =====================================
#        layout no Streamlit
# =====================================

tab1,tab2,tab3 = st.tabs(['Visão Gerencial','_','_'])

with tab1:
    with st.container():
        st.markdown("""--------""")
        st.title('Overal Metrics')
        col1,col2,col3,col4,col5,col6 = st.columns(6)
        with col1:
            delivery_unique = len(df_final['Delivery_person_ID'].unique())
            col1.metric('Entregadores Únicos registrados',delivery_unique)

        with col2:
            avg_distance = distance(df_final,fig=False)
            col2.metric('Distância média das entregas', avg_distance)

        with col3:
            media_festival = avg_std_time_delivery(df_final,op='avg',festival='Yes')
            col3.metric('Tempo média das entregas com festival', media_festival)

        with col4:
            std_festival = avg_std_time_delivery(df_final, op='std',festival='Yes')
            col4.metric('Desvio Padrão das entregas com festival',std_festival)

        with col5:
            mean_time_no_festival = avg_std_time_delivery(df_final, op='avg', festival='No')
            col5.metric('Tempo média das entregas sem festival',mean_time_no_festival)

        with col6:
            std_time_no_festival = avg_std_time_delivery(df_final, op='std', festival='No')
            col6.metric('Desvio Padrão das entregas sem festival',std_time_no_festival)

    with st.container():
        st.markdown("""--------""")
        col1,col2 = st.columns(2)
        with col1:
            st.title('Tempo médio de entrega por cidade')
            fig = avg_std_time_graph(df_final)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.title('Tempo médio e desvio padrão por cidade e tipo de pedido')
            st.markdown(""" """)
            st.markdown(""" """)
            st.markdown(""" """)
            st.markdown(""" """)
            df_aux = df_final.loc[:, ['Time_taken(min)', 'City', 'Type_of_order']].groupby(['City', 'Type_of_order']).agg(
                {'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['Time_Taken_Mean', 'Time_Taken_std']
            df_aux = df_aux.reset_index()
            st.dataframe(df_aux, use_container_width=True,height=450)#height=450

    with st.container():
        st.markdown("""--------""")
        st.title('Distribuição do Tempo')
        col1,col2 = st.columns(2)
        with col1:
            st.markdown('### Tempo médio por cidade')
            fig = distance(df_final,fig=True)
            st.plotly_chart(fig,use_container_width=True,hidth=1000)
        with col2:
            st.markdown('### Desvio Padrão por Cidade e Tráfego')
            fig = avg_std_time_on_traffic(df_final)
            st.plotly_chart(fig,use_container_width=True)
    st.markdown("""--------""")






