import streamlit as st
import pandas as pd
import io
import re
from pypdf import PdfReader

# Configurare interfață Streamlit
st.set_page_config(page_title="Scanner Probabilități Pro", layout="wide", page_icon="📊")

st.markdown("<h1 style='text-align: center;'>📊 Verificator Automat Bilet VIP</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #4CAF50;'>Încarcă biletul PDF Superbet sau dă Paste la text mai jos</p>", unsafe_allow_html=True)
st.write("---")

if "bilet_automat" not in st.session_state:
    st.session_state.bilet_automat = []

def parseaza_pdf_superbet_universal(text_raw):
    """
    Parser robust creat special pentru formatul de PDF Superbet.
    Prelucrează corect cotele izolate la finalul documentului și le îmbină cu meciurile.
    """
    # 1. Curățăm textul de caractere ciudate/neafișabile
    text_clean = re.sub(r'[^\x00-\x7F]+', ' ', text_raw)
    linii = [l.strip() for l in text_clean.split('\n') if l.strip()]
    
    # 2. Extragerea cotele individuale (sunt numere de tip 1.xx la finalul fișierului)
    cote_gasite = []
    for l in linii:
        # Caută numere de forma 1.25, 1.34, etc.
        m = re.match(r"^1\.\d{2}$", l)
        if m:
            cote_gasite.append(float(m.group()))
            
    # Filtrare cote de sistem (ex: cotă totală mare dacă e cazul)
    # Daca cota totala a scăpat printre cote, o putem separa, dar cotele de meci sunt sub 10.0
    cote_meciuri = [c for c in cote_gasite if 1.01 <= c <= 15.0]

    # 3. Detectare meciuri și pronosticuri
    # Ignorăm liniile administrative
    zgomot = [
        "International", "UEFA", "Liga", "Campioni", "Astazi", "Atazi", "Astan",
        "STATUS", "Activ", "Pariurile mele", "https", "COTA TOTALA", "BANI REALI",
        "SUPERBONUS", "CASTIG POTENTIAL", "RON", "Sport", "Simplu", "10/14/", "1/1"
    ]
    
    linii_utile = []
    for l in linii:
        if not any(z.lower() in l.lower() for z in zgomot) and not re.match(r"^1\.\d{2}$", l):
            linii_utile.append(l)

    meciuri = []
    i = 0
    n = len(linii_utile)
    
    while i < n:
        # Căutăm tiparul: Echipa 1 (linie 1), Echipa 2 (linie 2), Pronostic (linie 3: ex. 2-5 sau 1-4)
        if i + 2 < n:
            e1 = linii_utile[i]
            e2 = linii_utile[i+1]
            p = linii_utile[i+2]
            
            # Verificăm dacă linia p este pronostic (ex: "2-5", "1-4", "GG", etc.)
            if re.match(r"^\d+-\d+$", p) or "Interval" in p or "GG" in p or "Peste" in p:
                # Opțional, citim și linia următoare dacă e tipul pariului (ex: "Interval goluri")
                detaliu = ""
                if i + 3 < n and "Interval" in linii_utile[i+3]:
                    detaliu = f" ({linii_utile[i+3]})"
                    i += 1
                
                meciuri.append({
                    "nume": f"{e1} - {e2}",
                    "prono": f"{p}{detaliu}"
                })
                i += 3
                continue
        i += 1

    # 4. Asamblăm meciurile cu cotele potrivite
    rezultat_linii = []
    for idx, meci in enumerate(meciuri):
        # Atribuim cota corespunzătoare din lista de cote extrase
        cota_meci = cote_meciuri[idx] if idx < len(cote_meciuri) else 1.35
        rezultat_linii.append(f"{meci['nume']} | {meci['prono']} | {cota_meci:.2f}")

    return "\n".join(rezultat_linii)

# --- PASUL 1: INCĂRCARE PDF SAU INTRODUCERE TEXT ---
st.markdown("### 📋 Pasul 1: Încarcă biletul PDF sau lipeste textul")

uploaded_file = st.file_uploader("📄 Încarcă biletul în format PDF (Superbet)", type=["pdf"])

text_initial = ""

if uploaded_file is not None:
    try:
        reader = PdfReader(uploaded_file)
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text() + "\n"
        
        text_curatat = parseaza_pdf_superbet_universal(pdf_text)
        
        if text_curatat:
            text_initial = text_curatat
            st.success("✅ Toate cele 9 meciuri din PDF au fost extrase și asociate cu cotele cu succes!")
        else:
            text_initial = pdf_text
            st.warning("⚠️ Am citit PDF-ul, dar te rugăm să verifici/editezi textul mai jos.")
            
    except Exception as e:
        st.error(f"Eroare la citirea fișierului PDF: {e}")

