import re
import math
import statistics
import streamlit as st


def clean_text(text):
    """Clean the given text according to predefined rules."""
    if not text:
        return text

    # Remove various quotation marks
    text = text.replace('"', '')
    text = text.replace('„', '')
    text = text.replace('“', '')
    text = text.replace('”', '')

    # Normalize punctuation
    text = text.replace(';', ',')
    text = text.replace(' -', ',')
    text = text.replace(' –', ',')
    text = text.replace('-', '')

    # Fix month and century formatting
    months = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
    for m in months + ['Jahrhundert']:
        text = text.replace(f'. {m}', f' {m}')

    # Abbreviations
    abbrev = ['z.B.', 'z. B.', 'd.h.', 'd. h.', 'u.a.', 'u. a.', 'i.d.R.', 'i. d. R.', 'ca.', 'bzw.', 'etc.', 'usw.', 'ggf.', 'vgl.', 'Mio.', 'Mrd.', 'bzgl.', 'evtl.', 'Dr.', 'Prof.']
    repl = ['zB', 'zB', 'dh', 'dh', 'ua', 'ua', 'idR', 'idR', 'ca', 'bzw', 'etc', 'usw', 'ggf', 'vgl', 'Mio', 'Mrd', 'bzgl', 'evtl', 'Dr', 'Prof']
    for a, r in zip(abbrev, repl):
        text = text.replace(a, r)

    # Numeric punctuation
    text = re.sub(r'(?<=\d),(?=\d)', '', text)
    text = re.sub(r'(?<=\d)\.(?=\d)', '', text)

    # Collapse multiple spaces
    text = re.sub(r' {2,}', ' ', text)

    # Sentence endings
    text = text.replace('!', '.')
    text = text.replace('?', '.')

    return text


