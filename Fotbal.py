import streamlit as st
import math

# Funcția Poisson standard
def poisson_probability(lambd, k):
    if lambd <= 0: return 0.0 if k > 0 else 1.0
    return (math.exp(-lambd) * (lambd ** k)) / math.factorial(k)

# Configurare aplicație
st.set_page_config(page_title="Predictor Poisson Total", page_icon="🎲", layout="wide")
st.title("🎲 Predictor Poisson: Toate Opțiunile (Inclusiv GG / NG)")
st.write("Acum poți introduce ambele cote pentru goluri (DA/NU) ca să vezi unde se ascunde valoarea reală.")

st.markdown("---")
col_stanga, col_dreapta = st.columns([1, 2])

with col_stanga:
    st.header("⚙️ Configurare Date")
    nume_meci = st.text_input("Nume Meci:", "Meciul Meu")
    
    # 1. Introducere Cote Soliști
    st.subheader("💰 1. Cote Soliști (Meci Întreg)")
    c_col1, c_colx, c_col2 = st.columns(3)
    with c_col1: c1 = st.number_input("Cotă 1:", min_value=1.01, value=1.88, step=0.01)
    with c_colx: cx = st.number_input("Cotă X:", min_value=1.01, value=3.75, step=0.01)
    with c_col2: c2 = st.number_input("Cotă 2:", min_value=1.01, value=4.00, step=0.01)
        
    # 2. Introducere Cote Goluri (Perechi: Peste/Sub și GG/NG)
    st.subheader("💰 2. Cote Goluri & Speciale")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        c_p15 = st.number_input("Cotă Peste 1.5 Goluri:", min_value=1.01, value=1.22, step=0.01)
        c_p25 = st.number_input("Cotă Peste 2.5 Goluri:", min_value=1.01, value=1.63, step=0.01)
        c_gg = st.number_input("Cotă Ambele Marchează - DA (GG):", min_value=1.01, value=1.77, step=0.01)
    with col_g2:
        st.caption("Opțiuni inverse (Sub / NU):")
        c_s25 = st.number_input("Cotă Sub 2.5 Goluri:", min_value=1.01, value=2.20, step=0.01)
        c_ng = st.number_input("Cotă Ambele Marchează - NU (NG):", min_value=1.01, value=2.00, step=0.01)
    
    st.subheader("💰 3. Cote Repriza 1")
    r_col1, r_colx, r_col2 = st.columns(3)
    with r_col1: cr1 = st.number_input("Cotă 1 Repriza 1:", min_value=1.01, value=2.45, step=0.01)
    with r_colx: crx = st.number_input("Cotă X Repriza 1:", min_value=1.01, value=2.25, step=0.01)
    with r_col2: cr2 = st.number_input("Cotă 2 Repriza 1:", min_value=1.01, value=4.30, step=0.01)

    st.markdown("---")
    
    # 3. Introducere Medii Goluri
    st.subheader("⚽ 4. Estimări Statistice (Medii)")
    m_g = st.number_input("Medie Goluri Gazde:", min_value=0.0, value=1.90, step=0.1)
    m_o = st.number_input("Medie Goluri Oaspeți:", min_value=0.0, value=1.50, step=0.1)

    st.markdown("---")
    st.subheader("💵 5. Setări Management Bani")
    banca = st.number_input("Banca ta totală (RON):", min_value=10.0, value=1000.0, step=50.0)
    fracțiune_kelly = st.slider("Multiplicator Kelly:", min_value=0.05, max_value=1.0, value=0.20, step=0.05)

