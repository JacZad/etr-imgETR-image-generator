# Generator Grafik Ilustrujących do ETR

Aplikacja ma za zadanie generować grafiki do ETR (Easy to Read Text), czyli specjalnego formatu tekstu dla osób z niepełnosprawnością intelektualną. Została zbudowana jako interaktywne narzędzie do testowania różnych konfiguracji i zbierania danych zwrotnych.

## Stos technologiczny

* **Python 3**
* **Streamlit** - do budowy interfejsu użytkownika.
* **Google Generative AI for Python** - jako SDK do obsługi modeli AI.
  * Model językowy: **Gemini 2.5 Flash** (do analizy tekstu i tworzenia promptów).
  * Model graficzny: **Dwa warianty implementacji** (patrz: Warianty Generowania Grafik)
* **Pandas** - do zarządzania danymi zwrotnymi.
* **Pillow** - do generowania obrazów placeholder i edycji grafik.

## Opis działania

Aplikacja działa w oparciu o dwuetapowy proces generowania i posiada rozbudowany panel ustawień, który pozwala na pełną kontrolę nad procesem.

### Panel Ustawień (Sidebar)

W panelu bocznym użytkownik może konfigurować następujące parametry:

1. **Prompt Systemowy:** Użytkownik może edytować główną instrukcję (prompt systemowy), która jest wysyłana do modelu języka Gemini 2.5 Flash. Pozwala to na eksperymentowanie ze sposobem, w jaki model analizuje tekst i tworzy prompt do obrazu.
2. **Parametry Generowania:**
    * **Temperatura:** Suwak pozwalający ustawić kreatywność modelu (od 0.0 do 1.0).
    * **Styl Grafiki:** Pole wyboru pozwalające wybrać jeden z trzech stylów: `Fotograficzny`, `Rysunkowy`, `Komiksowy`.
3. **Tryb Generowania:** Wybór między dwoma wariantami generowania grafik (patrz: Warianty Generowania Grafik)

### Główny Proces

1. **Wprowadzenie Tekstu:** Użytkownik wkleja akapit tekstu w języku polskim.
2. **Analiza i Tworzenie Promptu:** Po wciśnięciu przycisku "Generuj grafikę", model `Gemini 2.5 Flash` analizuje tekst, biorąc pod uwagę instrukcje z **promptu systemowego** oraz wybrany **styl**. Na tej podstawie tworzy zwięzły, angielski prompt do generatora grafiki.
3. **Generowanie Grafiki:** Stworzony prompt jest przekazywany do wybranego wariantu generowania:
   - **Wariant A (Images API):** Próbuje użyć Google Images API do rzeczywistej generacji obrazu (wymaga uprawnień API).
   - **Wariant B (Fallback):** Generuje obraz placeholder z tekstem zawierającym prompt i parametry (domyślny, zawsze dostępny).
4. **Wyświetlanie Wyników i Przejrzystość Procesu:**
    * W głównym interfejsie wyświetlany jest wygenerowany obraz.
    * Poniżej znajduje się sekcja "Szczegóły procesu", gdzie użytkownik może sprawdzić:
        * Użyte parametry (styl, temperatura).
        * Dokładny prompt użyty do wygenerowania grafiki (w expanderze).
        * Pełny prompt systemowy, który został użyty do analizy (w expanderze).
5. **Zbieranie Ocen (Feedback Loop):**
    * Pod wynikami znajduje się formularz oceny z przyciskami "👍 Dobrze" i "👎 Źle" oraz polem na dodatkowe uwagi.
    * Po zapisaniu oceny, wszystkie dane o procesie oraz sama grafika są zapisywane na dysku.

### Zapisywane Dane

Grafiki są zapisywane w folderze `generated_images/`. Metadane każdej generacji i oceny są dopisywane do pliku `feedback.csv`, który zawiera następujące kolumny:

* `timestamp`: Data i czas generacji.
* `original_text`: Pierwotny tekst wprowadzony przez użytkownika.
* `used_system_prompt`: Pełna treść promptu systemowego użytego w danym cyklu.
* `style`: Wybrany styl grafiki.
* `temperature`: Ustawiona temperatura.
* `generated_prompt`: Prompt wygenerowany przez model językowy i użyty do stworzenia obrazu.
* `image_filename`: Nazwa pliku z zapisaną grafiką.
* `rating`: Ocena ("Dobrze" lub "Źle").
* `comments`: Dodatkowe uwagi od użytkownika.

## Wymagania dla grafiki

Wymagania zostały zaimplementowane poprzez odpowiednią konstrukcję domyślnego promptu systemowego oraz opcje w panelu bocznym.

* Grafika ma kształt kwadratu (generowana w rozdzielczości 1024x1024).
* Styl do wyboru: fotograficzny (domyślny), rysunkowy, komiksowy.
* Temperatura do ustawienia (domyślnie 0.0).
* Ograniczenie elementów graficznych i polski kontekst kulturowy są zasugerowane w domyślnym prompcie systemowym, który jest w pełni edytowalny.

## Warianty Generowania Grafik

### Wariant A: Images API (eksperymentalny)

- **Status:** Przygotowanie do przyszłej integracji
- **Opis:** Próbuje użyć Google Images API (gdy będzie dostępne) do rzeczywistej generacji obrazów
- **Zalety:** Profesjonalne, rzeczywiste obrazy zgodne z promptem
- **Limitacje:** Aktualnie Google nie udostępnia Images API w Python SDK
- **Kod:** Funkcja `generate_image_variant_a()` - zarezerwowana na przyszłość

### Wariant B: Placeholder + Tekst (zawsze dostępny)

- **Status:** Aktywny i w pełni funkcjonalny
- **Opis:** Generuje obraz placeholder (PNG 1024x1024) zawierający:
  - Styl grafiki
  - Wartość temperatury
  - Pełny tekst promptu wygenerowany przez AI
- **Zalety:** 
  - Zawsze dostępny, niezawodny
  - Pozwala na weryfikację poprawności promptu
  - Użytkownik może samodzielnie wygenerować obraz za pomocą innego narzędzia
- **Limitacje:** Obraz jest tekstem, nie rzeczywistą grafiką
- **Kod:** Funkcja `generate_image_variant_b()` - pełnie zaimplementowana

## Instalacja i Konfiguracja

### 1. Pobranie klucza API

1. Otwórz https://aistudio.google.com/app/apikey
2. Zaloguj się na konto Google (w razie potrzeby utwórz projekt)
3. Kliknij "Create API key"
4. Skopiuj wygenerowany klucz

### 2. Konfiguracja lokalnego środowiska

1. Otwórz plik `.env.example` w projekcie
2. Skopiuj go na `.env`
3. Zastąp `your_gemini_api_key_here` swoim kluczem API

### 3. Instalacja zależności

```bash
pip install -r requirements.txt
```

### 4. Uruchomienie aplikacji

```bash
streamlit run app.py
```

## Przyszłe Ulepszenia

1. **Integracja prawdziwych Images API:** Gdy Google udostępni oficjalny endpoint, zastąpi Wariant A
2. **Obsługa alternatywnych modeli:** Dodanie wsparcia dla DALL-E, Stable Diffusion, itp.
3. **Buforowanie promptów:** Oszczędzanie quotów API przez cachowanie
4. **Eksport danych:** Możliwość eksportu historii w różnych formatach (JSON, Excel)
