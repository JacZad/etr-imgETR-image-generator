import os
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import io
from PIL import Image

# --- Konfiguracja ---
# Klucz API będzie załadowany najpierw ze zmiennych środowiskowych, potem z .env


# --- Stałe ---
DEFAULT_SYSTEM_PROMPT = """
Jesteś ekspertem w tworzeniu promptów dla modeli text-to-image dla materiałów ETR (Easy to Read) - tekstów dla osób z niepełnosprawnością intelektualną.

═══════════════════════════════════════════════════════════════════
PROCES ANALIZY (myśl krok po kroku, pokaż swoje rozumowanie):

KROK 1 - IDENTYFIKACJA:
• Kto/co jest głównym tematem?
• Jakie emocje występują (jeśli są)?
• Jaki jest kontekst miejsca/sytuacji?

KROK 2 - UPROSZCZENIE:
• Ogranicz scenę do 1-2 kluczowych elementów
• Usuń szczegóły drugorzędne
• Zachowaj tylko to, co niezbędne do zrozumienia

KROK 3 - WIZUALIZACJA ETR:
Zastosuj zasady:

1. DOSŁOWNOŚĆ: Opisuj dokładnie to, co w tekście - bez artystycznych metafor
2. PROSTOTA: Jedna scena, 1-2 obiekty/osoby, proste tło
3. REALIZM: Styl fotorealistyczny ("photorealistic photo of...")
4. JEDNOZNACZNOŚĆ: Typowe, łatwo rozpoznawalne obiekty i postacie
5. KONTEKST POLSKI: Dodaj subtelne wskazówki kontekstu (jeśli pasuje):
   "in Poland", "Polish apartment", "Polish street sign"

6. EMOCJE - dwa podejścia:
   A) Gdy tekst opisuje OSOBĘ z emocją → mimika twarzy + język ciała
      • Radość: uśmiech, podniesione brwi
      • Smutek: opuszczone kąciki ust, pochylona głowa
      • Złość: zmarszczone brwi, zaciśnięte pięści
   
   B) Gdy tekst opisuje ABSTRAKCYJNĄ emocję (bez osoby) → prosty, typowy obiekt
      • "Ból w szpitalu" → strzykawka na stole
      • "Wstręt do brudu" → brudna skarpetka
      (UWAGA: używaj najprostszych symboli, unikaj artystycznych metafor)

7. KONTAKT WZROKOWY: Jeśli są 2+ osoby → powinny na siebie patrzeć
8. BEZ TEKSTU: Unikaj napisów na znakach, koszulkach, książkach
   (wyjątek: tekst kluczowy dla zrozumienia sceny)
9. KOLORY: Ograniczona paleta, neutralne/stonowane barwy
10. TŁO: Jednolite lub delikatny gradient, nie odwraca uwagi

KROK 4 - WYGENERUJ PROMPT:
Format: "A photorealistic photo of [główny temat] [czynność/stan] [gdzie]. [Szczegóły mimiki/emocji jeśli są]. Simple [kolor] background, soft neutral lighting."

═══════════════════════════════════════════════════════════════════
PRZYKŁADY (ucz się z nich):

PRZYKŁAD 1:
Tekst wejściowy: "Mężczyzna wchodzi do autobusu. Kasuje bilet w żółtym kasowniku."

[Analiza]
KROK 1: Mężczyzna + autobus + kasownik
KROK 2: Główna scena - wejście do autobusu z biletem
KROK 3: Fotorealizm, polski kontekst (żółty kasownik typowy dla PL), proste wnętrze
KROK 4: ↓

Prompt: "A photorealistic photo of a middle-aged man stepping onto a city bus in Poland, holding a paper ticket near a yellow ticket validator machine. Simple gray bus interior background, neutral daylight."

---

PRZYKŁAD 2:
Tekst wejściowy: "Kobieta czuje smutek po utracie pracy. Siedzi samotnie w pustym biurze."

[Analiza]
KROK 1: Kobieta + emocja (smutek) + kontekst (biuro, utrata pracy)
KROK 2: Główna scena - kobieta siedząca, puste biurko (symbol utraty)
KROK 3: Emocja przez mimikę (zasada 6A), proste biuro, stonowane kolory
KROK 4: ↓

Prompt: "A photorealistic portrait of a woman in her 30s sitting at an empty office desk, with a sad facial expression - downturned mouth corners and lowered head. She holds an unopened envelope. Simple beige office background with soft lighting, muted blue-gray tones."

---

PRZYKŁAD 3:
Tekst wejściowy: "Ludzie boją się szczepionki. Strach przed igłą."

[Analiza]
KROK 1: Emocja (strach) + obiekt (igła/szczepionka) - brak konkretnej osoby
KROK 2: Abstrakcyjna emocja → użyj obiektu wywołującego strach (zasada 6B)
KROK 3: Prosty symbol - strzykawka w zbliżeniu, sterylne tło medyczne
KROK 4: ↓

Prompt: "A photorealistic close-up photo of a medical syringe with a needle on a white sterile table in a clinical setting. Simple white background with soft overhead lighting, cool color temperature."

═══════════════════════════════════════════════════════════════════

Teraz przeanalizuj poniższy tekst według powyższych kroków. Pokaż swoje rozumowanie (KROK 1-3), a następnie wygeneruj końcowy prompt (KROK 4):
"""


