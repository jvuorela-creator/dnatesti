import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Sivun asetukset
st.set_page_config(page_title="MyHeritage DNA Visualisoija", layout="wide")

st.title("🧬 MyHeritage DNA-tulosten Visualisointi")
st.markdown("""
Tämä työkalu lukee MyHeritagen viemän (export) CSV-tiedoston ja luo siitä graafisia yhteenvetoja.
Lataa tiedosto alta aloittaaksesi.
""")

# Tiedoston lataaja
uploaded_file = st.file_uploader("Lataa MyHeritage DNA Matches CSV-tiedosto", type=['csv'])

def clean_currency(x):
    """Apufunktio cM-arvon siivoamiseen, jos se on muodossa '0.5% (35.4 cM)'"""
    if isinstance(x, str):
        # Etsitään luku cM-tekstin edestä tai sulkujen sisältä
        match = re.search(r'\(?(\d+(\.\d+)?)\s*cM\)?', x)
        if match:
            return float(match.group(1))
        return 0.0
    return x

if uploaded_file is not None:
    try:
        # Luetaan CSV. MyHeritage-tiedostot käyttävät usein pilkkua erottimena.
        df = pd.read_csv(uploaded_file)

        # Tarkistetaan yleisimmät sarakkeet ja yritetään tunnistaa oikeat
        # MyHeritage CSV:ssä sarakkeet ovat usein: Name, Age, Country, Shared DNA, Shared segments, Largest segment
        
        # Normalisoidaan sarakkeiden nimet (poistetaan välilyönnit alusta/lopusta)
        df.columns = df.columns.str.strip()

        # Etsitään Shared DNA -sarake
        cM_col = None
        candidates = ['Shared DNA', 'Shared DNA (cM)', 'Jaettu DNA']
        for col in df.columns:
            if any(c in col for c in candidates):
                cM_col = col
                break
        
        segment_col = None
        seg_candidates = ['Shared segments', 'Segments', 'Jaetut segmentit']
        for col in df.columns:
            if any(c in col for c in seg_candidates):
                segment_col = col
                break

        if cM_col:
            # Datan puhdistus: Muutetaan cM-sarake numeroiksi
            df['Cleaned_cM'] = df[cM_col].apply(clean_currency)
            
            # Sivupalkin suodattimet
            st.sidebar.header("Suodattimet")
            min_cm = st.sidebar.slider("Minimi cM", 0, int(df['Cleaned_cM'].max()), 8)
            max_cm = st.sidebar.slider("Maksimi cM", 0, int(df['Cleaned_cM'].max()), int(df['Cleaned_cM'].max()))
            
            # Suodatetaan data
            filtered_df = df[(df['Cleaned_cM'] >= min_cm) & (df['Cleaned_cM'] <= max_cm)]
            
            st.write(f"Näytetään **{len(filtered_df)}** osumaa valitulla välillä ({min_cm} - {max_cm} cM).")

            # --- Visualisoinnit ---
            
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Osumien jakauma (Histogrammi)")
                fig_hist = px.histogram(filtered_df, x="Cleaned_cM", nbins=50, 
                                        title="Kuinka monta osumaa eri cM-tasoilla",
                                        labels={'Cleaned_cM': 'Jaettu DNA (cM)'})
                st.plotly_chart(fig_hist, use_container_width=True)

            with col2:
                if segment_col:
                    st.subheader("Laatu: cM vs. Segmenttien määrä")
                    fig_scatter = px.scatter(filtered_df, x="Cleaned_cM", y=segment_col, 
                                             hover_data=[df.columns[0]], # Oletetaan että 1. sarake on Nimi
                                             title="Kokonais-cM vs. Segmenttien lkm",
                                             labels={'Cleaned_cM': 'Jaettu DNA (cM)', segment_col: 'Segmenttien määrä'})
                    st.plotly_chart(fig_scatter, use_container_width=True)
                else:
                    st.warning("Segmentti-tietoa ei löytynyt, sirontakuviota ei voida piirtää.")

            # Taulukko datasta
            st.subheader("Datarivit")
            st.dataframe(filtered_df.sort_values(by='Cleaned_cM', ascending=False))
            
        else:
            st.error("Ei löytynyt saraketta 'Shared DNA' tai vastaavaa. Tarkista CSV-tiedoston otsikot.")
            st.write("Löydetyt sarakkeet:", df.columns.tolist())

    except Exception as e:
        st.error(f"Virhe tiedoston lukemisessa: {e}")
