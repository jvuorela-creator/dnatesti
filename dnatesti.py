import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# 1. Lataa data (vaihda tiedostonimi tarvittaessa)
filename = 'Shared DNA segments - one to many comparison.csv'
df = pd.read_csv(filename)

# 2. Datan esikäsittely
# Muutetaan osumien nimet numeroiksi Y-akselia varten
matches = df['Match Name'].unique()
match_map = {name: i for i, name in enumerate(matches)}
df['Match_Y'] = df['Match Name'].map(match_map)

# Varmistetaan, että kromosomit ovat numeroita (X -> 23)
df['Chromosome'] = df['Chromosome'].replace({'X': 23, 'x': 23, 'Y': 24, 'y': 24})
df['Chromosome'] = pd.to_numeric(df['Chromosome'], errors='coerce')

# 3. Luodaan 3D-kuvaaja
fig = plt.figure(figsize=(14, 10))
ax = fig.add_subplot(111, projection='3d')

# Värit eri osumille
colors = plt.cm.Set2(np.linspace(0, 1, len(matches)))
proxies = [] # Selitettä varten

# 4. Piirretään palkit
for i, match_name in enumerate(matches):
    sub_df = df[df['Match Name'] == match_name]
    
    # Koordinaatit
    # X = Kromosomi, Y = Osuma, Z = Sijainti (Start)
    x = sub_df['Chromosome'].values - 0.4
    y = sub_df['Match_Y'].values - 0.4
    z = sub_df['Start Location'].values
    
    # Palkin mitat
    dx = 0.8  # Palkin leveys (kromosomi-akselilla)
    dy = 0.8  # Palkin syvyys (osuma-akselilla)
    dz = sub_df['End Location'].values - sub_df['Start Location'].values # Palkin korkeus (segmentin pituus)
    
    color = colors[i]
    
    ax.bar3d(x, y, z, dx, dy, dz, color=color, alpha=0.7)
    
    # Tallennetaan väri selitettä varten
    proxies.append(plt.Rectangle((0,0), 1, 1, fc=color))

# 5. Akselien asetukset
ax.set_xlabel('Kromosomi')
ax.set_ylabel('Osuma')
ax.set_zlabel('Sijainti kromosomissa (bp)')

# Asetetaan X-akselin merkit kromosomien mukaan
all_chroms = sorted(df['Chromosome'].dropna().unique().astype(int))
ax.set_xticks(all_chroms)

# Asetetaan Y-akselin merkit osumien nimien mukaan
ax.set_yticks(range(len(matches)))
ax.set_yticklabels(matches, rotation=-15, verticalalignment='baseline')

ax.set_title('3D-visualisointi: Jaetut DNA-segmentit')
ax.legend(proxies, matches, loc='upper left', bbox_to_anchor=(1.05, 1), title="Osumat")

plt.tight_layout()
plt.show() # Tai plt.savefig('3d_kuva.png')
