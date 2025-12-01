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
Jesteś ekspertem w tworzeniu promptów dla modeli text-to-image. Twoim zadaniem jest analiza poniższego akapitu napisanego w języku polskim i stworzenie na jego podstawie zwięzłego, angielskiego promptu, który posłuży do wygenerowania grafiki.

Przestrzegaj bezwzględnie następujących zasad zgodnych ze standardem ETR (Easy to Read):
1.  **DOSŁOWNOŚĆ:** Prompt musi opisywać dokładnie to, co jest w tekście. Unikaj metafor, symboli i abstrakcji.
2.  **PROSTOTA:** Skup się na jednej, głównej scenie lub czynności. Opis powinien zawierać minimalną liczbę postaci i obiektów - tylko te kluczowe. Tło ma być proste i nie odwracać uwagi.
3.  **REALIZM:** Styl grafiki musi być fotorealistyczny. Twój prompt powinien to sugerować (np. używając słów "photorealistic", "a photo of...").
4.  **JEDNOZNACZNOŚĆ:** Postacie i obiekty muszą być typowe i łatwo rozpoznawalne.
5.  **KONTEKST KULTUROWY:** Scena powinna być osadzona we współczesnym polskim kontekście. Dodawaj subtelne wskazówki, np. "in Poland", "at a Polish train station", "typical Polish multi-story apartment block", jeśli pasuje to do kontekstu.
6.  **FORMAT:** Zwróć TYLKO I WYŁĄCZNIE sam prompt w języku angielskim. Żadnych dodatkowych zdań, nagłówków czy wyjaśnień.

Przykład:
Tekst wejściowy: "Mężczyzna wchodzi do autobusu. Kasuje bilet w żółtym kasowniku."
Twój prompt: A photorealistic image of a man getting on a bus in Poland, putting a ticket into a yellow ticket validator machine. Simple background.
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
    temperature = st.slider(
        "Temperatura (kreatywność):",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.05
    )
    style = st.selectbox(
        "Styl grafiki:",
        ("Fotograficzny", "Rysunkowy", "Komiksowy")
    )

# --- Logika aplikacji ---

def generate_image_prompt(text: str, system_prompt: str, style: str) -> str:
    """
    Analizuje tekst użytkownika i generuje na jego podstawie prompt do generatora obrazów,
    zgodnie z wytycznymi ETR i wybranym stylem.
    """
    style_instruction = {
        "Fotograficzny": 'Styl grafiki musi być fotorealistyczny. Twój prompt powinien to sugerować (np. używając słów "photorealistic", "a photo of...").',
        "Rysunkowy": 'Styl grafiki musi być prostym, wyraźnym rysunkiem (line art). Twój prompt powinien to sugerować (np. używając słów "simple line drawing", "clear line art of...").',
        "Komiksowy": 'Styl grafiki musi być prostym, kolorowym stylem komiksowym. Twój prompt powinien to sugerować (np. używając słów "simple comic book style illustration of...").'
    }

    # Zastąp domyślną instrukcję stylu w prompcie systemowym
    final_system_prompt = system_prompt.replace(
        'Styl grafiki musi być fotorealistyczny. Twój prompt powinien to sugerować (np. używając słów "photorealistic", "a photo of...").',
        style_instruction.get(style, style_instruction["Fotograficzny"])
    )

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[final_system_prompt, f"Tekst wejściowy: \"{text}\""],
            config=types.GenerateContentConfig(temperature=0.7)
        )
        
        # Pobierz tekst z odpowiedzi
        if response.text:
            image_prompt = response.text.strip().replace("*", "")
            if image_prompt:
                return image_prompt
        
        # Fallback
        st.warning("⚠️ Model zwrócił pustą odpowiedź. Próbuję z uproszczonym promptem...")
        fallback_prompt = f"Create a simple English description for an illustration based on this Polish text: {text}. Description should be one sentence."
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=fallback_prompt,
            config=types.GenerateContentConfig(temperature=0.5)
        )
        
        if response.text:
            return response.text.strip()
        
        st.error("❌ Nie udało się uzyskać odpowiedzi od modelu.")
        return None
        
    except Exception as e:
        st.error(f"❌ Błąd API Gemini: {str(e)}")
        st.info("💡 Wskazówki:\n- Upewnij się, że klucz API jest ważny\n- Model może być niedostępny w Twojej lokalizacji\n- Spróbuj zmienić tekst na krótszy")
        return None



def generate_image(prompt: str, temperature: float) -> bytes:
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
                temperature=temperature
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
            "style": [st.session_state.used_style],
            "temperature": [st.session_state.used_temperature],
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
            'image_data', 'image_prompt', 'input_text', 
            'used_system_prompt', 'used_style', 'used_temperature'
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
            image_prompt = generate_image_prompt(input_text, custom_system_prompt, style)
        
        if image_prompt:
            st.session_state.image_prompt = image_prompt
            st.session_state.input_text = input_text
            st.session_state.used_system_prompt = custom_system_prompt
            st.session_state.used_style = style
            st.session_state.used_temperature = temperature
            
            with st.spinner("Tworzę grafikę..."):
                image_data = generate_image(image_prompt, temperature)
            
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
        st.write(f"**Użyte parametry:** Styl: `{st.session_state.used_style}`, Temperatura: `{st.session_state.used_temperature}`")
        
        with st.expander("Pokaż prompt użyty do wygenerowania grafiki"):
            st.code(st.session_state.image_prompt, language="text")

        with st.expander("Pokaż prompt systemowy użyty do analizy tekstu"):
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




