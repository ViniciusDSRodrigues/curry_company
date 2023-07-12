import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="🕷️"
)
image_path = 'data-science_file.png'
image = Image.open(image_path)
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")
st.sidebar.markdown("""## Powered by Vinicius Rodrigues""")

st.write("# Curry Company Growth Dashboard")

st.markdown("""
            Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes
            ## Como utilizá-lo?
            - Visão empresa:
              - Visão Gerencial: Métricas gerais de comportamento
              - Visão Tática: Indicadores semanais de crescimento
              - Visão Geográfica: Insights de geocalização.
            - Visão entregador:
              - Acompanhamento dos indicadores semanais de crescimento
            - Visão restaurante:
              - Indicadores semanais de crescimento dos restaurantes
            
            ## Ask for help
            - Time de Data science no Discord - Vinicius D.S. Rodrigues#2530
            """)



