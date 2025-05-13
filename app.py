import re
import math
import statistics
import streamlit as st

def analyze_text(text):
    """Analyze the given text and return calculated parameters."""
    if not text:
        return None

    text = text.replace('"', '')
    text = text.replace('„', '')
    text = text.replace('“', '')
    text = text.replace('”', '')

    text = text.replace(';', ',')
    text = text.replace(' -', ',')
    text = text.replace(' –', ',')

    text = text.replace('-', '')

    text = text.replace('. Januar', ' Januar')
    text = text.replace('. Februar', ' Februar')
    text = text.replace('. März', ' März')
    text = text.replace('. April', ' April')
    text = text.replace('. Mai', ' Mai')
    text = text.replace('. Juni', ' Juni')
    text = text.replace('. Juli', ' Juli')
    text = text.replace('. August', ' August')
    text = text.replace('. September', ' September')
    text = text.replace('. Oktober', ' Oktober')
    text = text.replace('. November', ' November')
    text = text.replace('. Dezember', ' Dezember')
    text = text.replace('. Jahrhundert', ' Jahrhundert')

    text = text.replace('z.B.', 'zB')
    text = text.replace('z. B.', 'zB')
    text = text.replace('d.h.', 'dh')
    text = text.replace('d. h.', 'dh')
    text = text.replace('u.a.', 'ua')
    text = text.replace('u. a.', 'ua')
    text = text.replace('i.d.R.', 'idR')
    text = text.replace('i. d. R.', 'idR')

    text = text.replace('ca.', 'ca')
    text = text.replace('bzw.', 'bzw')
    text = text.replace('etc.', 'etc')
    text = text.replace('usw.', 'usw')
    text = text.replace('ggf.', 'ggf')
    text = text.replace('vgl.', 'vgl')
    text = text.replace('Mio.', 'Mio')
    text = text.replace('Mrd.', 'Mrd')
    text = text.replace('bzgl.', 'bzgl')
    text = text.replace('evtl.', 'evtl')
    text = text.replace('Dr.', 'Dr')
    text = text.replace('Prof.', 'Prof')

    text = re.sub(r'(?<=\d),(?=\d)', '', text)
    text = re.sub(r'(?<=\d)\.(?=\d)', '', text)
    
    text = re.sub(r' {2,}', ' ', text)

    text = text.replace('!', '.')
    text = text.replace('?', '.')

    # Save cleaned text
    cleaned_text = text
    
    # Grundgrößen (Basic metrics)
    total_chars = len(text)
    total_chars_no_spaces = len(re.sub(r"\s+", "", text))
    total_letters = sum(1 for c in text if c.isalpha())
    words = re.findall(r"\b\w+\b", text)
    total_words = len(words)
    total_periods = text.count('.')
    total_commas = text.count(',')

    # Schätzer (Estimators)
    W = total_letters / total_words if total_words else 0
    SZ = total_letters / total_periods if total_periods else 0
    K = total_commas / total_periods if total_periods else 0

    # Prozent-Schätzer (Percentage estimators)
    substrings_lower = ('bar','lich','isch','haft','sam','voll','reich','los','arm')
    lower_words = [w for w in words if w.islower()]
    total_lower = len(lower_words)
    count_lower_sub = sum(1 for w in lower_words if any(sub in w for sub in substrings_lower))
    p_lower = (count_lower_sub / total_lower) if total_lower else 0
    P = p_lower * 100

    substrings_upper = ('tät','tion','igkeit','age','wert','logie','ktur','ktor','lung','tung','rung','zung')
    upper_words = [w for w in words if w and w[0].isupper()]
    total_upper = len(upper_words)
    count_upper_sub = sum(1 for w in upper_words if any(sub in w.lower() for sub in substrings_upper))
    p_upper = (count_upper_sub / total_upper) if total_upper else 0
    Q = p_upper * 100

    # Konfidenzintervalle (Confidence intervals)
    if total_words > 1:
        sd_w = statistics.stdev([sum(1 for c in w if c.isalpha()) for w in words])
        se_w = sd_w / math.sqrt(total_words)
        ci_w = (W - 1.96 * se_w, W + 1.96 * se_w)
    else:
        ci_w = (W, W)

    if total_periods > 1:
        segments = [s for s in text.split('.') if s]
        letters_per_sent = [sum(1 for c in s if c.isalpha()) for s in segments]
        sd_sz = statistics.stdev(letters_per_sent)
        se_sz = sd_sz / math.sqrt(total_periods)
        ci_sz = (SZ - 1.96 * se_sz, SZ + 1.96 * se_sz)

        sd_k = statistics.stdev([s.count(',') for s in segments])
        se_k = sd_k / math.sqrt(total_periods)
        ci_k = (K - 1.96 * se_k, K + 1.96 * se_k)
    else:
        ci_sz = (SZ, SZ)
        ci_k = (K, K)

    def conf_int_prop(p, n):
        if n > 0:
            se = math.sqrt(p * (1 - p) / n)
            low, high = p - 1.96 * se, p + 1.96 * se
            return max(0, low), min(1, high)
        return p, p

    ci_p = conf_int_prop(p_lower, total_lower)
    ci_q = conf_int_prop(p_upper, total_upper)

    # Implizite Level (Implicit levels)
    L1 = 6 * (1+math.tanh(0.76*W-4.72))
    L2 = 6 * (1+math.tanh(0.017*SZ-1.86))
    L3 = 6 * (1+math.tanh(K-1.36))
    L4 = 6 * (1+math.tanh(2.85*(P**0.25)-4.32))
    L5 = 6 * (1+math.tanh(1.38*(Q**0.25)-2.51))
    LT = (L1+L2+L3+L4+L5)/5

    return {
        'total_chars': total_chars,
        'total_chars_no_spaces': total_chars_no_spaces,
        'total_letters': total_letters,
        'total_words': total_words,
        'total_periods': total_periods,
        'total_commas': total_commas,
        'W': W,
        'SZ': SZ,
        'K': K,
        'P': P,
        'Q': Q,
        'ci_w': ci_w,
        'ci_sz': ci_sz,
        'ci_k': ci_k,
        'ci_p': ci_p,
        'ci_q': ci_q,
        'L1': L1,
        'L2': L2,
        'L3': L3,
        'L4': L4,
        'L5': L5,
        'LT': LT
    }