# --- Panel boczny ---
with st.sidebar:
    st.title("Ustawienia")
    
    # Konfiguracja klucza API Gemini
    # Najpierw sprawdź zmienne środowiskowe systemowe, potem .env
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            # Jeśli nie ma w środowisku, załaduj z .env
            load_dotenv()
            api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError("Brak klucza API")
        
        client = genai.Client(api_key=api_key)
        st.success("Klucz API Gemini załadowany.")
    except (ValueError, Exception) as e:
        st.error("⚠️ Brak klucza API Gemini!")
        st.info("Ustaw zmienną środowiskową `GEMINI_API_KEY` lub utwórz plik `.env` z zawartością: `GEMINI_API_KEY=your_key_here`")
        st.stop()
    
    st.header("Konfiguracja promptu systemowego")
    custom_system_prompt = st.text_area(
        "Edytuj prompt systemowy dla modelu językowego:",
        value=DEFAULT_SYSTEM_PROMPT,
        height=400
    )

    st.header("Parametry generowania")
    
    with st.expander("⚙️ Ustawienia zaawansowane", expanded=True):
        st.markdown("**Temperatura analizy tekstu**")
        st.caption("Kontroluje kreatywność interpretacji tekstu i tworzenia promptu (Gemini 2.5 Flash)")
        text_temperature = st.slider(
            "Analiza tekstu:",
            min_value=0.0,
            max_value=1.0,
            value=0.6,
            step=0.05,
            key="text_temp",
            label_visibility="collapsed"
        )
        
        st.markdown("**Temperatura generowania obrazu**")
        st.caption("Kontroluje różnorodność wizualną obrazu (Gemini 2.5 Flash Image)")
        image_temperature = st.slider(
            "Generowanie obrazu:",
            min_value=0.0,
            max_value=1.0,
            value=0.4,
            step=0.05,
            key="image_temp",
            label_visibility="collapsed"
        )

# --- Logika aplikacji ---

def generate_image_prompt(text: str, system_prompt: str, text_temp: float) -> tuple:
    """
    Analizuje tekst użytkownika i generuje na jego podstawie prompt do generatora obrazów,
    zgodnie z wytycznymi ETR.
    
    Returns:
        tuple: (final_prompt, full_reasoning) - końcowy prompt i pełne rozumowanie modelu
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[system_prompt, f"Tekst wejściowy: \"{text}\""],
            config=types.GenerateContentConfig(temperature=text_temp)
        )
        
        # Pobierz pełną odpowiedź z rozumowaniem
        if response.text:
            full_response = response.text.strip()
            
            # Spróbuj wyodrębnić końcowy prompt (po "KROK 4" lub "Prompt:")
            lines = full_response.split('\n')
            final_prompt = ""
            reasoning = ""
            
            # Szukaj ostatniego "Prompt:" w odpowiedzi
            for i, line in enumerate(lines):
                if 'Prompt:' in line or 'prompt:' in line.lower():
                    # Wszystko przed tym linijką to reasoning
                    reasoning = '\n'.join(lines[:i]).strip()
                    # Prompt zaczyna się od tej linii
                    final_prompt = '\n'.join(lines[i:]).replace('Prompt:', '').replace('prompt:', '').strip()
                    break
            
            # Jeśli nie znaleziono struktury, użyj całej odpowiedzi jako prompt
            if not final_prompt:
                final_prompt = full_response
                reasoning = "[Brak szczegółowego rozumowania]"
            
            # Wyczyść formatowanie markdown
            final_prompt = final_prompt.replace("*", "").replace("```", "").strip()
            
            if final_prompt:
                return final_prompt, reasoning
        
        # Fallback z zachowaniem wytycznych ETR
        st.warning("⚠️ Model zwrócił pustą odpowiedź. Próbuję z uproszczonym promptem...")
        fallback_prompt = f"""Based on this Polish text: "{text}"
        
Create ONE photorealistic scene description in English.
Rules: simple background, 1-2 subjects maximum, neutral colors, no text on objects.
Format: "A photorealistic photo of [subject] [action] [where]. Simple [color] background."""
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=fallback_prompt,
            config=types.GenerateContentConfig(temperature=0.5)
        )
        
        if response.text:
            return response.text.strip(), "[Fallback - uproszczony prompt]"
        
        st.error("❌ Nie udało się uzyskać odpowiedzi od modelu.")
        return None, None
        
    except Exception as e:
        st.error(f"❌ Błąd API Gemini: {str(e)}")
        st.info("💡 Wskazówki:\n- Upewnij się, że klucz API jest ważny\n- Model może być niedostępny w Twojej lokalizacji\n- Spróbuj zmienić tekst na krótszy")
        return None



