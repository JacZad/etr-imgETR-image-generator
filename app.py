import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import io
from PIL import Image, ImageDraw, ImageFont

# --- Konfiguracja ---
# Ładowanie zmiennych środowiskowych z pliku .env
load_dotenv()


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
    try:
        api_key = os.environ["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        st.success("Klucz API Gemini załadowany.")
    except KeyError:
        st.error("⚠️ Brak klucza API Gemini!")
        st.info("Utwórz plik `.env` z zawartością: `GEMINI_API_KEY=your_key_here`")
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
        value=0.0, # Domyślnie 0, zgodnie z wymaganiami
        step=0.05
    )
    style = st.selectbox(
        "Styl grafiki:",
        ("Fotograficzny", "Rysunkowy", "Komiksowy")
    )
    
    st.header("Tryb generowania")
    generation_mode = st.radio(
        "Wybierz tryb generowania:",
        ("Wariant A: Images API (eksperymentalny)", "Wariant B: Generuj jako tekst + obraz placeholder"),
        help="Wariant A: Próbuje użyć Google Images API (może wymagać dodatkowych uprawnień)\nWariant B: Generuje opis tekstowy i placeholder grafiki"
    )


# Inicjalizacja modeli
text_model = genai.GenerativeModel('gemini-2.5-flash')
# Wariant A: Próba użycia Images API (jeśli dostępne)
try:
    image_model = genai.GenerativeModel('gemini-1.5-pro')  # Alternatywa: model z obsługą obrazów
except:
    image_model = None

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
        response = text_model.generate_content(
            [final_system_prompt, f"Tekst wejściowy: \"{text}\""],
            generation_config=genai.GenerationConfig(temperature=0.7)  # Zwiększona temperatura dla lepszej odpowiedzi
        )
        
        # Bezpieczna obsługa odpowiedzi
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if candidate.content and candidate.content.parts:
                # Pobierz tekst z pierwszego part
                for part in candidate.content.parts:
                    if hasattr(part, 'text') and part.text:
                        image_prompt = part.text.strip().replace("*", "")
                        if image_prompt:  # Sprawdź czy nie jest puste
                            return image_prompt
        
        # Fallback: jeśli model zwrócił pustą odpowiedź, spróbuj z uproszczonym promptem
        st.warning("⚠️ Model zwrócił pustą odpowiedź. Próbuję z uproszczonym promptem...")
        fallback_prompt = f"Create a simple English description for an illustration based on this Polish text: {text}. Description should be one sentence."
        
        response = text_model.generate_content(
            fallback_prompt,
            generation_config=genai.GenerationConfig(temperature=0.5)
        )
        
        if response.candidates and len(response.candidates) > 0:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'text') and part.text:
                    return part.text.strip()
        
        st.error("❌ Nie udało się uzyskać odpowiedzi od modelu.")
        return None
        
    except Exception as e:
        st.error(f"❌ Błąd API Gemini: {str(e)}")
        st.info("💡 Wskazówki:\n- Upewnij się, że klucz API jest ważny\n- Model może być niedostępny w Twojej lokalizacji\n- Spróbuj zmienić tekst na krótszy\n- Czekaj chwilę i spróbuj ponownie")
        return None



def generate_image_variant_a(prompt: str, temperature: float) -> bytes:
    """
    WARIANT A: Próbuje wygenerować obraz za pomocą dostępnych API.
    W aktualnej wersji Gemini API brak dedykowanego modelu do generacji obrazów,
    dlatego ta funkcja zwraca None i kieruje do wariantu B.
    
    Przyszłe: jeśli Google udostępni Images API, tutaj będzie właściwa implementacja.
    """
    try:
        # Google Images API nie jest jeszcze dostępne w python SDK
        # Ta funkcja jest zarezerwowana na przyszłość
        st.warning("⚠️ Wariant A (Images API) nie jest jeszcze dostępny w SDK.")
        return None
    except Exception as e:
        st.error(f"Błąd Wariantu A: {e}")
        return None


def generate_image_variant_b(prompt: str, original_text: str, style: str, temperature: float) -> bytes:
    """
    WARIANT B: Generuje prosty obraz placeholder z tekstem opisu.
    Służy jako alternatywa do generacji przez Images API.
    
    W przyszłości ten obraz można zastąpić prawdziwą grafiką ze zintegrowanej usługi.
    """
    try:
        # Utwórz obraz placeholder w rozdzielczości 1024x1024
        width, height = 1024, 1024
        
        # Kolory w zależności od stylu
        style_colors = {
            "Fotograficzny": (220, 220, 220),  # Jasny szary
            "Rysunkowy": (240, 240, 240),       # Bardzo jasny szary
            "Komiksowy": (255, 255, 200)        # Jasnożółty
        }
        bg_color = style_colors.get(style, (220, 220, 220))
        
        # Utwórz obraz
        image = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(image)
        
        # Spróbuj załadować czcionkę, jeśli niedostępna użyj domyślnej
        try:
            title_font = ImageFont.truetype("arial.ttf", 40)
            text_font = ImageFont.truetype("arial.ttf", 24)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        # Rysuj informacje
        margin = 50
        y_position = margin
        
        # Nagłówek
        draw.text((margin, y_position), "ETR - Generator Grafik", fill=(0, 0, 0), font=title_font)
        y_position += 80
        
        # Styl
        draw.text((margin, y_position), f"Styl: {style}", fill=(50, 50, 50), font=text_font)
        y_position += 60
        
        # Temperatura
        draw.text((margin, y_position), f"Temperatura: {temperature:.2f}", fill=(50, 50, 50), font=text_font)
        y_position += 80
        
        # Prompt
        draw.text((margin, y_position), "Generated Prompt:", fill=(0, 0, 0), font=title_font)
        y_position += 60
        
        # Zawiń prompt na wiele linii
        words = prompt.split()
        line = ""
        max_width = width - 2 * margin
        
        for word in words:
            test_line = line + word + " "
            bbox = draw.textbbox((0, 0), test_line, font=text_font)
            if bbox[2] - bbox[0] > max_width:
                if line:
                    draw.text((margin, y_position), line, fill=(80, 80, 80), font=text_font)
                    y_position += 40
                line = word + " "
            else:
                line = test_line
        
        if line:
            draw.text((margin, y_position), line, fill=(80, 80, 80), font=text_font)
        
        # Konwertuj obraz do bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return img_byte_arr.getvalue()
        
    except Exception as e:
        st.error(f"Błąd podczas generowania obrazu placeholder: {e}")
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
            st.session_state.generation_mode = generation_mode
            
            with st.spinner("Tworzę grafikę..."):
                # Wybierz wariant generowania
                if "Wariant A" in generation_mode:
                    image_data = generate_image_variant_a(image_prompt, temperature)
                    if not image_data:
                        st.info("Wariant A niedostępny, przechodzę do Wariantu B...")
                        image_data = generate_image_variant_b(image_prompt, input_text, style, temperature)
                else:
                    image_data = generate_image_variant_b(image_prompt, input_text, style, temperature)
            
            if image_data:
                st.session_state.image_data = image_data
                # Rerun to display the image and feedback form cleanly
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
        st.image(st.session_state.image_data, caption="Wygenerowana grafika", use_container_width=True)

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
            if st.button("👍 Dobrze", use_container_width=True):
                save_feedback(rating="Dobrze", comments=comments)
                st.rerun()

        with col2:
            if st.button("👎 Źle", use_container_width=True):
                save_feedback(rating="Źle", comments=comments)
                st.rerun()




