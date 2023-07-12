import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime
from PIL import Image

st.set_page_config(page_title='Visão Entregadores',page_icon="🚚",layout='wide')

#------------- FUNÇÕES ---------------

#FUNÇÃO DE TOP ENTREGAS POR CIDADE
def top_deliveries(df_final,top_asc):
    """ FUNÇÃO DEFINE O RANKING (TOP) ENTREGADORES DA CIDADE.
    MAIS LENTOS OU MAIS RÁPIDO. O PARÂMETRO 'TOP_ASC' DEFINE ISSO.
    SE ELE FOR FALSE = MAIS LENTOS, SE FOR TRUE MAIS RÁPIDOS.
    """
    df_aux = df_final.loc[:, ['Delivery_person_ID', 'Time_taken(min)', 'City']].groupby(
        ['City', 'Delivery_person_ID']).mean().reset_index().sort_values(['City', 'Time_taken(min)'],
                                                                         ascending=top_asc)
    df_aux_final = pd.DataFrame

    list_df = [df_aux.loc[df_aux['City'] == cidade, :].head(10).reset_index(drop=True) for cidade in
               cidades]

    df_aux_final = pd.concat(list_df)
    return df_aux_final


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


# ----------------------------------------------- VISÃO ENTREGADOR ----------------------------------------------- #



 # =====================================
 #            Barra Lateral
 # =====================================
st.header('Marketplace - Visão Entregadores')
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


#########

st.dataframe(df_final)

# =====================================
#        layout no Streamlit
# =====================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','_','_'])

with tab1:
    with st.container():
        st.subheader('Principais Métricas')
        col1,col2,col3,col4 = st.columns(4,gap='large')
        with col1:
            maior_idade = df_final.loc[:, 'Delivery_person_Age'].max()
            if not np.isnan(maior_idade):
                maior_idade = int(maior_idade)
            col1.metric('Maior idade', maior_idade)
        with col2:
            menor_idade = df_final.loc[:, 'Delivery_person_Age'].min()
            if not np.isnan(menor_idade):
                menor_idade = int(menor_idade)
            col2.metric('Menor idade', menor_idade)
        with col3:
            melhor_condicao = df_final.loc[:,'Vehicle_condition'].max()
            col3.metric('Melhor condição',melhor_condicao)
        with col4:
            pior_condicao = df_final.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condição', pior_condicao)
    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação média por entregador')
            df_avg_per_deliver = df_final.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']].groupby(
                ['Delivery_person_ID']).mean().reset_index()
            st.dataframe(df_avg_per_deliver, height=500)
        with col2:
            st.markdown('##### Avaliação média por trânsito')
            df_avg_std_by_traffic = df_final.loc[:, ['Road_traffic_density', 'Delivery_person_Ratings']].groupby(
                ['Road_traffic_density']).agg(
                {'Delivery_person_Ratings': ['mean', 'std']})
            df_avg_std_by_traffic.columns = ['Delivery_mean','Delivery_std']
            df_avg_std_by_traffic = df_avg_std_by_traffic.reset_index()
            st.dataframe(df_avg_std_by_traffic, height=190)
##############################################
            st.markdown('##### Avaliação média por clima')
            df_avg_std_by_weather = df_final.loc[:, ['Weatherconditions', 'Delivery_person_Ratings']].groupby(
                ['Weatherconditions']).agg(
                {'Delivery_person_Ratings': ['mean', 'std']})
            df_avg_std_by_weather.columns = ['Delivery_person_mean','Delivery_person_std']
            st.dataframe(df_avg_std_by_weather,height=248)



    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de entrega')

        col1,col2 = st.columns(2)
        with col1:
            cidades = ['Metropolitian','Urban','Semi-Urban']
            st.markdown('##### Top entregadores mais rápidos')
            df_aux_final = top_deliveries(df_final,top_asc=True)
            st.dataframe(df_aux_final)
        with col2:
            st.markdown('##### Top entregadores mais lentos')
            df_aux_final = top_deliveries(df_final,top_asc=False)
            st.dataframe(df_aux_final)