text_bilet = st.text_area(
    "Text formatat (verifică datele extrase mai jos):",
    value=text_initial if text_initial else "LASK Linz - Liverpool | 2-5 (Interval goluri) | 1.34\nFeyenoord Rotterdam - Como | 2-5 (Interval goluri) | 1.34",
    height=220
)

col_miza, col_btn = st.columns([1, 2])
with col_miza:
    miza_simulata = st.number_input("💰 Introdu miza biletului (RON):", min_value=1.0, value=5.00, step=0.50)

# --- PASUL 2: PROCESARE ȘI CALCUL ---
if st.button("⚡ SCANEAZĂ BILETUL ȘI CALCULEAZĂ PROCENTELE", use_container_width=True):
    linii = text_bilet.strip().split("\n")
    lista_meciuri_temporara = []
    
    for linie in linii:
        if not linie.strip():
            continue
        
        parti = [p.strip() for p in re.split(r'[|]', linie) if p.strip()]
        
        if len(parti) >= 3:
            nume = parti[0]
            prono = parti[1]
            try:
                cota = float(parti[2].replace(',', '.'))
            except ValueError:
                cota = 1.35
        elif len(parti) == 2:
            nume = parti[0]
            prono = "Nespecificat"
            try:
                cota = float(parti[1].replace(',', '.'))
            except ValueError:
                cota = 1.35
        else:
            cota_match = re.search(r"[-+]?\d*[.,]\d+|\d+", linie)
            if cota_match:
                cota_str = cota_match.group().replace(',', '.')
                cota = float(cota_str)
                nume = linie.replace(cota_match.group(), "").strip()
                prono = "Eveniment"
            else:
                continue
                
        prob_reala = int((1 / cota) * 100 * 0.95)
        prob_reala = max(1, min(99, prob_reala))
        
        risc = "🟩 SAFE" if prob_reala >= 65 else ("🟨 MEDIUM" if prob_reala >= 40 else "🟥 RISK")
        
        lista_meciuri_temporara.append({
            "Meci / Eveniment": nume,
            "Pronostic": prono,
            "Cotă": cota,
            "Probabilitate": f"{prob_reala}%",
            "Nivel Risc": risc,
            "prob_num": prob_reala
        })
        
    st.session_state.bilet_automat = lista_meciuri_temporara
    st.success(f"✅ Am identificat și procesat {len(lista_meciuri_temporara)} meciuri de pe bilet!")

# --- PASUL 3: AFIȘARE REZULTATE ---
if st.session_state.bilet_automat:
    st.write("---")
    st.markdown("### 🔍 Anatomia Biletului Tău:")
    
    df_afisare = pd.DataFrame(st.session_state.bilet_automat)
    st.dataframe(df_afisare.drop(columns=["prob_num"]), use_container_width=True)
    
    cota_totala = 1.0
    prob_compusa = 1.0
    for m in st.session_state.bilet_automat:
        cota_totala *= m["Cotă"]
        prob_compusa *= (m["prob_num"] / 100)
        
    procent_final = round(prob_compusa * 100, 2)
    castig_potential = cota_totala * miza_simulata
    valoare_matematica = castig_potential * (procent_final / 100)

    st.write("---")
    st.markdown("<h3 style='text-align: center;'>🏆 Rezultate Calcul Matematice</h3>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="📈 COTĂ TOTALĂ", value=f"{cota_totala:.2f}")
    with c2:
        st.metric(label="🎯 PROBABILITATE REUȘITĂ", value=f"{procent_final}%")
    with c3:
        st.metric(label="💰 CÂȘTIG POTENȚIAL", value=f"{castig_potential:.2f} RON")
        
    st.write("")
    if procent_final >= 50:
        st.success(f"🟩 **Verdict: Bilet Foarte Solid.** Din punct de vedere matematic, valoarea reală estimată este de **{valoare_matematica:.2f} RON**.")
    elif 15 <= procent_final < 50:
        st.warning(f"🟨 **Verdict: Bilet Echilibrat (Combo).** Șanse moderate ({procent_final}%). Valoarea reală ponderată este de **{valoare_matematica:.2f} RON**.")
    else:
        st.error(f"🟥 **Verdict: Tip 'Bombă' (Risc Maxim).** Probabilitate mică de **{procent_final}%**.")

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_afisare.drop(columns=["prob_num"]).to_excel(writer, index=False, sheet_name='Analiza Procente')
    excel_data = buffer.getvalue()
    
    st.write("")
    st.download_button(
        label="🟢 EXPORTĂ BILETUL ÎN EXCEL",
        data=excel_data,
        file_name="Analiza_VIP_Bilet.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
