import time
import threading
import requests
import streamlit as st
from plyer import notification

# Introdu cheia ta gratuită de la API-Football / RapidAPI
API_KEY = "9b29c75b71a5a967808e8ec1e2f519d6"

def trimite_popup_desktop(titlu, mesaj):
    try:
        notification.notify(
            title=titlu,
            message=mesaj,
            app_name="Betting Live Alerts",
            timeout=10
        )
    except Exception as e:
        print(f"Eroare pop-up: {e}")

def cauta_scor_dupa_nume(nume_cautat):
    """ Caută automat meciul în toate meciurile LIVE ale zilei """
    if API_KEY and API_KEY != "CHEIA_TA_API_AICI":
        url = "https://v3.football.api-sports.io/fixtures?live=all"
        headers = {"x-apisports-key": API_KEY}
        try:
            res = requests.get(url, headers=headers, timeout=10).json()
            if res.get("response"):
                for meci in res["response"]:
                    gazda = meci["teams"]["home"]["name"]
                    oaspete = meci["teams"]["away"]["name"]
                    
                    # Dacă numele echipei se potrivește
                    if nume_cautat.lower() in gazda.lower() or nume_cautat.lower() in oaspete.lower():
                        return {
                            "meci": f"{gazda} vs {oaspete}",
                            "gazde": meci["goals"]["home"] or 0,
                            "oaspeti": meci["goals"]["away"] or 0
                        }
        except Exception as e:
            print(f"Eroare API: {e}")
    return None

def bucla_monitorizare(nume_echipa):
    scor_salvat = {"gazde": 0, "oaspeti": 0}
    
    while st.session_state.get("monitorizare_activa", False):
        meci_date = cauta_scor_dupa_nume(nume_echipa)
        
        if meci_date:
            if meci_date["gazde"] > scor_salvat["gazde"]:
                trimite_popup_desktop("⚽ GOL MARCAT!", f"{meci_date['meci']}\nScor nou: {meci_date['gazde']} - {meci_date['oaspeti']}")
                scor_salvat["gazde"] = meci_date["gazde"]
                
            elif meci_date["oaspeti"] > scor_salvat["oaspeti"]:
                trimite_popup_desktop("⚽ GOL MARCAT!", f"{meci_date['meci']}\nScor nou: {meci_date['gazde']} - {meci_date['oaspeti']}")
                scor_salvat["oaspeti"] = meci_date["oaspeti"]

        time.sleep(20) # Verifică la fiecare 20 secunde

def main():
    st.set_page_config(page_title="Live Alerts", page_icon="⚽")
    st.title("⚽ Alerte Pop-Up Scor Live")
    
    if "monitorizare_activa" not in st.session_state:
        st.session_state["monitorizare_activa"] = False

    echipa_cautata = st.text_input("Introdu numele echipei (ex: CSKA, Chertanovo, Dortmund):", "CSKA")

    if st.button("▶️ Pornește Monitorizarea"):
        st.session_state["monitorizare_activa"] = True
        t = threading.Thread(target=bucla_monitorizare, args=(echipa_cautata,), daemon=True)
        t.start()
        trimite_popup_desktop("🔔 Monitorizare Activă", f"Urmărești meciurile echipei: {echipa_cautata}")
        st.success(f"Monitorizezi meciul echipei: {echipa_cautata}")

    if st.button("⏹️ Oprește"):
        st.session_state["monitorizare_activa"] = False
        st.warning("Monitorizare oprită.")

if __name__ == "__main__":
    main()