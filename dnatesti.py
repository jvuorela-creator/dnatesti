import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Sivun asetukset
st.set_page_config(page_title="DNA 3D", layout="wide")

st.title("🧬 DNA-segmenttien 3D-visualisointi")

# 1. Tiedoston lataus
uploaded_file = st.file_uploader("Valitse CSV-tiedosto", type=["csv"])

if uploaded_file is not None:
    try:
        # Luetaan data
        df = pd.read_csv(uploaded_file)
        
        # DEBUG: Näytetään data, jotta nähdään onko lataus onnistunut
        st.write("Ladattu data (ensimmäiset rivit):")
        st.dataframe(df.head())

        # 2. Esikäsittely
        # Varmistetaan sarakenimet (poistetaan turhat välilyönnit nimistä varmuuden vuoksi)
        df.columns = df.columns.str.strip()
        
        # Tarkistetaan että tarvittavat sarakkeet löytyvät
        required_cols = ['Match Name', 'Chromosome', 'Start Location', 'End Location']
        if not all(col in df.columns for col in required_cols):
            st.error(f"Virhe: CSV-tiedostosta puuttuu jokin näistä sarakkeista: {required_cols}")
            st.stop()

        # Osumien numerointi Y-akselia varten
        matches = df['Match Name'].unique()
        match_map = {name: i for i, name in enumerate(matches)}
        df['Match_Y'] = df['Match Name'].map(match_map)

        # Kromosomien numerointi (X=23, Y=24)
        df['Chromosome'] = df['Chromosome'].replace({'X': 23, 'x': 23, 'Y': 24, 'y': 24})
        df['Chromosome'] = pd.to_numeric(df['Chromosome'], errors='coerce')
        df = df.dropna(subset=['Chromosome']) # Poistetaan rivit joissa kromosomi ei kelpaa

        # 3. Luodaan Plotly 3D-kuvaaja
        fig = go.Figure()

        # Käydään läpi jokainen osuma ja lisätään kuvaajaan
        for match_name in matches:
            sub_df = df[df['Match Name'] == match_name]
            
            # Rakennetaan viivat segmenteille
            # Plotlyssa katkonaiset viivat tehdään lisäämällä None väliin
            x_vals = []
            y_vals = []
            z_vals = [] # Z on tässä tapauksessa sijainti (bp)
            
            for _, row in sub_df.iterrows():
                # Viiva alkaa (Start) ja loppuu (End)
                x_vals.extend([row['Chromosome'], row['Chromosome'], None])
                y_vals.extend([row['Match_Y'], row['Match_Y'], None])
                z_vals.extend([row['Start Location'], row['End Location'], None])
            
            fig.add_trace(go.Scatter3d(
                x=x_vals,
                y=y_vals,
                z=z_vals,
                mode='lines',
                line=dict(width=10), # Viivan paksuus
                name=match_name
            ))

        # Akselien nimet
        fig.update_layout(
            scene=dict(
                xaxis=dict(title='Kromosomi', tickmode='linear', tick0=1, dtick=1),
                yaxis=dict(title='Osuma', tickvals=list(range(len(matches))), ticktext=matches),
                zaxis=dict(title='Sijainti (bp)'),
            ),
            margin=dict(r=0, l=0, b=0, t=0), # Minimoidaan reunat
            height=700
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Tapahtui virhe: {e}")
else:
    st.info("Lataa CSV-tiedosto aloittaaksesi.")