def analyze_text(text):
    """Analyze the given text and return calculated parameters along with cleaned text."""
    if not text:
        return None

    cleaned = clean_text(text)

    # Basic metrics
    total_chars = len(cleaned)
    total_chars_no_spaces = len(re.sub(r"\s+", "", cleaned))
    total_letters = sum(1 for c in cleaned if c.isalpha())
    words = re.findall(r"\b\w+\b", cleaned)
    total_words = len(words)
    total_periods = cleaned.count('.')
    total_commas = cleaned.count(',')

    # Estimators
    W = total_letters / total_words if total_words else 0
    SZ = total_letters / total_periods if total_periods else 0
    K = total_commas / total_periods if total_periods else 0

    # Percentage estimators
    substrings_lower = ('bar', 'lich', 'isch', 'haft', 'sam', 'voll', 'reich', 'los', 'arm')
    lower_words = [w for w in words if w.islower()]
    total_lower = len(lower_words)
    count_lower_sub = sum(1 for w in lower_words if any(sub in w for sub in substrings_lower))
    p_lower = (count_lower_sub / total_lower) if total_lower else 0
    P = p_lower * 100

    substrings_upper = ('tät', 'tion', 'igkeit', 'age', 'wert', 'logie', 'ktur', 'ktor', 'lung', 'tung', 'rung', 'zung')
    upper_words = [w for w in words if w and w[0].isupper()]
    total_upper = len(upper_words)
    count_upper_sub = sum(1 for w in upper_words if any(sub in w.lower() for sub in substrings_upper))
    p_upper = (count_upper_sub / total_upper) if total_upper else 0
    Q = p_upper * 100

    # Confidence intervals
    def conf_prop(p, n):
        if n > 0:
            se = math.sqrt(p * (1 - p) / n)
            low, high = p - 1.96 * se, p + 1.96 * se
            return max(0, low), min(1, high)
        return p, p

    # Word-length CI
    if total_words > 1:
        lengths = [sum(1 for c in w if c.isalpha()) for w in words]
        sd_w = statistics.stdev(lengths)
        se_w = sd_w / math.sqrt(total_words)
        ci_w = (W - 1.96 * se_w, W + 1.96 * se_w)
    else:
        ci_w = (W, W)

    # Sentence-length and comma CI
    if total_periods > 1:
        segments = [s for s in cleaned.split('.') if s]
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

    ci_p = conf_prop(p_lower, total_lower)
    ci_q = conf_prop(p_upper, total_upper)

    # Implicit levels
    L1 = 6 * (1 + math.tanh(0.76 * W - 4.72))
    L2 = 6 * (1 + math.tanh(0.017 * SZ - 1.86))
    L3 = 6 * (1 + math.tanh(K - 1.36))
    L4 = 6 * (1 + math.tanh(2.85 * (P**0.25) - 4.32))
    L5 = 6 * (1 + math.tanh(1.38 * (Q**0.25) - 2.51))
    LT = (L1 + L2 + L3 + L4 + L5) / 5

    return {
        'cleaned_text': cleaned,
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
    text = "```"
    text += f"\n{'Gesamtanzahl Zeichen':<40}: {results['total_chars']:<10}\n"
    text += f"{'Zeichen ohne Leerzeichen':<40}: {results['total_chars_no_spaces']:<10}\n"
    text += f"{'Gesamtanzahl Buchstaben':<40}: {results['total_letters']:<10}\n"
    text += f"{'Wörter insgesamt':<40}: {results['total_words']:<10}\n"
    text += f"{'Punkte insgesamt':<40}: {results['total_periods']:<10}\n"
    text += f"{'Kommas insgesamt':<40}: {results['total_commas']:<10}\n"
    text += "\n"
    text += f"{'Anzahl Buchstaben pro Wort (W)':<40}: {results['W']:<10.4f} 95% CI [{results['ci_w'][0]:.4f}, {results['ci_w'][1]:.4f}]\n"
    text += f"{'Anzahl Buchstaben pro Satz (SZ)':<40}: {results['SZ']:<10.4f} 95% CI [{results['ci_sz'][0]:.4f}, {results['ci_sz'][1]:.4f}]\n"
    text += f"{'Anzahl Kommas pro Satz (K)':<40}: {results['K']:<10.4f} 95% CI [{results['ci_k'][0]:.4f}, {results['ci_k'][1]:.4f}]\n"
    text += f"{'Kleinwörter mit adj. Strings (P)':<40}: {results['P']:<10.4f} 95% CI [{100*results['ci_p'][0]:.2f}%, {100*results['ci_p'][1]:.2f}%]\n"
    text += f"{'Großwörter mit akad. Strings (Q)':<40}: {results['Q']:<10.4f} 95% CI [{100*results['ci_q'][0]:.2f}%, {100*results['ci_q'][1]:.2f}%]\n"
    text += "\n"
    text += f"{'Implizites Level L1 aus W':<40}: {results['L1']:<6.2f}\n"
    text += f"{'Implizites Level L2 aus SZ':<40}: {results['L2']:<6.2f}\n"
    text += f"{'Implizites Level L3 aus K':<40}: {results['L3']:<6.2f}\n"
    text += f"{'Implizites Level L4 aus P':<40}: {results['L4']:<6.2f}\n"
    text += f"{'Implizites Level L5 aus Q':<40}: {results['L5']:<6.2f}\n"
    text += f"\n{'Durchschnittliches Sprachniveau (L)':<40}: {results['LT']:<6.2f}\n"
    text += "```"
    return text


def main():
    st.set_page_config(page_title="Textparameter-Analyse", layout="wide")
    st.title("Textparameter-Analyse")

    # Initialize session state for text and results
    if 'text_input' not in st.session_state:
        st.session_state['text_input'] = ''
    if 'analysis' not in st.session_state:
        st.session_state['analysis'] = None

    # Callback functions
    def on_clean():
        st.session_state['text_input'] = clean_text(st.session_state['text_input'])
        st.session_state['analysis'] = None  # reset previous analysis

    def on_analyze():
        st.session_state['analysis'] = analyze_text(st.session_state['text_input'])

    # Text area
    st.text_area("", value=st.session_state['text_input'], height=300, key='text_input')

    # Buttons with callbacks
    cols = st.columns(2)
    with cols[0]:
        st.button("Bereinigen", on_click=on_clean)
    with cols[1]:
        st.button("Analysieren", on_click=on_analyze)

    # Display cleaned text and results
    if st.session_state['analysis'] is not None:
        st.subheader("Ergebnisse:")
        st.markdown(format_results(st.session_state['analysis']))

if __name__ == "__main__":
    main()
