import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(
    page_title="Análise de Estabilidade - Iogurte",
    page_icon="microbe",
    layout="wide"
)

@st.cache_data
def load_data():
    file_path = 'contagem_microbiana.csv'

    if not os.path.exists(file_path):
        st.error(f"Arquivo '{file_path}' não encontrado.")
        return None

    df = pd.read_csv(file_path, sep=None, engine="python", dtype=str)

    colunas_numericas = [
        'pH', 'Acidez_Titravel',
        'Contagem_Mesofila',
        'Contagem_Psicrofila',
        'Aceitabilidade_Sensorial'
    ]

    for col in colunas_numericas:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.replace(",", ".", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


df = load_data()

if df is not None:

    st.sidebar.title("Filtros")

    temperaturas = sorted(df['Temperatura_Armazenamento'].dropna().unique())
    temp_sel = st.sidebar.multiselect("Temperatura (°C)", temperaturas, default=[])

    dias = sorted(df['Dias_Armazenamento'].dropna().unique())
    dias_sel = st.sidebar.multiselect("Dias", dias, default=[])

    df_filtered = df.copy()

    if temp_sel:
        df_filtered = df_filtered[df_filtered['Temperatura_Armazenamento'].isin(temp_sel)]

    if dias_sel:
        df_filtered = df_filtered[df_filtered['Dias_Armazenamento'].isin(dias_sel)]

    st.title("📊 Visualização Completa da Análise Estatística — Shelf-life do Iogurte")

    if df_filtered.empty:
        st.warning("Selecione filtros para iniciar.")
        st.stop()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Amostras", len(df_filtered))
    col2.metric("pH Médio", f"{df_filtered['pH'].mean():.2f}")
    col3.metric("Mesófilos Médio", f"{df_filtered['Contagem_Mesofila'].mean():.2f}")
    col4.metric("Aceitação Média", f"{df_filtered['Aceitabilidade_Sensorial'].mean():.2f}")

    st.subheader("Base Filtrada")
    st.dataframe(df_filtered.fillna("-"))

    tab_micro, tab_media, tab_mediana, tab_std, tab_min, tab_max, tab_amp, tab_cv, tab_formulas = st.tabs([
        "🦠 Microbiologia",
        "📈 Média",
        "📊 Mediana",
        "📉 Desvio Padrão",
        "🔽 Mínimo",
        "🔼 Máximo",
        "📏 Amplitude",
        "📐 Coef. Variação",
        "📘 Como os Cálculos Foram Feitos"
    ])

    variaveis = [
        'pH',
        'Acidez_Titravel',
        'Contagem_Mesofila',
        'Contagem_Psicrofila',
        'Aceitabilidade_Sensorial'
    ]

    with tab_micro:
        st.subheader("Crescimento Microbiano")

        fig_meso = px.line(
            df_filtered,
            x='Dias_Armazenamento',
            y='Contagem_Mesofila',
            color='Temperatura_Armazenamento',
            markers=True
        )
        fig_meso.add_hline(y=6, line_dash="dash", line_color="red")
        st.plotly_chart(fig_meso, use_container_width=True)

        fig_psicro = px.line(
            df_filtered,
            x='Dias_Armazenamento',
            y='Contagem_Psicrofila',
            color='Temperatura_Armazenamento',
            markers=True
        )
        fig_psicro.add_hline(y=5, line_dash="dash", line_color="red")
        st.plotly_chart(fig_psicro, use_container_width=True)

    with tab_media:
        media = df_filtered[variaveis].mean()
        fig = px.bar(x=media.index, y=media.values, title="Médias das Variáveis")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(media.to_frame("Média"))

    with tab_mediana:
        mediana = df_filtered[variaveis].median()
        fig = px.bar(x=mediana.index, y=mediana.values, title="Mediana das Variáveis")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(mediana.to_frame("Mediana"))

    with tab_std:
        std = df_filtered[variaveis].std()
        fig = px.bar(x=std.index, y=std.values, title="Desvio Padrão")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(std.to_frame("Desvio Padrão"))

    with tab_min:
        minimo = df_filtered[variaveis].min()
        fig = px.bar(x=minimo.index, y=minimo.values, title="Valores Mínimos")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(minimo.to_frame("Mínimo"))

    with tab_max:
        maximo = df_filtered[variaveis].max()
        fig = px.bar(x=maximo.index, y=maximo.values, title="Valores Máximos")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(maximo.to_frame("Máximo"))

    with tab_amp:
        amplitude = df_filtered[variaveis].max() - df_filtered[variaveis].min()
        fig = px.bar(x=amplitude.index, y=amplitude.values, title="Amplitude das Variáveis")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(amplitude.to_frame("Amplitude"))

    with tab_cv:
        cv = (df_filtered[variaveis].std() / df_filtered[variaveis].mean()) * 100
        fig = px.bar(x=cv.index, y=cv.values, title="Coeficiente de Variação (%)")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(cv.to_frame("CV (%)"))
    
    with tab_formulas:

      st.header("📘 Como os Cálculos Estatísticos Foram Feitos")

      c_media, c_mediana, c_std, c_min, c_max, c_amp, c_cv = st.tabs([
          "✅ Média",
          "✅ Mediana",
          "✅ Desvio Padrão",
          "✅ Mínimo",
          "✅ Máximo",
          "✅ Amplitude",
          "✅ Coef. de Variação"
      ])

      exemplo = df_filtered["pH"].dropna().head(5)

      with c_media:
          st.markdown("**Fórmula:** Média = (x₁ + x₂ + ... + xₙ) / n")
          st.write("Exemplo com os 5 primeiros valores de pH:")
          st.write(exemplo.values)
          st.write("Média =", round(exemplo.mean(), 3))

      with c_mediana:
          st.markdown("**Definição:** Valor central dos dados ordenados.")
          st.write("Valores:", exemplo.values)
          st.write("Mediana =", round(exemplo.median(), 3))

      with c_std:
          st.markdown("### ✅ Desvio Padrão")
          st.markdown("**Fórmula:** σ = √( Σ (xᵢ − μ)² / n )")

          valores = exemplo.values
          media_ex = exemplo.mean()

          st.write("Valores usados:")
          st.write(valores)

          st.write("Média (μ):", round(media_ex, 4))

          desvios = valores - media_ex
          st.write("Cada (xᵢ − μ):")
          st.write(desvios)

          quadrados = desvios ** 2
          st.write("Cada (xᵢ − μ)²:")
          st.write(quadrados)

          soma_quadrados = quadrados.sum()
          st.write("Soma dos quadrados:", round(soma_quadrados, 4))

          n = len(valores)
          st.write("Quantidade de valores (n):", n)

          variancia = soma_quadrados / n
          st.write("Variância:", round(variancia, 4))

          desvio_final = variancia ** 0.5
          st.success(f"✅ Desvio padrão final = {round(desvio_final, 4)}")


      with c_min:
          st.markdown("Menor valor observado.")
          st.write("Mínimo =", exemplo.min())

      with c_max:
          st.markdown("Maior valor observado.")
          st.write("Máximo =", exemplo.max())

      with c_amp:
          st.markdown("### ✅ Amplitude")
          st.markdown("**Fórmula:** Amplitude = Máximo − Mínimo")

          valor_min = exemplo.min()
          valor_max = exemplo.max()
          amplitude_ex = valor_max - valor_min

          st.write("Valores usados:")
          st.write(exemplo.values)

          st.write("Mínimo:", valor_min)
          st.write("Máximo:", valor_max)

          st.success(f"✅ Amplitude = {valor_max} − {valor_min} = {round(amplitude_ex, 4)}")

      with c_cv:
          st.markdown("### ✅ Coeficiente de Variação (CV)")
          st.markdown("**Fórmula:** CV (%) = (Desvio Padrão / Média) × 100")

          valores = exemplo.values
          media_ex = exemplo.mean()

          st.write("Valores usados:")
          st.write(valores)

          st.write("Média (μ):", round(media_ex, 4))

          desvios = valores - media_ex
          quadrados = desvios ** 2
          soma_quadrados = quadrados.sum()
          n = len(valores)
          variancia = soma_quadrados / n
          desvio_padrao = variancia ** 0.5

          st.write("Desvio padrão (σ):", round(desvio_padrao, 4))

          cv_exemplo = (desvio_padrao / media_ex) * 100

          st.write(f"CV (%) = ({round(desvio_padrao,4)} / {round(media_ex,4)}) × 100")

          st.success(f"✅ Coeficiente de Variação Final = {round(cv_exemplo, 2)} %")

else:
    st.info("Aguardando carregamento do arquivo...")
