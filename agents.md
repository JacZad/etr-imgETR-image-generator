# Generator Grafik Ilustrujących do ETR

Aplikacja ma za zadanie generować grafiki do ETR (Easy to Read Text), czyli specjalnego formatu tekstu dla osób z niepełnosprawnością intelektualną. Została zbudowana jako interaktywne narzędzie do testowania różnych konfiguracji i zbierania danych zwrotnych.

## Stos technologiczny

* **Python 3.12+**
* **Streamlit** - do budowy interfejsu użytkownika.
* **Google Gen AI SDK (google-genai)** - jako SDK do obsługi modeli AI.
  * Model językowy: **Gemini 2.5 Flash** (do analizy tekstu i tworzenia promptów z Chain-of-Thought).
  * Model graficzny: **Gemini 2.5 Flash Image** (do generowania fotorealistycznych obrazów).
* **Pandas** - do zarządzania danymi zwrotnymi.
* **Pillow** - do przetwarzania obrazów.

## Opis działania

Aplikacja działa w oparciu o dwuetapowy proces generowania i posiada rozbudowany panel ustawień, który pozwala na pełną kontrolę nad procesem.

### Panel Ustawień (Sidebar)

W panelu bocznym użytkownik może konfigurować następujące parametry:

1. **Prompt Systemowy:** Użytkownik może edytować główną instrukcję (prompt systemowy), która jest wysyłana do modelu języka Gemini 2.5 Flash. Prompt zawiera:
   - Proces Chain-of-Thought (4 kroki analizy)
   - 10 zasad ETR (dosłowność, prostota, realizm, itp.)
   - 3 przykłady few-shot learning
2. **Parametry Generowania (Ustawienia zaawansowane):**
    * **Temperatura analizy tekstu:** Kontroluje kreatywność interpretacji tekstu (domyślnie 0.6)
### Główny Proces

1. **Wprowadzenie Tekstu:** Użytkownik wkleja akapit tekstu w języku polskim.

2. **Analiza z Chain-of-Thought:** Po wciśnięciu przycisku "Generuj grafikę", model `Gemini 2.5 Flash` analizuje tekst w 4 krokach:
   - **KROK 1 - IDENTYFIKACJA:** Rozpoznaje główny temat, emocje i kontekst
   - **KROK 2 - UPROSZCZENIE:** Redukuje do 1-2 kluczowych elementów
   - **KROK 3 - WIZUALIZACJA ETR:** Stosuje 11 zasad ETR (w tym autentyczność lokalizacji i obiektów)
   - **KROK 4 - WYGENERUJ PROMPT:** Tworzy zwięzły, angielski prompt fotorealistyczny
   
   Model uczy się na 4 przykładach (few-shot learning):
   - Scena z obiektami (autobus + kasownik)
   - Emocja osoby przez mimikę (smutek po utracie pracy)
   - Abstrakcyjna emocja przez obiekt (strach przed igłą → strzykawka)
   - Konkretna lokalizacja (Zamek na Wawelu → autentyczny obraz Wawelu)

3. **Generowanie Grafiki:** Stworzony prompt jest przekazywany do modelu `Gemini 2.5 Flash Image`, który generuje fotorealistyczny obraz w rozdzielczości 1024x1024.

4. **Wyświetlanie Wyników i Przejrzystość Procesu:**
    * W głównym interfejsie wyświetlany jest wygenerowany obraz.
### Zapisywane Dane

Grafiki są zapisywane w folderze `generated_images/`. Metadane każdej generacji i oceny są dopisywane do pliku `feedback.csv`, który zawiera następujące kolumny:

* `timestamp`: Data i czas generacji.
* `original_text`: Pierwotny tekst wprowadzony przez użytkownika.
* `used_system_prompt`: Pełna treść promptu systemowego użytego w danym cyklu.
* `text_temperature`: Temperatura użyta do analizy tekstu.
* `image_temperature`: Temperatura użyta do generowania obrazu.
* `reasoning`: Pełne rozumowanie modelu (KROK 1-3 z Chain-of-Thought).
* `generated_prompt`: Końcowy prompt wygenerowany przez model językowy i użyty do stworzenia obrazu.
* `image_filename`: Nazwa pliku z zapisaną grafiką.
* `rating`: Ocena ("Dobrze" lub "Źle").
* `comments`: Dodatkowe uwagi od użytkownika.
## Wymagania dla grafiki

Wymagania ETR zostały zaimplementowane poprzez odpowiednią konstrukcję domyślnego promptu systemowego z 11 zasadami:

1. **DOSŁOWNOŚĆ:** Bez metafor i symboli artystycznych
2. **PROSTOTA:** Jedna scena, 1-2 obiekty/osoby, proste tło
3. **REALIZM:** Styl fotorealistyczny
4. **JEDNOZNACZNOŚĆ:** Typowe, łatwo rozpoznawalne obiekty
5. **AUTENTYCZNOŚĆ:** Konkretne lokalizacje, obiekty i marki z tekstu muszą być przedstawione autentycznie (np. Wawel → "Wawel Castle in Krakow", nie "generic castle")
6. **KONTEKST POLSKI:** Subtelne wskazówki polskiego kontekstu
7. **EMOCJE:** Mimika twarzy dla osób, proste obiekty dla abstrakcji
8. **KONTAKT WZROKOWY:** Osoby patrzą na siebie
9. **BEZ TEKSTU:** Unikaj napisów (wyjątek: konkretne nazwy/marki z tekstu)
10. **KOLORY:** Ograniczona paleta, stonowane barwy
11. **TŁO:** Jednolite lub delikatny gradient

Grafika ma kształt kwadratu (rozdzielczość 1024x1024).
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
## Techniki AI zastosowane w projekcie

### 1. Chain-of-Thought Prompting
Model wyświetla swoje rozumowanie w 3 krokach przed wygenerowaniem promptu, co zwiększa jakość i przejrzystość procesu.
### 2. Few-Shot Learning
Prompt systemowy zawiera 4 szczegółowe przykłady różnych typów scen ETR, z których model uczy się odpowiedniego podejścia:
- Sceny z konkretnymi obiektami
- Emocje wyrażone przez mimikę
- Abstrakcyjne emocje przez symbole
- Autentyczne lokalizacje (Wawel)
Prompt systemowy zawiera 3 szczegółowe przykłady różnych typów scen ETR, z których model uczy się odpowiedniego podejścia.
### 4. Wariant B dla Emocji
Hybrydowe podejście:
- Osoby z emocjami → mimika + język ciała
- Abstrakcyjne emocje → prosty obiekt symboliczny

### 5. Autentyczność i Konkretność
Model został wytrenowany aby:
- Rozpoznawać konkretne lokalizacje (np. Wawel, Pałac Kultury) i generować ich autentyczne obrazy
- Zachowywać nazwy marek i konkretnych obiektów z tekstu
- NIE zamieniać szczegółów na ogólnikiejście dla stabilnej jakości wizualnej

### 4. Wariant B dla Emocji
Hybrydowe podejście:
- Osoby z emocjami → mimika + język ciała
- Abstrakcyjne emocje → prosty obiekt symboliczny

## Przyszłe Ulepszenia

1. **A/B Testing:** Automatyczne porównywanie różnych wersji promptów
2. **Obsługa alternatywnych modeli:** Dodanie wsparcia dla DALL-E, Stable Diffusion, itp.
3. **Buforowanie promptów:** Oszczędzanie quotów API przez cachowanie
4. **Eksport danych:** Możliwość eksportu historii w różnych formatach (JSON, Excel)
5. **Analityka:** Dashboard z metrykami ocen i najpopularniejszymi wzorcami