def generate_image(prompt: str, image_temp: float) -> bytes:
    """
    Generuje obraz na podstawie podanego promptu za pomocą gemini-2.5-flash-image.
    Zwraca dane obrazu w formacie bytes.
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-image',
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE'],
                temperature=image_temp
            )
        )
        
        # Pobierz obraz z odpowiedzi
        for part in response.parts:
            if part.inline_data is not None:
                return part.inline_data.data
        
        st.error("❌ Model nie zwrócił obrazu.")
        return None
            
    except Exception as e:
        st.error(f"❌ Błąd podczas generowania obrazu: {e}")
        st.info("💡 Upewnij się, że masz dostęp do modelu 'gemini-2.5-flash-image'.")
        return None


def save_feedback(rating: str, comments: str):
    """
    Zapisuje obraz na dysku oraz dodaje wpis do pliku CSV z metadanymi.
    """
    try:
        # 1. Przygotuj unikalną nazwę pliku
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"etr_image_{timestamp}.png"
        image_path = os.path.join("generated_images", image_filename)

        # 2. Zapisz obraz na dysku
        with open(image_path, "wb") as f:
            f.write(st.session_state.image_data)

        # 3. Przygotuj dane do zapisu w CSV
        feedback_data = {
            "timestamp": [timestamp],
            "original_text": [st.session_state.input_text],
            "used_system_prompt": [st.session_state.used_system_prompt],
            "text_temperature": [st.session_state.text_temperature],
            "image_temperature": [st.session_state.image_temperature],
            "reasoning": [st.session_state.get('reasoning', '')],
            "generated_prompt": [st.session_state.image_prompt],
            "image_filename": [image_filename],
            "rating": [rating],
            "comments": [comments]
        }
        df = pd.DataFrame(feedback_data)

        # 4. Zapisz/dopisz do pliku CSV
        csv_path = "feedback.csv"
        if not os.path.exists(csv_path):
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        else:
            df.to_csv(csv_path, mode='a', header=False, index=False, encoding='utf-8-sig')
        
        st.success(f"Dziękujemy! Twoja ocena została zapisana. Obraz: {image_filename}")
        
        # Wyczyść stan sesji po zapisaniu
        keys_to_clear = [
            'image_data', 'image_prompt', 'reasoning', 'input_text', 
            'used_system_prompt', 'text_temperature', 'image_temperature'
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
    except Exception as e:
        st.error(f"Wystąpił błąd podczas zapisywania oceny: {e}")


st.title("Generator grafik do tekstu ETR")




st.subheader("1. Wklej tekst do analizy")
input_text = st.text_area("Akapit tekstu ETR", height=150, label_visibility="collapsed")

if st.button("Generuj grafikę"):
    if input_text:
        with st.spinner("Analizuję tekst i generuję prompt..."):
            result = generate_image_prompt(input_text, custom_system_prompt, text_temperature)
        
        if result and result[0]:
            image_prompt, reasoning = result
            st.session_state.image_prompt = image_prompt
            st.session_state.reasoning = reasoning
            st.session_state.input_text = input_text
            st.session_state.used_system_prompt = custom_system_prompt
            st.session_state.text_temperature = text_temperature
            st.session_state.image_temperature = image_temperature
            
            with st.spinner("Tworzę grafikę..."):
                image_data = generate_image(image_prompt, image_temperature)
            
            if image_data:
                st.session_state.image_data = image_data
                st.rerun()
            else:
                st.error("Nie udało się wygenerować grafiki.")
        else:
            st.error("Nie udało się wygenerować promptu dla grafiki.")
    else:
        st.warning("Proszę wkleić tekst.")

# Wyświetlanie wyników i formularza feedbacku, jeśli istnieją w stanie sesji
if 'image_data' in st.session_state and 'image_prompt' in st.session_state:
    with st.container(border=True):
        st.subheader("2. Wynik")
        st.image(st.session_state.image_data, caption="Wygenerowana grafika", width='stretch')

    with st.container(border=True):
        st.subheader("3. Szczegóły procesu")
        st.write(f"**Użyte parametry:**")
        st.write(f"- Temperatura analizy tekstu: `{st.session_state.text_temperature}`")
        st.write(f"- Temperatura generowania obrazu: `{st.session_state.image_temperature}`")
        
        with st.expander("📋 Pokaż proces analizy (Chain-of-Thought)"):
            st.markdown("**Rozumowanie modelu (KROK 1-3):**")
            st.text(st.session_state.get('reasoning', '[Brak danych o rozumowaniu]'))
        
        with st.expander("🎨 Pokaż końcowy prompt użyty do wygenerowania grafiki"):
            st.code(st.session_state.image_prompt, language="text")

        with st.expander("⚙️ Pokaż pełny prompt systemowy"):
            st.code(st.session_state.used_system_prompt, language="text")

    # Placeholder for feedback form
    with st.container(border=True):
        st.subheader("4. Zapisz ocenę")
        comments = st.text_area("Dodatkowe uwagi (opcjonalnie):", key="feedback_comments")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("👍 Dobrze", width='stretch'):
                save_feedback(rating="Dobrze", comments=comments)
                st.rerun()

        with col2:
            if st.button("👎 Źle", width='stretch'):
                save_feedback(rating="Źle", comments=comments)
                st.rerun()




