# ETR Image Generator 🖼️

> **Note:** This project is developed in Polish language as it targets Polish-speaking users with intellectual disabilities (ETR - Easy to Read format in Poland).

Generator grafik ilustrujących do materiałów ETR (Easy to Read) - interaktywne narzędzie wykorzystujące AI do tworzenia fotorealistycznych obrazów zgodnych ze standardami dostępności dla osób z niepełnosprawnością intelektualną.

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red.svg)](https://streamlit.io/)
[![Google Gen AI](https://img.shields.io/badge/Google_Gen_AI-1.0+-green.svg)](https://ai.google.dev/)

## 🎯 Cel Projektu

Aplikacja wspiera tworzenie materiałów ETR poprzez automatyczne generowanie prostych, dosłownych, fotorealistycznych ilustracji. Wykorzystuje zaawansowane techniki AI (Chain-of-Thought, Few-Shot Learning) do zapewnienia wysokiej jakości wizualizacji zgodnych z wytycznymi dostępności.

## ✨ Kluczowe Funkcje

### 🤖 Inteligentna Analiza Tekstu
- **Chain-of-Thought Prompting:** Model pokazuje swoje rozumowanie w 4 krokach
- **Few-Shot Learning:** 4 przykłady uczące model prawidłowego podejścia
- **11 Zasad ETR:** Dosłowność, prostota, realizm, autentyczność lokalizacji i więcej

### 🎨 Generowanie Obrazów
- **Gemini 2.5 Flash Image:** Fotorealistyczne obrazy 1024x1024
- **Rozdzielone Temperatury:** Osobne kontrolki dla analizy (0.6) i obrazu (0.4)
- **Wariant B dla Emocji:** Mimika dla osób, symbolika dla abstrakcji

### 📊 Zbieranie Feedbacku
- Zapisywanie obrazów i metadanych do CSV
- Pełne śledzenie procesu (reasoning, prompt, parametry)
- System ocen z dodatkowymi uwagami

## 🚀 Szybki Start

### Wymagania
- Python 3.12 lub nowszy
- Klucz API Google Gemini ([pobierz tutaj](https://aistudio.google.com/app/apikey))

### Instalacja

1. **Sklonuj repozytorium:**
```bash
git clone https://github.com/JacZad/etr-img.git
cd etr-img
```

2. **Zainstaluj zależności:**
```bash
pip install -r requirements.txt
```

3. **Skonfiguruj klucz API:**

Skopiuj plik przykładowy:
```bash
cp .env.example .env
```

Edytuj `.env` i wstaw swój klucz:
```
GEMINI_API_KEY=your_api_key_here
```

Alternatywnie ustaw zmienną środowiskową:
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your_api_key_here"

# Linux/Mac
export GEMINI_API_KEY="your_api_key_here"
```

4. **Uruchom aplikację:**
```bash
streamlit run app.py
```

Aplikacja otworzy się w przeglądarce pod adresem `http://localhost:8501`

## 📖 Jak Używać

1. **Wklej tekst** w języku polskim do głównego pola tekstowego
2. **Opcjonalnie dostosuj** prompt systemowy w panelu bocznym
3. **Opcjonalnie zmień** temperatury w ustawieniach zaawansowanych
4. **Kliknij** "Generuj grafikę"
5. **Sprawdź** proces analizy w expanderach:
   - 📋 Proces analizy (Chain-of-Thought)
   - 🎨 Końcowy prompt
   - ⚙️ Pełny prompt systemowy
6. **Oceń** wynik (👍/👎) i zostaw uwagi

## 🗂️ Struktura Projektu

```
etr-img/
├── app.py                  # Główna aplikacja Streamlit
├── requirements.txt        # Zależności Python
├── .env.example           # Przykładowa konfiguracja
├── agents.md              # Szczegółowa dokumentacja techniczna
├── README.md              # Ten plik
├── generated_images/      # Folder z wygenerowanymi obrazami
└── feedback.csv           # Dane feedbacku i metadane
```

## 🧠 Zastosowane Techniki AI

| Technika | Opis | Korzyści |
|----------|------|----------|
| **Chain-of-Thought** | Model pokazuje rozumowanie (KROK 1-3) | Przejrzystość, lepsza jakość |
| **Few-Shot Learning** | 4 przykłady różnych typów scen ETR | Spójność ze standardem ETR |
| **Dual Temperature** | Osobne kontrolki dla tekstu (0.6) i obrazu (0.4) | Optymalna kreatywność vs stabilność |
| **Authenticity** | Konkretne lokalizacje i marki są autentyczne | Dokładność przekazu |
| **Hybrid Emotions** | Mimika dla osób, obiekty dla abstrakcji | Dosłowność + ekspresja emocji |

## 📋 Format Danych CSV

Każda generacja zapisuje następujące kolumny:
- `timestamp` - data i czas
- `original_text` - wprowadzony tekst
- `used_system_prompt` - użyty prompt systemowy
- `text_temperature` / `image_temperature` - parametry
- `reasoning` - pełne rozumowanie CoT (KROK 1-3)
- `generated_prompt` - końcowy prompt
- `image_filename` - nazwa pliku PNG
- `rating` - ocena (Dobrze/Źle)
- `comments` - uwagi użytkownika

## 🛠️ Stack Technologiczny

- **Python 3.12+** - język programowania
- **Streamlit** - framework UI
- **Google Gen AI SDK** - integracja z Gemini
  - `gemini-2.5-flash` - analiza tekstu
  - `gemini-2.5-flash-image` - generowanie obrazów
- **Pandas** - zarządzanie danymi
- **Pillow** - przetwarzanie obrazów
- **python-dotenv** - konfiguracja środowiska

## 🌟 Wymagania ETR

Aplikacja implementuje 11 zasad ETR dla grafik:

1. ✅ **DOSŁOWNOŚĆ** - bez metafor i symboli artystycznych
2. ✅ **PROSTOTA** - jedna scena, 1-2 elementy
3. ✅ **REALIZM** - fotorealistyczny styl
4. ✅ **JEDNOZNACZNOŚĆ** - typowe obiekty
5. ✅ **AUTENTYCZNOŚĆ** - konkretne lokalizacje (Wawel, Pałac Kultury) i marki są autentyczne
6. ✅ **KONTEKST POLSKI** - subtelne kulturowe wskazówki
7. ✅ **EMOCJE** - mimika twarzy lub proste obiekty
8. ✅ **KONTAKT WZROKOWY** - osoby patrzą na siebie
9. ✅ **BEZ TEKSTU** - unikaj napisów (wyjątek: kluczowe nazwy z tekstu)
10. ✅ **KOLORY** - stonowana paleta
11. ✅ **TŁO** - proste, nieodwracające uwagi

## 🔮 Roadmap

- [ ] A/B testing różnych wersji promptów
- [ ] Wsparcie dla alternatywnych modeli (DALL-E, Stable Diffusion)
- [ ] Cachowanie promptów dla oszczędności API
- [ ] Dashboard analityczny z metrykami
- [ ] Eksport do JSON/Excel

## 📄 Licencja

Ten projekt jest dostępny na zasadach open source. Zobacz plik `LICENSE` dla szczegółów.

## 🤝 Wkład w Projekt

Zapraszamy do zgłaszania issues i pull requestów! Przed zgłoszeniem PR:
1. Sprawdź czy issue już nie istnieje
2. Opisz zmianę w komentarzu do commita
3. Przetestuj kod lokalnie

## 📬 Kontakt

- **Autor:** JacZad
- **Repozytorium:** [github.com/JacZad/etr-img](https://github.com/JacZad/etr-img)

---

**Uwaga:** Projekt wymaga klucza API Google Gemini. Dostępne są darmowe limity API do testowania.
