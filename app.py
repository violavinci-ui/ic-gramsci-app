import streamlit as st
import requests
import re
from datetime import datetime

# Configurazione della schermata stile app mobile
st.set_page_config(
    page_title="IC Albano - Circolari Docenti",
    page_icon="👨‍🏫",
    layout="centered"
)

# Stile CSS personalizzato
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
        border-left: 5px solid #d9534f; /* Bordo rosso/arancio per evidenziare l'area docenti */
    }
    .badge {
        background-color: #ffebe9;
        color: #c92a2a;
        font-size: 0.75rem;
        font-weight: bold;
        padding: 3px 8px;
        border-radius: 6px;
        display: inline-block;
        margin-bottom: 6px;
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
    </style>
""", unsafe_allow_html=True)

st.title("👨‍🏫 IC Albano Pavona")
st.subheader("📢 Solo Circolari Docenti")

BASE_URL = "https://www.icalbanopavona.edu.it"

@st.cache_data(ttl=300)
def fetch_circolari_docenti():
    try:
        # Tenta il recupero con filtro sulla tipologia 'circolari-per-docenti'
        api_url = f"{BASE_URL}/wp-json/wp/v2/circolare?tipologia-circolare=circolari-per-docenti&per_page=20"
        response = requests.get(api_url, timeout=6)
        
        # Se la tassonomia usa un formato diverso, recupera le circolari generali per poi filtrarle via codice
        if response.status_code != 200 or len(response.json()) == 0:
            api_url = f"{BASE_URL}/wp-json/wp/v2/circolare?per_page=30"
            response = requests.get(api_url, timeout=6)
            if response.status_code == 200:
                posts = response.json()
                # Filtra mantenendo solo i titoli che riguardano i docenti/personale
                docenti_posts = [
                    p for p in posts 
                    if any(term in p.get('title', {}).get('rendered', '').lower() 
                           for term in ['docent', 'collegio', 'consiglio', 'scrutini', 'convocaz', 'personale', 'punti'])
                ]
                return docenti_posts
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

with st.spinner("Scaricamento circolari docenti..."):
    posts = fetch_circolari_docenti()

if posts is None:
    st.error("Impossibile connettersi al sito dell'IC Albano Pavona.")
elif len(posts) == 0:
    st.info("Nessuna circolare specifica per i docenti trovata di recente.")
else:
    st.caption(f"Trovate {len(posts)} circolari per il personale docente.")
    
    ricerca = st.text_input("🔍 Filtra (es. 'Collegio', 'Consiglio', 'Orario')...", "")
    
    count = 0
    for post in posts:
        raw_title = post.get('title', {}).get('rendered', 'Senza titolo')
        title = re.sub('<.*?>', '', raw_title)
        link = post.get('link', '#')
        date_raw = post.get('date', '')
        
        try:
            dt = datetime.fromisoformat(date_raw)
            date_formatted = dt.strftime('%d/%m/%Y alle %H:%M')
        except:
            date_formatted = date_raw
            
        if ricerca.lower() in title.lower():
            count += 1
            st.markdown(f"""
                <div class="card">
                    <span class="badge">AREA DOCENTI</span>
                    <div class="date">📅 {date_formatted}</div>
                    <div class="title">{title}</div>
                </div>
            """, unsafe_allow_html=True)
            st.link_button("📄 Apri circolare integrata", link)
            st.write("")

    if count == 0 and ricerca:
        st.warning("Nessuna circolare corrisponde alla parola cercata.")

if st.button("🔄 Aggiorna circolari"):
    st.rerun()
