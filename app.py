import streamlit as st
import requests
import re
from datetime import datetime

# Configurazione della schermata per renderla simile a un'app mobile
st.set_page_config(
    page_title="IC Albano Pavona - Circolari",
    page_icon="🏫",
    layout="centered"
)

# Stile CSS grafico "Mobile App style"
st.markdown("""
    <style>
    .stApp {
        background-color: #f4f6f9;
    }
    .card {
        background-color: white;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 12px;
        border-left: 4px solid #004080;
    }
    .date {
        font-size: 0.8rem;
        color: #6c757d;
        margin-bottom: 4px;
    }
    .title {
        font-size: 1rem;
        font-weight: 600;
        color: #212529;
    }
    .btn-container {
        margin-top: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏫 IC Albano Pavona")
st.subheader("📢 Ultime Circolari in Tempo Reale")

# URL base del sito della scuola
BASE_URL = "https://www.icalbanopavona.edu.it"

@st.cache_data(ttl=300) # Aggiorna la cache ogni 5 minuti
def fetch_circolari_wordpress():
    try:
        # Su molti WordPress scolastici, le circolari sono un post type personalizzato chiamato 'circolare'
        api_url = f"{BASE_URL}/wp-json/wp/v2/circolare?per_page=15"
        response = requests.get(api_url, timeout=6)
        
        # Se l'endpoint personalizzato non risponde, ripieghiamo sui post standard
        if response.status_code != 200:
            api_url = f"{BASE_URL}/wp-json/wp/v2/posts?per_page=15"
            response = requests.get(api_url, timeout=6)
            
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

with st.spinner("Scaricamento circolari dal sito della scuola..."):
    posts = fetch_circolari_wordpress()

if posts is None:
    st.error("Impossibile connettersi al sito dell'IC Albano Pavona. Riprova più tardi.")
elif len(posts) == 0:
    st.info("Nessuna circolare trovata al momento.")
else:
    st.success(f"Trovate le ultime circolari pubblicate!")
    
    # Barra di ricerca per filtrare tra le circolari caricate
    ricerca = st.text_input("🔍 Cerca per parola chiave (es. 'Mensa', 'Consiglio', 'Padel')...", "")
    
    count = 0
    for post in posts:
        # Estrazione e pulizia del titolo dai tag HTML
        raw_title = post.get('title', {}).get('rendered', 'Senza titolo')
        title = re.sub('<.*?>', '', raw_title)
        
        link = post.get('link', '#')
        date_raw = post.get('date', '')
        
        # Formattazione della data
        try:
            dt = datetime.fromisoformat(date_raw)
            date_formatted = dt.strftime('%d/%m/%Y alle %H:%M')
        except:
            date_formatted = date_raw
            
        # Applicazione del filtro di ricerca
        if ricerca.lower() in title.lower():
            count += 1
            st.markdown(f"""
                <div class="card">
                    <div class="date">📅 {date_formatted}</div>
                    <div class="title">{title}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Pulsante per aprire la circolare originale nel browser del telefono
            st.link_button("📄 Leggi circolare integrale", link)
            st.write("")

    if count == 0 and ricerca:
        st.warning("Nessuna circolare corrisponde alla ricerca effettuata.")

# Pulsante manuale per forzare l'aggiornamento dei dati bypassando la cache
if st.button("🔄 Aggiorna elenco"):
    st.rerun()