with col_dreapta:
    st.header(f"🎯 Rezultate & Expected Value (EV) pentru {nume_meci}")
    
    # --- CALCULE POISSON MECI ÎNTREG ---
    p1, px, p2, p_p15, p_p25, p_gg = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    for g in range(9):
        for o in range(9):
            prob = poisson_probability(m_g, g) * poisson_probability(m_o, o)
            if g > o: p1 += prob
            elif g == o: px += prob
            else: p2 += prob
            
            if (g + o) > 1: p_p15 += prob
            if (g + o) > 2: p_p25 += prob
            if g > 0 and o > 0: p_gg += prob

    # Inversul probabilităților pentru piețele complementare
    p_s25 = 1.0 - p_p25
    p_ng = 1.0 - p_gg

    # --- CALCULE POISSON REPRIZA 1 ---
    m_g_r1, m_o_r1 = m_g * 0.38, m_o * 0.38
    pr1, prx, pr2 = 0.0, 0.0, 0.0
    for g in range(6):
        for o in range(6):
            prob_r1 = poisson_probability(m_g_r1, g) * poisson_probability(m_o_r1, o)
            if g > o: pr1 += prob_r1
            elif g == o: prx += prob_r1
            else: pr2 += prob_r1

    pariuri_valoroase = []

    def analizeaza_optiune(nume, prob, cota):
        ev = (prob * cota) - 1
        culoare = "green" if ev > 0 else "red"
        status = "🔥 DA" if ev > 0 else "❌ NU"
        
        if ev > 0:
            b_factor = cota - 1
            q = 1 - prob
            kelly_brut = (prob * b_factor - q) / b_factor
            miza_recomandata = kelly_brut * fracțiune_kelly * banca
            pariuri_valoroase.append({"tip": nume, "ev": ev, "miza": max(0.0, miza_recomandata)})
            
        return f"| **{nume}** | {prob*100:.1f}% | {cota:.2f} | :{culoare}[**{ev*100:+.2f}%**] | {status} |"

    st.subheader("⚽ Piețe Principale & Ambele Marchează (Meci Întreg)")
    st.markdown(f"""
| Tip Pronostic | Probabilitate Matematică | Cotă Agenție | Expected Value (EV) | Are Valoare? |
| :--- | :---: | :---: | :---: | :---: |
{analizeaza_optiune('Solist 1 (Gazde)', p1, c1)}
{analizeaza_optiune('Solist X (Egal)', px, cx)}
{analizeaza_optiune('Solist 2 (Oaspeți)', p2, c2)}
{analizeaza_optiune('Ambele marchează - DA (GG)', p_gg, c_gg)}
{analizeaza_optiune('Ambele marchează - NU (NG)', p_ng, c_ng)}
{analizeaza_optiune('Peste 1.5 Goluri', p_p15, c_p15)}
{analizeaza_optiune('Peste 2.5 Goluri', p_p25, c_p25)}
{analizeaza_optiune('Sub 2.5 Goluri', p_s25, c_s25)}
""")

    st.subheader("⏱️ Piețe Repriza 1")
    st.markdown(f"""
| Tip Pronostic (R1) | Probabilitate Matematică | Cotă Agenție | Expected Value (EV) | Are Valoare? |
| :--- | :---: | :---: | :---: | :---: |
{analizeaza_optiune('Repriza 1: Solist 1', pr1, cr1)}
{analizeaza_optiune('Repriza 1: Solist X', prx, crx)}
{analizeaza_optiune('Repriza 1: Solist 2', pr2, cr2)}
""")

    st.markdown("---")
    st.header("💵 Recomandări de Miză (Criteriul Kelly)")
    
    if len(pariuri_valoroase) == 0:
        st.warning("❌ Nu a fost detectat niciun pariu cu valoare.")
    else:
        st.success(f"🔥 S-au detectat {len(pariuri_valoroase)} opțiuni cu valoare matematică!")
        cols = st.columns(min(len(pariuri_valoroase), 3))
        for idx, pariu in enumerate(pariuri_valoroase):
            with cols[idx % min(len(pariuri_valoroase), 3)]:
                st.metric(label=f"🎯 {pariu['tip']}", value=f"{pariu['miza']:.2f} RON", delta=f"EV: +{pariu['ev']*100:.1f}%")