def format_results(results):
    """Format the analysis results for display."""
    if not results:
        return "Keine Ergebnisse verfügbar. Bitte geben Sie Text ein und klicken Sie auf 'Analysieren'."
    
    # Use monospace font for better alignment
    text = """```
"""
    
    # Basic metrics section
    text += f"{'Gesamtanzahl Zeichen im Text':<40}: {results['total_chars']:>10}\n"
    text += f"{'Gesamtanzahl Zeichen ohne Leerzeichen':<40}: {results['total_chars_no_spaces']:>10}\n"
    text += f"{'Gesamtanzahl Buchstaben im Text':<40}: {results['total_letters']:>10}\n"
    text += f"{'Gesamtanzahl Wörter im Text':<40}: {results['total_words']:>10}\n"
    text += f"{'Gesamtanzahl Punkte im Text':<40}: {results['total_periods']:>10}\n"
    text += f"{'Gesamtanzahl Kommas im Text':<40}: {results['total_commas']:>10}\n"
    text += "\n"
    
    # Statistical metrics with confidence intervals
    text += f"{'Buchstaben/Wörter (W)':<40}: {results['W']:>10.4f}    95% CI: [{results['ci_w'][0]:.4f}, {results['ci_w'][1]:.4f}]\n"
    text += f"{'Buchstaben/Punkte (SZ)':<40}: {results['SZ']:>10.4f}    95% CI: [{results['ci_sz'][0]:.4f}, {results['ci_sz'][1]:.4f}]\n"
    text += f"{'Kommas/Punkte (K)':<40}: {results['K']:>10.4f}    95% CI: [{results['ci_k'][0]:.4f}, {results['ci_k'][1]:.4f}]\n"
    text += f"{'Kleinwörter mit adj. Strings (P)':<40}: {results['P']:>10.4f}    95% CI: [{100*results['ci_p'][0]:.4f}, {100*results['ci_p'][1]:.4f}]\n"
    text += f"{'Großwörter mit akad. Strings (Q)':<40}: {results['Q']:>10.4f}    95% CI: [{100*results['ci_q'][0]:.4f}, {100*results['ci_q'][1]:.4f}]\n"
    text += "\n"
    
    # Implicit levels
    text += f"{'Implizites Level L1 (Wörter)':<40}: {results['L1']:>10.2f}\n"
    text += f"{'Implizites Level L2 (Sätze)':<40}: {results['L2']:>10.2f}\n"
    text += f"{'Implizites Level L3 (Kommas)':<40}: {results['L3']:>10.2f}\n"
    text += f"{'Implizites Level L4 (Adjektive)':<40}: {results['L4']:>10.2f}\n"
    text += f"{'Implizites Level L5 (Akademisch)':<40}: {results['L5']:>10.2f}\n"
    text += "\n"
    text += f"{'Implizites Level L (Mittelwert)':<40}: {results['LT']:>10.2f}\n"
    text += "```"
    
    return text

def main():
    """Main application function."""
    st.set_page_config(
        page_title="Textparameter-Analyse",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    st.title("Textparameter-Analyse")
    
    # Session-State initialisieren, falls noch nicht gesetzt
    if "text_input" not in st.session_state:
    st.session_state["text_input"] = ""

    # Text input area
    st.subheader("Text eingeben:")
    text_input = st.text_area("", height=300, key="text_input")
    
    # Analyze button
    if st.button("Analysieren"):
        if st.session_state["text_input"].strip():
            with st.spinner("Analysiere Text..."):
                results = analyze_text(st.session_state["text_input"])
            # Update the input box to show the cleaned text
            st.session_state["text_input"] = results.get("cleaned_text", st.session_state["text_input"])
            # Display results
            st.subheader("Ergebnisse:")
            st.markdown(format_results(results))
        else:
            st.error("Bitte geben Sie einen Text ein.")
    
    # Display help information in an expandable section
    with st.expander("Informationen zur Textparameter-Analyse"):
        st.markdown("""
        ### Über diese Anwendung
        
        Diese Anwendung analysiert einen gegebenen Text und berechnet verschiedene linguistische Parameter:
        
        * Grundlegende Metriken: Zeichen, Wörter, Satzzeichen
        * Komplexitätsmetriken: Wort- und Satzlänge, Kommasetzung
        * Linguistische Level: Bewertung der Sprachkomplexität

        (Der Text wird automatisch für die Analyse formatiert)
        
        ### Berechnete Parameter
        
        * W: Durchschnittliche Buchstaben pro Wort
        * SZ: Durchschnittliche Buchstaben pro Satz
        * K: Verhältnis von Kommas zu Punkten
        * P: Prozentsatz von Kleinwörtern mit adjektivischen Endungen
        * Q: Prozentsatz von Großwörtern mit akademischen Endungen
        * L1-L5: Implizite Sprachniveaus für verschiedene Aspekte
        * LT: Durchschnittliches Sprachniveau
        
        Die Konfidenzintervalle (95% CI) geben die statistische Sicherheit der Messungen an.
        """)

if __name__ == "__main__":
    main()
