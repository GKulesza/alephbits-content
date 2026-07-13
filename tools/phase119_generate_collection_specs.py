#!/usr/bin/env python3
"""Generate phase119 Collection Ten/Eleven spec JSON files."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
BUILD_SPECS = TOOLS / "phase119_build_specs.py"
C10_MANUSCRIPT = Path(
    "/Users/admin/Developer/MiscellaneousNotes/AwesomeVault/!Apps/App Ideas/alephBits/Books/10 CollectionTen.md"
)
C11_MANUSCRIPT = Path(
    "/Users/admin/Developer/MiscellaneousNotes/AwesomeVault/!Apps/App Ideas/alephBits/Books/11 CollectionEleven.md"
)
OUT_C10 = TOOLS / "phase119_collection_ten_specs.json"
OUT_C11 = TOOLS / "phase119_collection_eleven_specs.json"

C10_TITLES = [
    "Chór",
    "Dobra dziewczynka",
    "Kij i marchewka",
    "W pełni",
    "Poligon",
    "Radio w głowie",
    "Nowy świat",
    "Autorytet na przepraszam",
    "Cisza",
    "Naczynia połączone",
    "Ułamki",
    "Przedszkole bez ścian",
    "Etykieta",
    "Jeszcze",
    "Lista rzeczy, których żałuję",
    "Bogini i liczby",
]

C11_TITLES = [
    "Święci wojownicy",
    "Klucz babci Rózi",
    "Cudaczek-Wyśmiewaczek",
    "Kapuściana tajemnica",
    "Złoto i zwykłe szczęście",
    "Ciekawska Zosia i skarb przyjaźni",
    "Koziołek Matołek i podróż do Pacanowa",
    "Nowy ogród",
    "Ciche serce dzwonka",
    "Głos i cisza",
    "Franek i mały Karolek",
    "Klucz do deszczowej krainy",
    "Ognioskoczek",
    "Cukierek z magicznego drzewa",
    "Pies Pankracy i sprawy ważne",
]

C11_SKIP = {"Sprawa"}

REQUIRED_FIELDS = [
    "manuscript_title",
    "slug",
    "pack_id",
    "display_title",
    "subtitle",
    "blurb",
    "genres",
    "cover_family",
    "audience",
    "difficulty",
    "reader_stars",
    "trust",
    "tags",
    "keywords",
    "editorial_notes",
    "inspiration",
    "philosophy_stars",
    "philosophy_note",
    "founder_notes",
    "series",
    "motifs",
    "quiz",
]

ACT_SECTIONS = {
    "WSTĘP",
    "ROZWINIĘCIE",
    "ZAKOŃCZENIE",
    "EPILOG",
    "CO WIEDZIAŁ",
}

C10_QUIZZES = {
    "Chór": [
        {
            "question": "O co kłócą się Magda i Tomek na początku opowieści?",
            "answers": [
                "O rozstanie",
                "O to, że Franek nie wyłączył tabletu po czasie ekranowym",
                "O wakacje",
                "O pracę Magdy"
            ],
            "correct": "B",
            "explanation": "Franek grał w piłkę nożną na tablecie po 18:45.",
            "reference": "Wyłącz to"
        },
        {
            "question": "Co Franek pyta matkę po kłótni?",
            "answers": [
                "Czy dostanie tablet",
                "Czy rodzice się jeszcze kochają",
                "Czy pójdą do kina",
                "Czy Zosia jest chora"
            ],
            "correct": "B",
            "explanation": "Franek pyta wprost: „Czy wy się jeszcze kochacie?”.",
            "reference": "Czy wy się jeszcze kochacie"
        },
        {
            "question": "Czyja podcastowa myśl Magda przywołuje w sypialni?",
            "answers": [
                "Jespera Jula",
                "Agi Rogali",
                "Marii Berlińskiej",
                "Szymona Grzelaka"
            ],
            "correct": "B",
            "explanation": "Magda cytuje Agę Rogalę o zbędnych kłótniach i pracy nad sobą.",
            "reference": "podcast Agi Rogali"
        },
        {
            "question": "Jak Tomek reaguje, gdy Franek prosi o wcześniejsze ostrzeżenie przed zabraniem tabletu?",
            "answers": [
                "Krzyknie",
                "Uśmiecha się i mówi „Umowa stoi”",
                "Ignoruje syna",
                "Każe iść spać"
            ],
            "correct": "B",
            "explanation": "Tomek akceptuje propozycję i mówi: „Umowa stoi”.",
            "reference": "Umowa stoi"
        },
        {
            "question": "Co metafora „chóru głosów” oznacza w finale?",
            "answers": [
                "Że dzieci powinny milczeć",
                "Że w rodzicach brzmią głosy poprzednich pokoleń, których uczą się słuchać i przekształcać",
                "Że rodzina śpiewa w kościele",
                "Że Tomek zostaje śpiewakiem"
            ],
            "correct": "B",
            "explanation": "Tomek i Magda uczą się słuchać głosów rodziców/dziadków i „śpiewać własną melodię”.",
            "reference": "Chór głosów"
        }
    ],
    "Dobra dziewczynka": [
        {
            "question": "Kiedy Zosia po raz pierwszy słyszy, że jest „grzeczną dziewczynką”?",
            "answers": [
                "W szkole",
                "Ma około pięciu lat przy śniadaniu",
                "Na studiach",
                "Po urodzeniu syna"
            ],
            "correct": "B",
            "explanation": "Mama mówi jej to nad śniadaniem, gdy ma pięć lat.",
            "reference": "pięć lat"
        },
        {
            "question": "Co Zosia robi po raz pierwszy w wieku ~15 lat?",
            "answers": [
                "Zmienia szkołę",
                "Mówi „nie jadę” na próbę chóru",
                "Wyjeżdża na Erasmusa",
                "Rezygnuje z Instagrama"
            ],
            "correct": "B",
            "explanation": "Odmawia wyjazdu na próbę chóru i zamyka się w łazience.",
            "reference": "Nie jadę"
        },
        {
            "question": "Jaki kierunek studiów wybiera po rozczarowaniu dziennikarstwem?",
            "answers": [
                "Psychologię",
                "Europeistykę",
                "Medycynę",
                "Prawo"
            ],
            "correct": "B",
            "explanation": "Przenosi się na europeistykę ze względu na Erasmusa i podróże.",
            "reference": "europeistykę"
        },
        {
            "question": "Co Zosia zaczyna robić w czasie pandemii i trudnej ciąży?",
            "answers": [
                "Pisać powieść kryminalną",
                "Nagrywać rozmowy i publikować w social media",
                "Prowadzić restaurację",
                "Uczyć się programowania"
            ],
            "correct": "B",
            "explanation": "Nagrywa rozmowy dla rodziny, potem Instagram/TikTok/YouTube.",
            "reference": "Nagrywać rozmowy"
        },
        {
            "question": "Co Zosia powiedziałaby swojej młodej wersji?",
            "answers": [
                "Bądź jeszcze bardziej idealna",
                "Nie musisz być doskonała — wystarczy, że będziesz sobą",
                "Rzuć szkołę",
                "Nigdy nie mów nie"
            ],
            "correct": "B",
            "explanation": "W wywiadzie mówi: „Nie musisz być taka doskonała. Wystarczy, że będziesz sobą”.",
            "reference": "Wystarczy, że będziesz sobą"
        }
    ],
    "Kij i marchewka": [
        {
            "question": "Co Magda mówi do Tymona zamiast wysłać go do kąta w sklepie?",
            "answers": [
                "Idź do kąta",
                "Potrzebuję przytulenia",
                "Dostaniesz klapsa",
                "Nigdy więcej nie pójdziemy na zakupy"
            ],
            "correct": "B",
            "explanation": "Powtarza: „Potrzebuję przytulenia” — i chłopiec się uspokaja.",
            "reference": "Potrzebuję przytulenia"
        },
        {
            "question": "Ile długofalowych skutków kary wymienia Magda?",
            "answers": [
                "Dwa",
                "Cztery",
                "Sześć",
                "Jeden"
            ],
            "correct": "B",
            "explanation": "Rozgoryczenie, rewanż, rebelia i wycofanie.",
            "reference": "czterech długofalowych skutków"
        },
        {
            "question": "Co robi Magda, gdy Tymon rozlewa sok na dywan?",
            "answers": [
                "Krzyknie i zabiera zabawkę",
                "Pyta: „Co możemy zrobić?” i wspólnie czyści",
                "Ignoruje bałagan",
                "Każe iść do kąta"
            ],
            "correct": "B",
            "explanation": "Pokazuje konsekwencję (sprzątanie), nie karę.",
            "reference": "Co możemy zrobić"
        },
        {
            "question": "Jak Gabryś proponuje nazwać kącik w domu?",
            "answers": [
                "Kącikiem kary",
                "Kącikiem spokoju",
                "Kącikiem nauki",
                "Kącikiem gier"
            ],
            "correct": "B",
            "explanation": "Gabryś mówi: „Kącikiem spokoju — bo jak jestem spokojny, to myślę lepiej”.",
            "reference": "Kącikiem spokoju"
        },
        {
            "question": "Jaki jest główny wniosek opowieści?",
            "answers": [
                "Dzieci muszą być posłuszne",
                "Chodzi o to, by dzieci były gotowe na życie — umiały radzić sobie z emocjami",
                "Kary są najskuteczniejsze",
                "Nagrody słodyczami są obowiązkowe"
            ],
            "correct": "B",
            "explanation": "Finale: „Nie chodzi o to, żeby dzieci były posłuszne. Chodzi o to, żeby były gotowe na życie”.",
            "reference": "gotowe na życie"
        }
    ],
    "W pełni": [
        {
            "question": "Czyja teza o dziecku „w 100% kompletnym” zmienia myślenie Oli?",
            "answers": [
                "Agi Rogali",
                "Jespera Jula",
                "Hardy'ego",
                "Szymona Grzelaka"
            ],
            "correct": "B",
            "explanation": "Słyszy o Jesperze Julu i tezie o kompletnym człowieku od narodzin.",
            "reference": "Jesperze Julu"
        },
        {
            "question": "Co Ola robi, gdy Franek boi się basenu?",
            "answers": [
                "Zmusza go do nauki pływania",
                "Pyta o uczucia i proponuje rękawki",
                "Anuluje wyjazd",
                "Krzyknie"
            ],
            "correct": "B",
            "explanation": "Pyta „Co czujesz?” i wspólnie szukają bezpieczeństwa (rękawki).",
            "reference": "Co czujesz"
        },
        {
            "question": "Co Franek mówi po udanym pływaniu?",
            "answers": [
                "Nigdy więcej na basen",
                "Mamo, ja mogę wszystko, jak mi pozwolisz",
                "Chcę zostać trenerem",
                "Basen jest głupi"
            ],
            "correct": "B",
            "explanation": "Franek: „Mamo, ja mogę wszystko, jak mi pozwolisz”.",
            "reference": "jak mi pozwolisz"
        },
        {
            "question": "Co Zosia robi z nożyczkami mimo pierwszego odruchu matki?",
            "answers": [
                "Zabrania im używać",
                "Pyta o bezpieczne użycie i pozwala wyciąć serduszko",
                "Oddaje nożyczki nauczycielce",
                "Karze"
            ],
            "correct": "B",
            "explanation": "Ola pyta o bezpieczne użycie i towarzyszy — Zosia wycina serduszko sama.",
            "reference": "Tato, zrobiłam to sama"
        },
        {
            "question": "Dlaczego wprowadza rutyny dla Zosi?",
            "answers": [
                "Jako kary",
                "Jako pomoc przy możliwym ADHD — mniej bodźców, stały rytm snu, bez ekranów",
                "Bo nauczyciel każe",
                "Dla sportu"
            ],
            "correct": "B",
            "explanation": "Uporządkowana przestrzeń, rutyna, timer do zębów, brak ekranów przed snem.",
            "reference": "rytm dobowy"
        }
    ],
    "Poligon": [
        {
            "question": "Co ojciec mówi Maćkowi przy kawałku stali w warsztacie?",
            "answers": [
                "Metal trzeba hartować w ogniu — tak samo człowieka",
                "Ucz się grać na gitarze",
                "Bądź miły dla matki",
                "Czytaj codziennie"
            ],
            "correct": "A",
            "explanation": "Metafora hartowania metalu = wychowanie „twardym” bólem.",
            "reference": "hartować w ogniu"
        },
        {
            "question": "Jak Maciek nazywa brak bezpiecznej przystani u rodziców?",
            "answers": [
                "Raj",
                "Poligon",
                "Bibliotekę",
                "Most"
            ],
            "correct": "B",
            "explanation": "Myśli: „Ja nie mam takiej przystani. Ja mam poligon”.",
            "reference": "mam poligon"
        },
        {
            "question": "Co mówi psycholog Maciekowi?",
            "answers": [
                "Rodzice byli źli",
                "Rodzice nie byli źli — byli nieobecni i nieumiejący; to nie jego wina",
                "Powinien wrócić do domu",
                "Nie powinien mieć dzieci"
            ],
            "correct": "B",
            "explanation": "Psycholog: nieobecni, nieumiejący — i to nie wina Maćka.",
            "reference": "nie twoja wina"
        },
        {
            "question": "Co Maciek mówi ojcu po latach?",
            "answers": [
                "Że go nienawidzi",
                "Że bał się jego nieprzewidywalności i myślał, że to z nim jest coś nie tak",
                "Że dziękuje za surowość",
                "Nic — nie odwiedza go"
            ],
            "correct": "B",
            "explanation": "Opowiada o strachu i przekonaniu, że jest „słaby”.",
            "reference": "bałem się ciebie"
        },
        {
            "question": "Co rysuje córka na końcu?",
            "answers": [
                "Dinozaura",
                "Rodzinę — wszyscy się uśmiechają",
                "Samochód",
                "Dom bez ludzi"
            ],
            "correct": "B",
            "explanation": "Córka: „To my — ja, ty i mama. I wszyscy się uśmiechamy”.",
            "reference": "wszyscy się uśmiechamy"
        }
    ],
    "Radio w głowie": [
        {
            "question": "Jak Kasia opisuje swoje ADHD psychologowi?",
            "answers": [
                "Jestem leniwa",
                "Mam w głowie radio — wszystkie stacje naraz",
                "Nie lubię szkoły",
                "Jestem chora"
            ],
            "correct": "B",
            "explanation": "Mówi: „Mam w głowie radio… Grają wszystkie stacje naraz”.",
            "reference": "Mam w głowie radio"
        },
        {
            "question": "Co pomaga Kasi skupić się na lekcji?",
            "answers": [
                "Kary",
                "Gniotek sensoryczny i możliwość krótkiego ruchu",
                "Zakaz rozmów",
                "Usunięcie z klasy"
            ],
            "correct": "B",
            "explanation": "Dostaje gniotka; może wstać na chwilę bez przeszkadzania.",
            "reference": "gniotka sensorycznego"
        },
        {
            "question": "Co mama robi przed snem?",
            "answers": [
                "Włącza telewizor",
                "Eliminuje ekrany — czytanie i cisza",
                "Daje energetyki",
                "Odrabia za Kasię lekcje"
            ],
            "correct": "B",
            "explanation": "Bez ekranów przed snem; czytanie książek.",
            "reference": "żadnych ekranów"
        },
        {
            "question": "Co Kasia mówi klasie o ADHD?",
            "answers": [
                "To znaczy, że jestem chora",
                "Mój mózg działa inaczej, nie gorzej",
                "Powinnam siedzieć w kącie",
                "Nigdy nie będę dobra w szkole"
            ],
            "correct": "B",
            "explanation": "„Nie. To znaczy, że mój mózg działa inaczej. Nie gorzej”.",
            "reference": "inaczej. Nie gorzej"
        },
        {
            "question": "Kim Kasia chce zostać na studiach?",
            "answers": [
                "Lekarką",
                "Psychologiem — pomagać dzieciom jak ona",
                "Piosenkarką",
                "Programistką"
            ],
            "correct": "B",
            "explanation": "Studiuje psychologię, by wspierać dzieci z podobnymi trudnościami.",
            "reference": "Studiuje psychologię"
        }
    ],
    "Nowy świat": [
        {
            "question": "Co mówił ojciec Tomka, gdy ten próbował się wypowiedzieć?",
            "answers": [
                "Dzieci i ryby głosu nie mają",
                "Mów głośniej",
                "Pytaj o wszystko",
                "Ucz się sam"
            ],
            "correct": "A",
            "explanation": "Ojciec: „Dzieci i ryby głosu nie mają — masz słuchać, nie gadać”.",
            "reference": "Dzieci i ryby głosu nie mają"
        },
        {
            "question": "Co uruchamia refleksję Tomka w samochodzie?",
            "answers": [
                "SMS od szefa",
                "Podcast z Marią Berlińską o dialogu z dziećmi",
                "Film akcji",
                "Reklama"
            ],
            "correct": "B",
            "explanation": "Słyszy: „Kiedyś dzieci miały słuchać, a teraz chcą być w dialogu”.",
            "reference": "U Sawickich"
        },
        {
            "question": "Co Zosia mówi, czego potrzebuje od taty?",
            "answers": [
                "Więcej prezentów",
                "Żeby był ze mną — nie tylko fizycznie",
                "Nowego telefonu",
                "Żeby nie pracował"
            ],
            "correct": "B",
            "explanation": "„Potrzebuję, żebyś był ze mną. Nie tylko fizycznie”.",
            "reference": "Nie tylko fizycznie"
        },
        {
            "question": "Co Tomek zmienia wieczorami?",
            "answers": [
                "Więcej telewizora",
                "Odkłada telefon i rozmawia z dziećmi",
                "Wysyła dzieci do babci",
                "Kupuje im gry"
            ],
            "correct": "B",
            "explanation": "Wieczory bez telefonów — rozmowa, czytanie, spacer.",
            "reference": "odkładał telefon"
        },
        {
            "question": "Co mówi nauczycielka na wywiadówce?",
            "answers": [
                "Że Zosia się pogorszyła",
                "Że Zosia jest bardziej otwarta — i Tomek odpowiada: „Ja się zmienił”",
                "Że Zosia powinna zmienić szkołę",
                "Nic"
            ],
            "correct": "B",
            "explanation": "Nauczycielka widzi zmianę; Tomek: „Ja się zmienił”.",
            "reference": "Ja się zmienił"
        }
    ],
    "Autorytet na przepraszam": [
        {
            "question": "Jak pani Maria definiuje budowanie autorytetu?",
            "answers": [
                "Na nakazach i zakazach",
                "Na „przepraszam” i przyznawaniu się do błędów",
                "Na karach",
                "Na nagrodach"
            ],
            "correct": "B",
            "explanation": "„Autorytet… zbuduje się go na przepraszam”.",
            "reference": "na przepraszam"
        },
        {
            "question": "Co Ania robi, gdy Marysia rozlewa mleko?",
            "answers": [
                "Krzyknie „Znowu?”",
                "Przytula i proponuje wspólne wytarcie; chwali próbę samodzielności",
                "Każe iść do pokoju",
                "Ignoruje"
            ],
            "correct": "B",
            "explanation": "Opisowe wsparcie zamiast strofowania.",
            "reference": "Widzę, że bardzo się starałaś"
        },
        {
            "question": "Jak Marek chwali rysunek Marysi?",
            "answers": [
                "„Jesteś piękna”",
                "Opisowo: widzi szczegóły, czas pracy, talent do obserwacji",
                "„Świetnie” i koniec",
                "Nie chwali"
            ],
            "correct": "B",
            "explanation": "Marek mówi o kwiatkach w tle i długiej pracy nad rysunkiem.",
            "reference": "kwiatki w tle"
        },
        {
            "question": "Czego Marek się boi, mówiąc o swoim ojcu?",
            "answers": [
                "Że syn go nie kocha",
                "Że stanie się jak ojciec, który nigdy nie przepraszał ani nie mówił „kocham cię”",
                "Że straci pracę",
                "Że wyjadą za granicę"
            ],
            "correct": "B",
            "explanation": "Marek: ojciec nigdy nie przepraszał — on nie wie, jak być inaczej.",
            "reference": "nigdy mnie nie przeprosił"
        },
        {
            "question": "Jaką bajkę czyta Ania na koniec?",
            "answers": [
                "O Kopciuszku",
                "O smoku, który nie umiał przepraszać",
                "O kosmonaucie",
                "O psie"
            ],
            "correct": "B",
            "explanation": "Marysia prosi: „O smoku, który nie umiał przepraszać”.",
            "reference": "smoku, który nie umiał przepraszać"
        }
    ],
    "Cisza": [
        {
            "question": "Co oznacza shitsuke w opowieści?",
            "answers": [
                "Karanie za każdy błąd",
                "Budowanie umiejętności zamiast karania",
                "Ignorowanie dziecka",
                "Nagradzanie słodyczami"
            ],
            "correct": "B",
            "explanation": "Shitsuke pyta: jakiej umiejętności brakuje dziecku?",
            "reference": "Budowanie umiejętności"
        },
        {
            "question": "Co robi Kasia, gdy Franek nie może zapiąć kurtki?",
            "answers": [
                "Zapina za niego od razu",
                "Czeka 10 sekund zanim pomoże",
                "Krzyknie",
                "Wychodzi bez niego"
            ],
            "correct": "B",
            "explanation": "Mimamoru — czeka z miłością; Franek sam zapina.",
            "reference": "Poczekaj tylko 10 sekund"
        },
        {
            "question": "Co to amae według filmu?",
            "answers": [
                "Karanie publiczne",
                "Bycie bezpiecznym bez słów — dziecko może oprzeć się na miłości",
                "Samodzielność bez rodzica",
                "Konkursy piękności"
            ],
            "correct": "B",
            "explanation": "Amae = bezpieczne przywiązanie umożliwiające spokój.",
            "reference": "bezpiecznym bez słów"
        },
        {
            "question": "Co mówi głos z filmu o wychowaniu?",
            "answers": [
                "Wychowanie zmienia dziecko",
                "Wychowanie zmienia ciebie — i to wystarczy",
                "Wychowanie nie ma znaczenia",
                "Wychowanie to tylko kara"
            ],
            "correct": "B",
            "explanation": "„Wychowanie nie zmienia twojego dziecka. Zmienia ciebie”.",
            "reference": "Zmienia ciebie"
        },
        {
            "question": "Jaka cisza zapanowała w domu na końcu?",
            "answers": [
                "Cisza napięcia i strachu",
                "Cisza zaufania i obecności",
                "Cisza, bo wszyscy poszli spać",
                "Brak rozmów"
            ],
            "correct": "B",
            "explanation": "Cisza obecności, zaufania i miłości — nie braku dźwięków.",
            "reference": "ciszą, która rodzi się z obecności"
        }
    ],
    "Naczynia połączone": [
        {
            "question": "Jak Anna opisuje rodzinę?",
            "answers": [
                "Jako więzienie",
                "Jako naczynia połączone — poziom wody zmienia się wszędzie",
                "Jako firmę",
                "Jako teatr"
            ],
            "correct": "B",
            "explanation": "Rodzina jak połączone naczynia — wpływ w obie strony.",
            "reference": "naczynia połączone"
        },
        {
            "question": "Co Anna proponuje zamiast kar typu zabierania tabletu?",
            "answers": [
                "Konsekwencje i naprawianie szkody",
                "Ignorowanie",
                "Wykluczenie ze szkoły",
                "Publiczne upokorzenie"
            ],
            "correct": "A",
            "explanation": "Konsekwencje naturalne — przeprosiny, sprzątanie, naprawa.",
            "reference": "konsekwencje"
        },
        {
            "question": "Co Marta mówi Kacprowi, gdy rzuca rzeczami?",
            "answers": [
                "Masz zakaz emocji",
                "Masz prawo być zły, ale nie możesz rzucać rzeczami",
                "Idź do kąta natychmiast",
                "Nic nie mówi"
            ],
            "correct": "B",
            "explanation": "„Masz prawo być zły” + jasna granica.",
            "reference": "Masz prawo być zły"
        },
        {
            "question": "Co Kacper robi, gdy się denerwuje w szkole po zmianach?",
            "answers": [
                "Bije innych",
                "Siada na dywanie, ściska gniotka, mówi „potrzebuję chwili”",
                "Ucieka ze szkoły",
                "Krzyczy na nauczycielkę"
            ],
            "correct": "B",
            "explanation": "Uczy się regulacji — gniotek, chwila, wyjście.",
            "reference": "potrzebuję chwili"
        },
        {
            "question": "Co jest na rysunku, który Kacper daje Annie?",
            "answers": [
                "Dinozaur",
                "Podziękowanie: „nauczyłaś mnie, jak być dobrym”",
                "Dom bez ludzi",
                "Mapa"
            ],
            "correct": "B",
            "explanation": "Napis: „Dziękuję, że nauczyłaś mnie, jak być dobrym”.",
            "reference": "jak być dobrym"
        }
    ],
    "Ułamki": [
        {
            "question": "Co Aga Rogala mówi o zdaniu „Załóż kurtkę”?",
            "answers": [
                "To jedno proste polecenie",
                "To wiele kroków: haczyk, rękawy, zamek itd.",
                "To nie ma sensu",
                "To tylko dla dorosłych"
            ],
            "correct": "B",
            "explanation": "Dla dziecka jedno zdanie = seria skomplikowanych czynności.",
            "reference": "wiele czynności"
        },
        {
            "question": "Co Magda robi następnego ranka?",
            "answers": [
                "Wkłada kurtkę Zosi sama",
                "Siada obok i prowadzi krok po kroku",
                "Rezygnuje z przedszkola",
                "Krzyknie"
            ],
            "correct": "B",
            "explanation": "„Pokażę ci, jak się ubieramy. Razem”.",
            "reference": "krok po kroku"
        },
        {
            "question": "Jak Magda tłumaczy „szykuj się do spania”?",
            "answers": [
                "Jednym słowem wystarczy",
                "Dzieli na: łazienka, zęby, piżama, łóżko",
                "Każe iść spać w ubraniu",
                "Ignoruje"
            ],
            "correct": "B",
            "explanation": "Konkretna lista kroków wieczornych.",
            "reference": "Pierwsze: idziemy do łazienki"
        },
        {
            "question": "Jak Zosia porównuje instrukcje do piosenki?",
            "answers": [
                "Nie lubi piosenek",
                "Jak zna słowa — śpiewa sama; jak nie — mama pomaga",
                "Zawsze potrzebuje mamy",
                "Nigdy nie pamięta"
            ],
            "correct": "B",
            "explanation": "Metafora piosenki = stopniowa samodzielność.",
            "reference": "Jak znam wszystkie słowa"
        },
        {
            "question": "Co Zosia robi sama po kilku tygodniach?",
            "answers": [
                "Gotuje obiad dla rodziny",
                "Robi kanapkę i herbatę krok po kroku",
                "Jedzie autobusem",
                "Pisze list do Agi"
            ],
            "correct": "B",
            "explanation": "Opisuje kroki: chleb, masło, ser, herbata.",
            "reference": "Zrobiłam sobie sama"
        }
    ],
    "Przedszkole bez ścian": [
        {
            "question": "Co Franek pyta o kolorowance z jabłkiem?",
            "answers": [
                "Czy może być fioletowe",
                "Czy dostanie nagrodę",
                "Czy pani Marta odchodzi",
                "Czy jabłko jest jadalne"
            ],
            "correct": "A",
            "explanation": "Franek: „Moje może być fioletowe?”.",
            "reference": "fioletowe"
        },
        {
            "question": "Gdzie dzieci spędzają większość czasu po zmianie?",
            "answers": [
                "W sali z kolorowankami",
                "Na dworze, niezależnie od pogody",
                "W kinie",
                "W domu"
            ],
            "correct": "B",
            "explanation": "Grażyna: większość czasu na dworze, uczenie przez doświadczenie.",
            "reference": "na dworze"
        },
        {
            "question": "Jak zaczyna się projekt o dinozaurach?",
            "answers": [
                "Od testu pisemnego",
                "Od figurki dinozaura, którą Franek przynosi",
                "Od kary",
                "Od rodziców"
            ],
            "correct": "B",
            "explanation": "Franek przynosi figurkę — dzieci chcą wiedzieć więcej.",
            "reference": "figurkę dinozaura"
        },
        {
            "question": "Kogo Marta zaprasza do przedszkola?",
            "answers": [
                "Astronautę",
                "Tatę Franka — weterynarza",
                "Politka",
                "Piosenkarza"
            ],
            "correct": "B",
            "explanation": "Tata Franka opowiada o zwierzętach; powstaje kącik weterynaryjny.",
            "reference": "weterynarzem"
        },
        {
            "question": "Co Franek mówi Martę po latach jako uczeń?",
            "answers": [
                "Nienawidził przedszkola",
                "W szkole też lubi się uczyć, bo może pytać",
                "Zapomniał dinozaurów",
                "Chce zostać nauczycielem"
            ],
            "correct": "B",
            "explanation": "Franek: w szkole lubi uczyć się, bo wie, że może pytać.",
            "reference": "mogę pytać"
        }
    ],
    "Etykieta": [
        {
            "question": "Co ojciec Kamila mówił mu regularnie?",
            "answers": [
                "Jesteś geniuszem",
                "Jesteś leniwy / z ciebie leń",
                "Idź spać",
                "Kocham cię"
            ],
            "correct": "B",
            "explanation": "„Ty to jesteś leniwy jak nic”.",
            "reference": "leniwy jak nic"
        },
        {
            "question": "Jaką książkę czyta Kamil?",
            "answers": [
                "Harry Potter",
                "Dziki ojciec Szymona Grzelaka",
                "W pustyni i w puszczy",
                "1984"
            ],
            "correct": "B",
            "explanation": "Czyta „Dziki ojciec” Grzelaka o etykietach.",
            "reference": "Dziki ojciec"
        },
        {
            "question": "Co Kamil mówi Adamowi po trójce z kartkówki?",
            "answers": [
                "Zawsze z ciebie był leń",
                "Widzę, że się przygotowałeś — to wytrwałość",
                "Idź do pokoju",
                "Nigdy więcej sportu"
            ],
            "correct": "B",
            "explanation": "Opisowe docenienie wysiłku, nie oceny.",
            "reference": "wytrwałość"
        },
        {
            "question": "Co Adam mówi o „leniu” na końcu?",
            "answers": [
                "Nadal w to wierzy",
                "Wie, że nie jest leniem — czasem brakuje mu motywacji, ale może to zmienić",
                "Nienawidzi taty",
                "Nie chce chodzić do szkoły"
            ],
            "correct": "B",
            "explanation": "Adam: nie jest leniem, czasem brak motywacji — ale może zmienić.",
            "reference": "nie jestem leniem"
        },
        {
            "question": "Jak Kamil reaguje na zepsuty projekt szkolny?",
            "answers": [
                "Krzyknie o nieuważności",
                "Pyta spokojnie co się stało i co Adam może zrobić",
                "Kupuje nowy projekt",
                "Anuluje lekcje"
            ],
            "correct": "B",
            "explanation": "Pyta o rozwiązanie i lekcję na przyszłość.",
            "reference": "Co możesz zrobić"
        }
    ],
    "Jeszcze": [
        {
            "question": "Jak Tomasz poprawia zdanie Julii „nie umiem matematyki”?",
            "answers": [
                "Masz rację",
                "Jeszcze nie umiesz — możesz się nauczyć",
                "Ucz się więcej",
                "Matma jest głupia"
            ],
            "correct": "B",
            "explanation": "Kluczowe słowo „jeszcze” zmienia perspektywę.",
            "reference": "Jeszcze nie umiesz"
        },
        {
            "question": "Które pytanie Tomasz zadaje zamiast „jak było w szkole”?",
            "answers": [
                "Ile masz ocen",
                "Co dziś najbardziej cię zaskoczyło?",
                "Czy dostaniesz dwóję",
                "Kiedy odrabisz lekcje"
            ],
            "correct": "B",
            "explanation": "Pytania o odkrycia i zaskoczenia budzą ciekawość.",
            "reference": "najbardziej cię zaskoczyło"
        },
        {
            "question": "Jak Tomasz używa naleśników?",
            "answers": [
                "Jako nagrodę za oceny",
                "Jako praktyczną matematykę — podwajanie porcji",
                "Nigdy nie gotuje",
                "Jako karę"
            ],
            "correct": "B",
            "explanation": "Julia liczy mąkę i jajka na podwójną porcję.",
            "reference": "podwójną porcję"
        },
        {
            "question": "Co Julia mówi do siebie podczas odrabiania lekcji?",
            "answers": [
                "Nigdy tego nie zrobię",
                "Nie umiem tego jeszcze, ale mogę spróbować",
                "Tato mi pomoże",
                "Nie będę się uczyć"
            ],
            "correct": "B",
            "explanation": "Wewnętrzny monolog z „jeszcze”.",
            "reference": "jeszcze, ale mogę spróbować"
        },
        {
            "question": "Co Julia mówi na końcu o nauce?",
            "answers": [
                "Nigdy więcej szkoły",
                "Chyba lubię się uczyć",
                "Tylko matma jest ok",
                "Tato robi za mnie lekcje"
            ],
            "correct": "B",
            "explanation": "„Chyba lubię się uczyć” — motywacja wewnętrzna.",
            "reference": "lubię się uczyć"
        }
    ],
    "Lista rzeczy, których żałuję": [
        {
            "question": "Ile lat ma Anna?",
            "answers": [
                "32",
                "42",
                "52",
                "38"
            ],
            "correct": "B",
            "explanation": "Tekst: „Anna miała czterdzieści dwa lata”.",
            "reference": "czterdzieści dwa lata"
        },
        {
            "question": "Co Tomek pamięta z dzieciństwa bolesnego dla Anny?",
            "answers": [
                "Tylko prezenty",
                "Że mama często krzyczała i odwołała wyjście do kina",
                "Tylko wakacje",
                "Nic"
            ],
            "correct": "B",
            "explanation": "Tomek wspomina krzyk i odwołane kino.",
            "reference": "odwołać wyjście do kina"
        },
        {
            "question": "Po co Anna pisze listę?",
            "answers": [
                "Dla sąsiadów",
                "By zrozumieć błędy i coś zmienić — nie by się obwiniać",
                "Dla sądu",
                "Dla szkoły"
            ],
            "correct": "B",
            "explanation": "Napisała listę, żeby zrozumieć i zmienić, nie by się obwiniać.",
            "reference": "żeby zrozumieć"
        },
        {
            "question": "Co Tomek robi ze starymi zdjęciami?",
            "answers": [
                "Wyrzuca je",
                "Skanuje i porządkuje album wspomnień",
                "Sprzedaje",
                "Palą"
            ],
            "correct": "B",
            "explanation": "Tomek skanuje zdjęcia z pudła — „nasze wspomnienia”.",
            "reference": "zeskanował"
        },
        {
            "question": "Co Tomek pisze o liście żalów?",
            "answers": [
                "Jest zły",
                "Jest wdzięczny — widać, że mamie zależy i ją kocha",
                "Ignoruje matkę",
                "Chce pieniędzy"
            ],
            "correct": "B",
            "explanation": "Tomek: lista pokazuje, że zależy i kocha — to najważniejsze.",
            "reference": "Jestem wdzięczny"
        }
    ],
    "Bogini i liczby": [
        {
            "question": "Kto jest głównym bohaterem opowieści?",
            "answers": [
                "Isaac Newton",
                "Srinivasa Ramanujan",
                "Albert Einstein",
                "Ada Lovelace"
            ],
            "correct": "B",
            "explanation": "Opowieść śledzi życie Ramanujana.",
            "reference": "Srinivasa Ramanujan"
        },
        {
            "question": "Kto w Cambridge otrzymuje list pełen twierdzeń bez dowodów?",
            "answers": [
                "Littlewood",
                "Hardy",
                "Euler",
                "Gauss"
            ],
            "correct": "B",
            "explanation": "Hardy czyta list od Ramanujana w Trinity College.",
            "reference": "Hardy patrzył na list"
        },
        {
            "question": "Jaką boginię Ramanujan wspomina?",
            "answers": [
                "Lakshmi",
                "Namagiri z Namakkalu",
                "Kali",
                "Saraswati"
            ],
            "correct": "B",
            "explanation": "Matka słyszy we śnie głos bogini Namagiri.",
            "reference": "Namagiri"
        },
        {
            "question": "Ile lat miał Ramanujan, gdy zmarł?",
            "answers": [
                "42",
                "32",
                "22",
                "52"
            ],
            "correct": "B",
            "explanation": "26 kwietnia 1920 — miał 32 lata.",
            "reference": "32 lata"
        },
        {
            "question": "Co Ramanujan mówi o równaniach?",
            "answers": [
                "Muszą być krótkie",
                "Nie mają sensu, jeśli nie wyrażają myśli Boga",
                "Są tylko dla inżynierów",
                "Nie lubi równań"
            ],
            "correct": "B",
            "explanation": "Powtarza: równanie bez sensu, jeśli nie wyraża myśli Boga.",
            "reference": "myśli Boga"
        }
    ]
}

C10_INSPIRATION = {
    "Chór": "Podcast Agi Rogali o zbędnych kłótniach rodzicielskich; opowieść o traumach pokoleń",
    "Dobra dziewczynka": "Motyw perfekcjonizmu i maski „grzecznej dziewczynki” w macierzyństwie",
    "Kij i marchewka": "Koncepcje pozytywnej dyscypliny — konsekwencje zamiast kar",
    "W pełni": "Filozofia Jespera Jula o dziecku kompletnym od urodzenia",
    "Poligon": "Opowieść o przerwaniu cyklu przemocy emocjonalnej w rodzinie",
    "Radio w głowie": "Metafora ADHD jako „radia” z wieloma stacjami naraz",
    "Nowy świat": "Podcast Marii Berlińskiej o dialogu zamiast tresury",
    "Autorytet na przepraszam": "Podcast Marii Berlińskiej o autorytecie przez przepraszanie",
    "Cisza": "Japońskie koncepcje shitsuke, mimamoru i amae w rodzicielstwie",
    "Naczynia połączone": "Metafora rodziny jako naczyń połączonych — system rodzinny",
    "Ułamki": "Podcast Agi Rogali o dzieleniu czynności na kroki",
    "Przedszkole bez ścian": "Alternatywna edukacja przedszkolna przez naturę i projekty",
    "Etykieta": "Książka Szymona Grzelaka „Dziki ojciec” o etykietach",
    "Jeszcze": "Singapurska metoda growth mindset — słowo „jeszcze”",
    "Lista rzeczy, których żałuję": "Refleksja matki dorosłych dzieci nad rodzicielskimi żalami",
    "Bogini i liczby": "Biografia Srinivasy Ramanujana i współpracy z G.H. Hardy"
}

COLLECTION_ELEVEN_RAW = {
    "Święci wojownicy": {
        "manuscript_title": "Święci wojownicy",
        "slug": "swieci-wojownicy",
        "pack_id": "polish_swieci_wojownicy",
        "display_title": "Święci wojownicy",
        "subtitle": "Podcast, rytuały i wojownicy wszystkich kultur",
        "blurb": "Dorosły narrator słucha podcastu o templariuszach, samurajach, wikingach i mudżahedinach — i przypomina sobie medalik z dzieciństwa, dziadka z AK oraz pytanie: czy potrzebujemy wiary w bogów, by walczyć własne wojny?",
        "genres": "philosophy, history, short_story",
        "cover_family": "philosophy",
        "audience": "adult",
        "difficulty": 5,
        "reader_stars": "★★★★☆",
        "trust": "Fiction",
        "tags": "podcast, wojownicy, rytuały, templariusze, Collection Eleven",
        "keywords": "Święci wojownicy, templariusze, samuraje, rytuały, podcast",
        "editorial_notes": "Eseistyczna fikcja inspirowana podcastem Atora i Artura Wójtowicza; odniesienia historyczne (berserkerzy, II wojna światowa, islam) w narracji dorosłego bohatera — nie lekcja historii.",
        "inspiration": "Manuskrypt Collection Eleven; YouTube -vRABYN-UAA (13.07.2026).",
        "philosophy_stars": 4,
        "philosophy_note": "Silna refleksja o sensie, rytuałach i akceptacji — dobry ton AlephBits dla dorosłych; nie dla dzieci.",
        "founder_notes": [
            "Founder note: Treści wojenne i narkotyki w kontekście historycznym — fiction framing.",
            "Founder note: Powiązanie z serią podcastową — rozważyć tag serii."
        ],
        "series": "Collection Eleven",
        "quiz": [
            {
                "question": "Ile lat miał narrator, gdy pierwszy raz usłyszał o templariuszach?",
                "answers": [
                    "Dziesięć",
                    "Dwanaście",
                    "Piętnaście",
                    "Siedem"
                ],
                "correct": "B",
                "explanation": "Tekst mówi: „Kiedy miałem dwanaście lat, pierwszy raz usłyszałem o templariuszach.”",
                "reference": "dwanaście lat"
            },
            {
                "question": "Kogo narrator wspomina jako „świętego wojownika” w sensie ludzkim?",
                "answers": [
                    "Ojca",
                    "Dziadka z AK",
                    "Artura Wójtowicza",
                    "Atora"
                ],
                "correct": "B",
                "explanation": "Dziadek był żołnierzem Armii Krajowej i znalazł spokój w akceptacji przeszłości.",
                "reference": "dziadek"
            },
            {
                "question": "Co narrator nosił jako dziecko?",
                "answers": [
                    "Medalik z Matką Boską",
                    "Czerwony krzyż",
                    "Amulet samurajski",
                    "Order"
                ],
                "correct": "A",
                "explanation": "Wspomina medalik z Matką Boską, w który wierzył jako dziecko.",
                "reference": "medalik"
            },
            {
                "question": "Jaki wniosek wyciąga narrator na końcu?",
                "answers": [
                    "Trzeba wrócić do religii",
                    "Może wystarczy wiara w siebie i nadanie życiu sensu",
                    "Wojna jest zawsze słuszna",
                    "Rytuały są bezużyteczne"
                ],
                "correct": "B",
                "explanation": "Kończy myślą, że może nie potrzebujemy wiary w bogów — wystarczy wiara w siebie.",
                "reference": "wiara w siebie"
            },
            {
                "question": "Gdzie siedzi narrator podczas słuchania podcastu?",
                "answers": [
                    "W warszawskim mieszkaniu",
                    "W Krakowie",
                    "W Poznaniu",
                    "Na wsi u dziadka"
                ],
                "correct": "A",
                "explanation": "Opowieść zaczyna się od „siedzę w swoim warszawskim mieszkaniu”.",
                "reference": "warszawskim mieszkaniu"
            }
        ],
        "motifs": [
            "warrior",
            "faith",
            "ritual",
            "memory",
            "mentor",
            "question"
        ]
    },
    "Klucz babci Rózi": {
        "manuscript_title": "Klucz babci Rózi",
        "slug": "klucz-babci-rozi",
        "pack_id": "polish_klucz_babci_rozi",
        "display_title": "Klucz babci Rózi",
        "subtitle": "Susza, trzy domki i Królowa Deszczu",
        "blurb": "Dziesięcioletnia Lena wędruje przez zaczarowaną krainę za srebrnym kluczem, by prosić Królową Deszczu o deszcz dla wyschniętego gospodarstwa — i odkrywa, że jej babci Rózi skrywa własną magiczną przeszłość.",
        "genres": "fairy_tale, short_story",
        "cover_family": "legends",
        "audience": "children_8_12",
        "difficulty": 2,
        "reader_stars": "★★★★☆",
        "trust": "Fiction",
        "tags": "bajka, susza, magia, babcia, Collection Eleven",
        "keywords": "Klucz babci Rózi, Królowa Deszczu, Lena, bajka",
        "editorial_notes": "Klasyczna bajka o trzech domkach i zagadkach; końcówka ujawnia, że babcia była Królową Wiatru.",
        "inspiration": "Manuskrypt Collection Eleven; YouTube 55rrx4XtY8g (06.01.2022).",
        "philosophy_stars": 4,
        "philosophy_note": "Ciepła opowieść o odwadze, rodzinie i pomocy innym — mocny kandydat na półkę dziecięcą.",
        "founder_notes": [
            "Founder note: Near-duplicate z „Klucz do deszczowej krainy” — ta sama ścieżka fabuły i ten sam YouTube; rozważyć jedną wersję na półce."
        ],
        "series": "Collection Eleven",
        "quiz": [
            {
                "question": "Ile lat ma Lena?",
                "answers": [
                    "Osiem",
                    "Dziesięć",
                    "Dwanaście",
                    "Siedem"
                ],
                "correct": "B",
                "explanation": "Tekst: „Lena miała dziesięć lat”.",
                "reference": "dziesięć lat"
            },
            {
                "question": "Co otwiera drzwi do zaczarowanej krainy?",
                "answers": [
                    "Srebrny klucz",
                    "Złota moneta",
                    "Mapa",
                    "Piosenka bez klucza"
                ],
                "correct": "A",
                "explanation": "Babcia wyciąga srebrny klucz ze szuflady fartucha.",
                "reference": "srebrny klucz"
            },
            {
                "question": "Kim okazuje się babcia Rózia na końcu?",
                "answers": [
                    "Królową Wiatru",
                    "Królową Deszczu",
                    "Ciotką Stellą",
                    "Śnieżynką"
                ],
                "correct": "A",
                "explanation": "Mówi: „Kiedyś byłam Królową Wiatru”.",
                "reference": "Królową Wiatru"
            },
            {
                "question": "Jaką piosenkę Lena śpiewa, by otworzyć drzwi?",
                "answers": [
                    "Kap, kap, kap, otwórz proszę drzwi…",
                    "Deszczu spłyń na tę ziemię",
                    "Kukuryku",
                    "Muuu"
                ],
                "correct": "A",
                "explanation": "Babcia uczy piosenki zaczynającej się od „Kap, kap, kap…”.",
                "reference": "Kap, kap, kap"
            },
            {
                "question": "Co Lena robi, by uratować suknię Królowej Kropei?",
                "answers": [
                    "Gra na flecie",
                    "Tańczy",
                    "Śpiewa o deszczu",
                    "Podlewa kwiaty"
                ],
                "correct": "A",
                "explanation": "Lena gra melodię na flecie, by odmrozić suknię z kropli.",
                "reference": "flet"
            }
        ],
        "motifs": [
            "key",
            "rain",
            "journey",
            "grandmother",
            "courage",
            "wonder"
        ]
    },
    "Cudaczek-Wyśmiewaczek": {
        "manuscript_title": "Cudaczek-Wyśmiewaczek",
        "slug": "cudaczek-wysmiewaczek",
        "pack_id": "polish_cudaczek_wysmiewaczek",
        "display_title": "Cudaczek-Wyśmiewaczek",
        "subtitle": "Panna Obrażalska i licho od śmiechu",
        "blurb": "Ośmioletnia dziewczynka, którą wszyscy nazywają Panną Obrażalską, żyje w symbiozie z lichutkim Cudaczkiem-Wyśmiewaczkiem — dopóki staruszek nie każe jej przez trzy dni ani razu się nie obrazić.",
        "genres": "fairy_tale, short_story",
        "cover_family": "legends",
        "audience": "children_8_12",
        "difficulty": 2,
        "reader_stars": "★★★★☆",
        "trust": "Fiction",
        "tags": "obrazki, charakter, szkoła, Collection Eleven",
        "keywords": "Cudaczek-Wyśmiewaczek, Panna Obrażalska, licho",
        "editorial_notes": "Bajka moralna o przemianie postawy; humorystyczny ton, bez przemocy.",
        "inspiration": "Manuskrypt Collection Eleven; YouTube Xe3B8tGjKXE (10.04.2019).",
        "philosophy_stars": 4,
        "philosophy_note": "Prosta, skuteczna opowieść o emocjach i współpracy — dobra dla młodszych czytelników.",
        "founder_notes": [],
        "series": "Collection Eleven",
        "quiz": [
            {
                "question": "Czym żywi się Cudaczek-Wyśmiewaczek?",
                "answers": [
                    "Śmiechem",
                    "Chlebem",
                    "Mlekiem",
                    "Owocami"
                ],
                "correct": "A",
                "explanation": "Licho „żywiło się tylko śmiechem”.",
                "reference": "śmiechem"
            },
            {
                "question": "Jaką radę daje staruszek?",
                "answers": [
                    "Przez trzy dni ani razu się nie obraź",
                    "Nie chodź do szkoły",
                    "Wyprowadź się na stałe",
                    "Zjedz więcej grochówki"
                ],
                "correct": "A",
                "explanation": "Staruszek każe wytrzymać trzy dni bez obrażania się.",
                "reference": "trzy dni"
            },
            {
                "question": "Gdzie mieszka Cudaczek?",
                "answers": [
                    "W jasnych warkoczykach dziewczynki",
                    "W piwnicy",
                    "W szafie",
                    "W kominie"
                ],
                "correct": "A",
                "explanation": "Mieszka w warkoczykach Panny Obrażalskiej.",
                "reference": "warkoczykach"
            },
            {
                "question": "Co dziewczynka wiąże na ręce na pamiątkę?",
                "answers": [
                    "Niebieską tasiemkę",
                    "Czerwoną wstążkę",
                    "Sznurek",
                    "Bransoletkę"
                ],
                "correct": "A",
                "explanation": "Zawiązuje niebieską tasiemkę po radzie staruszka.",
                "reference": "niebieską tasiemkę"
            },
            {
                "question": "Co dzieje się z Cudaczkiem po trzecim dniu?",
                "answers": [
                    "Słabnie i ucieka z domu",
                    "Rośnie w siłę",
                    "Zamienia się w psa",
                    "Zostaje na zawsze"
                ],
                "correct": "A",
                "explanation": "Po trzecim dniu Cudaczek słabnie i wychodzi z domu.",
                "reference": "ucieknie gdzie pieprz rośnie"
            }
        ],
        "motifs": [
            "childhood",
            "anger",
            "forgiveness",
            "home",
            "teaching",
            "companionship"
        ]
    },
    "Kapuściana tajemnica": {
        "manuscript_title": "Kapuściana tajemnica",
        "slug": "kapusciana-tajemnica",
        "pack_id": "polish_kapusciana_tajemnica",
        "display_title": "Kapuściana tajemnica",
        "subtitle": "Nudna babcia i mapa do skarbów",
        "blurb": "Jedenastoletni Kacper nudzi się u babci i jej kapuśniaka — dopóki nie odkryje, że starsza pani z kryminałów i zupy to dawna poszukiwaczka skarbów z młodości pełnej pościgów.",
        "genres": "adventure, short_story",
        "cover_family": "legends",
        "audience": "children_8_12",
        "difficulty": 3,
        "reader_stars": "★★★★☆",
        "trust": "Fiction",
        "tags": "babcia, tajemnica, czytanie, Collection Eleven",
        "keywords": "Kapuściana tajemnica, Kacper, babcia, skarb",
        "editorial_notes": "Motyw trudności w czytaniu (Kacper zostaje na drugi rok) — pozytywnie; wątek gangsterski w przeszłości babci jako tło, nie przemoc na pierwszym planie.",
        "inspiration": "Manuskrypt Collection Eleven; YouTube DoKNiN4QpYI (08.09.2015).",
        "philosophy_stars": 4,
        "philosophy_note": "Ciepła opowieść o patrzeniu ponad stereotypy i wspólne czytanie.",
        "founder_notes": [
            "Founder note: Delikatny wątek trudności szkolnych / czytania — pozytywnie ujęty."
        ],
        "series": "Collection Eleven",
        "quiz": [
            {
                "question": "Ile lat ma Kacper?",
                "answers": [
                    "Dziewięć",
                    "Jedenastu",
                    "Trzynaście",
                    "Osiem"
                ],
                "correct": "B",
                "explanation": "Tekst: „Kacper miał jedenaście lat”.",
                "reference": "jedenaście lat"
            },
            {
                "question": "Jakie ciasto podaje babcia po zupie?",
                "answers": [
                    "Kapuściane",
                    "Jabłkowe",
                    "Marchewkowe",
                    "Miodowe"
                ],
                "correct": "A",
                "explanation": "Po zupie nadeszła kolej na kapuściane ciasto.",
                "reference": "Kapuściane"
            },
            {
                "question": "Jaką książkę babcia nazywa ulubioną?",
                "answers": [
                    "Wielki skarb",
                    "Harry Potter",
                    "Pinokio",
                    "Robinson"
                ],
                "correct": "A",
                "explanation": "Mówi o „Wielkim skarbie” — o chłopcu i mapach w piwnicy.",
                "reference": "Wielki skarb"
            },
            {
                "question": "Co Kacper odkrywa za obrazkiem?",
                "answers": [
                    "Srebrny kluczyk",
                    "Złoto",
                    "Pistolet",
                    "List"
                ],
                "correct": "A",
                "explanation": "Babcia wyjmuje mały srebrny kluczyk spod obrazka.",
                "reference": "srebrny kluczyk"
            },
            {
                "question": "Dlaczego babcia i dziadek przestali rabować?",
                "answers": [
                    "Dla bezpieczeństwa rodziny",
                    "Bo stracili mapę",
                    "Bo poszli do więzienia",
                    "Bo nie lubili skarbów"
                ],
                "correct": "A",
                "explanation": "Mówi: „Dla was. Dla rodziny. Dla waszego bezpieczeństwa.”",
                "reference": "Dla rodziny"
            }
        ],
        "motifs": [
            "grandmother",
            "secret",
            "discovery",
            "reading",
            "adventure",
            "treasure"
        ]
    },
    "Złoto i zwykłe szczęście": {
        "manuscript_title": "Złoto i zwykłe szczęście",
        "slug": "zloto-i-zwykle-szczescie",
        "pack_id": "polish_zloto_i_zwykle_szczescie",
        "display_title": "Złoto i zwykłe szczęście",
        "subtitle": "Legenda o złotej kaczce i szewczyku Lutku",
        "blurb": "Biedny praktykant Lutek w noc świętojańską odnajduje w lochach Zamku Ostrogskich zaklętą królewnę-kaczkę — lecz prawdziwe bogactwo okazuje się nie w sakiewce, lecz w jednym geście wobec głodnego starca.",
        "genres": "fairy_tale, legends, short_story",
        "cover_family": "legends",
        "audience": "children_8_12",
        "difficulty": 3,
        "reader_stars": "★★★★☆",
        "trust": "Fiction",
        "tags": "legenda warszawska, szewc, hojność, Collection Eleven",
        "keywords": "Złoto i zwykłe szczęście, Zamek Ostrogskich, Lutek, legenda",
        "editorial_notes": "Klasyczna baśń z morałem; odniesienia do Kilińskiego i Starówki jako tło kulturowe.",
        "inspiration": "Manuskrypt Collection Eleven; YouTube WFOCPSWVVvE (17.03.2019).",
        "philosophy_stars": 4,
        "philosophy_note": "Uniwersalna opowieść o hojności vs chciwości — mocny materiał edukacyjno-moralny.",
        "founder_notes": [],
        "series": "Collection Eleven",
        "quiz": [
            {
                "question": "Kiedy można znaleźć królewnę według legendy?",
                "answers": [
                    "W noc świętojańską",
                    "W Wigilię",
                    "W noc andrzejkową",
                    "W każdą noc"
                ],
                "correct": "A",
                "explanation": "Legenda mówi, że można tego dokonać tylko w noc świętojańską.",
                "reference": "noc świętojańską"
            },
            {
                "question": "Ile dukatów dostaje Lutek od królewny?",
                "answers": [
                    "Sto",
                    "Pięćdziesiąt",
                    "Dziesięć",
                    "Tysiąc"
                ],
                "correct": "A",
                "explanation": "Królewna daje mu sakiewkę ze stu dukatami.",
                "reference": "stu dukatami"
            },
            {
                "question": "Na co Lutek ostatecznie wydaje pieniądze?",
                "answers": [
                    "Daje je głodnemu staruszkowi",
                    "Kupuje pałac",
                    "Gra w karty do rana",
                    "Chowa pod podłogą"
                ],
                "correct": "A",
                "explanation": "Wysypuje pozostałe dukaty staruszkowi-inwalidzie.",
                "reference": "staruszka"
            },
            {
                "question": "Kim zostaje Lutek na końcu opowieści?",
                "answers": [
                    "Majstrem szewskim z własnym warsztatem",
                    "Królem",
                    "Kupcem",
                    "Żołnierzem"
                ],
                "correct": "A",
                "explanation": "Wkrótce Lutek zostaje majstrem i otwiera własny warsztat.",
                "reference": "majstrem"
            },
            {
                "question": "Gdzie znajduje się legenda o kaczce?",
                "answers": [
                    "W lochach Zamku Ostrogskich na Tamce",
                    "W Wawelu",
                    "Na Woli",
                    "W Łazienkach"
                ],
                "correct": "A",
                "explanation": "Szewcy mówią o lochach Zamku Ostrogskich na Tamce.",
                "reference": "Zamek Ostrogskich"
            }
        ],
        "motifs": [
            "gold",
            "generosity",
            "legend",
            "home",
            "shame",
            "gratitude"
        ]
    },
    "Ciekawska Zosia i skarb przyjaźni": {
        "manuscript_title": "Ciekawska Zosia i skarb przyjaźni",
        "slug": "ciekawska-zosia-i-skarb-przyjazni",
        "pack_id": "polish_ciekawska_zosia_i_skarb_przyjazni",
        "display_title": "Ciekawska Zosia i skarb przyjaźni",
        "subtitle": "Ciekawość, obietnica i suszone kwiaty",
        "blurb": "Zosia nie potrafi powstrzymać ciekawości — aż wnuczka u babci na wsi łamie obietnicę, puszcza mysz z kredensu i uczy się, że prawdziwy skarb to panowanie nad ciekawością i dzielenie się pięknem natury.",
        "genres": "fairy_tale, short_story",
        "cover_family": "nature",
        "audience": "children_8_12",
        "difficulty": 2,
        "reader_stars": "★★★★☆",
        "trust": "Fiction",
        "tags": "ciekawość, babcia, natura, Collection Eleven",
        "keywords": "Ciekawska Zosia, skarb przyjaźni, ciekawość",
        "editorial_notes": "Morał o ciekawości bez moralizowania; pozytywne zakończenie z pasją botaniczną.",
        "inspiration": "Manuskrypt Collection Eleven; YouTube gGZ7a47-rW4 (21.03.2016).",
        "philosophy_stars": 4,
        "philosophy_note": "Dobra opowieść o samokontroli i przekierowaniu ciekawości — AlephBits-friendly.",
        "founder_notes": [],
        "series": "Collection Eleven",
        "quiz": [
            {
                "question": "Co wyskakuje z kredensu, gdy Zosia go otwiera?",
                "answers": [
                    "Biała mysz",
                    "Kot",
                    "Motyl",
                    "Pająk"
                ],
                "correct": "A",
                "explanation": "Z kredensu wyskakuje biała mysz.",
                "reference": "biała mysz"
            },
            {
                "question": "Co obiecuje babcia dać Zosi, gdy przestanie być zbyt ciekawska?",
                "answers": [
                    "Zabawki z kredensu",
                    "Konie",
                    "Telefon",
                    "Pieniądze"
                ],
                "correct": "A",
                "explanation": "W kredensie stoją lalka, pajac, wózek i piłka.",
                "reference": "zabawki"
            },
            {
                "question": "Jaką nową pasję odkrywa Zosia?",
                "answers": [
                    "Suszenie kwiatów i roślin",
                    "Grę w piłkę",
                    "Gotowanie",
                    "Tańce"
                ],
                "correct": "A",
                "explanation": "Zaczyna suszyć kwiaty i robić z nich prezenty.",
                "reference": "suszenie kwiatów"
            },
            {
                "question": "Co łapie Zosi za palec w koszyku?",
                "answers": [
                    "Rak",
                    "Krab",
                    "Ryba",
                    "Żaba"
                ],
                "correct": "A",
                "explanation": "Rak schowany w koszyku chwyta ją za palec.",
                "reference": "rak"
            },
            {
                "question": "Jaki wniosek wyciąga babcia w liście?",
                "answers": [
                    "Ciekawość jest dobra, gdy nie łamie obietnic i nie krzywdzi",
                    "Ciekawość jest zawsze zła",
                    "Nigdy nie wolno dotykać niczego",
                    "Zabawki są najważniejsze"
                ],
                "correct": "A",
                "explanation": "Babcia pisze, że ciekawość jest dobra, gdy nie krzywdzi i nie łamie obietnic.",
                "reference": "nie krzywdzi innych"
            }
        ],
        "motifs": [
            "curiosity",
            "childhood",
            "forgiveness",
            "nature",
            "grandmother",
            "discovery"
        ]
    },
    "Koziołek Matołek i podróż do Pacanowa": {
        "manuscript_title": "Koziołek Matołek i podróż do Pacanowa",
        "slug": "koziolek-matolek-i-podroz-do-pacanowa",
        "pack_id": "polish_koziolek_matolek_i_podroz_do_pacanowa",
        "display_title": "Koziołek Matołek i podróż do Pacanowa",
        "subtitle": "Skrócona podróż najsłynniejszego koziołka",
        "blurb": "Koziołek Matołek rusza do Pacanowa po podkowy — i przez więzienie, czarownicę, utratę brody i podróż aż na Księżyc odkrywa, że najlepiej jest w domu, wśród swoich.",
        "genres": "fairy_tale, short_story",
        "cover_family": "legends",
        "audience": "children_8_12",
        "difficulty": 3,
        "reader_stars": "★★★☆☆",
        "trust": "Fiction",
        "tags": "Koziołek Matołek, Pacanów, klasyka, Collection Eleven",
        "keywords": "Koziołek Matołek, Pacanów, Kornel Makuszyński",
        "editorial_notes": "Skondensowane streszczenie klasyki Makuszyńskiego; niektóre epizody (ścięcie brody, czarownica) mogą być intensywne dla najmłodszych.",
        "inspiration": "Manuskrypt Collection Eleven; YouTube C18gZmTbHh4 (26.01.2024); postać z twórczości Kornela Makuszyńskiego.",
        "philosophy_stars": 3,
        "philosophy_note": "Przyjemna abridżacja klasyki, lecz bardzo skrótowa — słabsza niż pełne opowiadania Makuszyńskiego.",
        "founder_notes": [
            "Founder note: Prawa autorskie — postać public domain / klasyka; sprawdzić status Makuszyńskiego w katalogu.",
            "Founder note: Epizody strachu (czarownica, więzienie) — rozważyć age note."
        ],
        "series": "Collection Eleven",
        "quiz": [
            {
                "question": "Dokąd Matołek chce dotrzeć na początku?",
                "answers": [
                    "Do Pacanowa",
                    "Do Warszawy",
                    "Do Afryki",
                    "Na Księżyc"
                ],
                "correct": "A",
                "explanation": "Rusza do Pacanowa, by założyć podkowy.",
                "reference": "Pacanowie"
            },
            {
                "question": "Kogo spotyka Matołek na Księżycu?",
                "answers": [
                    "Pana Twardowskiego",
                    "Smoka",
                    "Króla",
                    "Czarownicę"
                ],
                "correct": "A",
                "explanation": "Na Księżycu spotyka pana Twardowskiego.",
                "reference": "pana Twardowskiego"
            },
            {
                "question": "Co traci Matołek w mieście z dziwnym prawem?",
                "answers": [
                    "Broda",
                    "Podkowy",
                    "Tobołek",
                    "Nogi"
                ],
                "correct": "A",
                "explanation": "W mieście, gdzie brodacze muszą ją stracić, ścinają mu brodę.",
                "reference": "brodę"
            },
            {
                "question": "Gdzie Matołek ostatecznie zostaje?",
                "answers": [
                    "W Polsce wśród swoich",
                    "W Pacanowie na stałe",
                    "W Afryce jako król",
                    "Na Księżycu"
                ],
                "correct": "A",
                "explanation": "Mówi: „Zostanę! Już nigdy nie opuszczę Polski.”",
                "reference": "wśród swoich"
            },
            {
                "question": "Kto przyszywa Matołkowi głowę po utracie brody?",
                "answers": [
                    "Szewc",
                    "Czarownica",
                    "Księżniczka",
                    "Kowal"
                ],
                "correct": "A",
                "explanation": "Poczciwy szewc przyszywa mu głowę do tułowia.",
                "reference": "szewc"
            }
        ],
        "motifs": [
            "journey",
            "home",
            "courage",
            "discovery",
            "fear",
            "companionship"
        ]
    },
    "Nowy ogród": {
        "manuscript_title": "Nowy ogród",
        "slug": "nowy-ogrod",
        "pack_id": "polish_nowy_ogrod",
        "display_title": "Nowy ogród",
        "subtitle": "Myszka Terka, susza i ślimak-wynalazca",
        "blurb": "Myszka Terka walczy o uratowanie pola kukurydzy w suszy — dopóki tajemniczy ślimak Tygrys nie wyjaśnia, że drzewa na skraju pola mogą zatrzymać wodę lepiej niż sama kukurydza.",
        "genres": "nature, short_story",
        "cover_family": "nature",
        "audience": "children_8_12",
        "difficulty": 2,
        "reader_stars": "★★★★☆",
        "trust": "Fiction",
        "tags": "ekologia, susza, ogrodnictwo, Collection Eleven",
        "keywords": "Nowy ogród, Terka, Tygrys, susza",
        "editorial_notes": "Opowieść edukacyjna o roli drzew i retencji wody; postacie zwierzęce.",
        "inspiration": "Manuskrypt Collection Eleven; YouTube SdQAa0A4XvA (23.07.2019).",
        "philosophy_stars": 4,
        "philosophy_note": "Delikatna ekologia i współpraca — dobry materiał dla dzieci.",
        "founder_notes": [],
        "series": "Collection Eleven",
        "quiz": [
            {
                "question": "Co uprawia Terka?",
                "answers": [
                    "Kukurydzę",
                    "Pszenicę",
                    "Truskawki",
                    "Winogrona"
                ],
                "correct": "A",
                "explanation": "Terka dba o swoje pole kukurydzy.",
                "reference": "kukurydzy"
            },
            {
                "question": "Kim jest Tygrys?",
                "answers": [
                    "Ślimakiem-wynalazcą",
                    "Kotem",
                    "Potworem",
                    "Krową"
                ],
                "correct": "A",
                "explanation": "Tygrys przedstawia się jako ślimak i wynalazca.",
                "reference": "ślimak"
            },
            {
                "question": "Po co Tygrys kopie doły na skraju pola?",
                "answers": [
                    "By posadzić drzewa zatrzymujące wodę",
                    "By zniszczyć kukurydzę",
                    "By szukać skarbów",
                    "By zrobić basen"
                ],
                "correct": "A",
                "explanation": "Wyjaśnia, że korzenie drzew pomagają zatrzymać wodę w glebie.",
                "reference": "drzewa"
            },
            {
                "question": "Jak nazywają się przyjaciele Terki?",
                "answers": [
                    "Tola i Urwis",
                    "Burek i Azor",
                    "Filek i Milek",
                    "Hania i Basia"
                ],
                "correct": "A",
                "explanation": "Tola (kotka) i Urwis (piesek) pomagają Terce.",
                "reference": "Tola i Urwis"
            },
            {
                "question": "Co się dzieje po pierwszej burzy?",
                "answers": [
                    "Ziemia wilgotnieje, kukurydza odżywa",
                    "Pole zostaje zalane i zniszczone",
                    "Terka wyjeżdża z wsi",
                    "Tygrys znika na zawsze"
                ],
                "correct": "A",
                "explanation": "Deszcz zatrzymuje się w glebie dzięki drzewom, kukurydza wygląda lepiej.",
                "reference": "wilgotna ziemia"
            }
        ],
        "motifs": [
            "garden",
            "nature",
            "drought",
            "community",
            "discovery",
            "teaching"
        ]
    },
    "Ciche serce dzwonka": {
        "manuscript_title": "Ciche serce dzwonka",
        "slug": "ciche-serce-dzwonka",
        "pack_id": "polish_ciche_serce_dzwonka",
        "display_title": "Ciche serce dzwonka",
        "subtitle": "Gdy głośny dźwięk nie jest potrzebny",
        "blurb": "Złoty Dzwonek w sklepiku z instrumentami wstydzi się, że dzwoni tylko szeptem — dopóki wiolonczela i mała dziewczynka nie pokażą mu, że cisza też może być piękna.",
        "genres": "fairy_tale, short_story",
        "cover_family": "short_story",
        "audience": "children_8_12",
        "difficulty": 2,
        "reader_stars": "★★★★☆",
        "trust": "Fiction",
        "tags": "muzyka, pewność siebie, Collection Eleven",
        "keywords": "Ciche serce dzwonka, Złoty Dzwonek, instrumenty",
        "editorial_notes": "Allegoria o akceptacji siebie; delikatny ton, bez konfliktu.",
        "inspiration": "Manuskrypt Collection Eleven; YouTube RXdgMlRqr-E (02.02.2022).",
        "philosophy_stars": 4,
        "philosophy_note": "Prosta, ciepła opowieść o samoaceptacji — idealna dla młodszych.",
        "founder_notes": [],
        "series": "Collection Eleven",
        "quiz": [
            {
                "question": "Czym różni się Złoty Dzwonek od innych instrumentów?",
                "answers": [
                    "Dzwoni bardzo cicho",
                    "Nie ma dzwonka",
                    "Jest największy",
                    "Nie lubi muzyki"
                ],
                "correct": "A",
                "explanation": "Jego dźwięk jest cichutki jak szept.",
                "reference": "cichutki"
            },
            {
                "question": "Co mówi wiolonczela o szeptach?",
                "answers": [
                    "Że też mają znaczenie",
                    "Że są bezużyteczne",
                    "Że trzeba krzyczeć",
                    "Że dzwonek jest zepsuty"
                ],
                "correct": "A",
                "explanation": "Wiolonczela mówi, że szepty też mają znaczenie.",
                "reference": "Szepty też mają znaczenie"
            },
            {
                "question": "Kto kupuje dzwonek?",
                "answers": [
                    "Mała dziewczynka",
                    "Pan sklepikarz",
                    "Nauczyciel",
                    "Staruszek"
                ],
                "correct": "A",
                "explanation": "Dziewczynka słyszy jego cichy dźwięk i go kupuje.",
                "reference": "dziewczynka"
            },
            {
                "question": "Gdzie dziewczynka wiesza dzwonek?",
                "answers": [
                    "Na oknie w pokoju",
                    "W piwnicy",
                    "Na dachu",
                    "W szkole"
                ],
                "correct": "A",
                "explanation": "Powiesiła go na oknie, gdzie wieje wietrzyk.",
                "reference": "na oknie"
            },
            {
                "question": "Jaki wniosek wyciąga dzwonek?",
                "answers": [
                    "Nie musi być głośny, by być ważny",
                    "Musi grać jak bęben",
                    "Powinien się chować",
                    "Cisza jest zła"
                ],
                "correct": "A",
                "explanation": "Rozumie, że jego cichy dźwięk jest wyjątkowy i ważny.",
                "reference": "nie musi być głośny"
            }
        ],
        "motifs": [
            "music",
            "silence",
            "self_acceptance",
            "discovery",
            "home",
            "wonder"
        ]
    },
    "Głos i cisza": {
        "manuscript_title": "Głos i cisza",
        "slug": "glos-i-cisza",
        "pack_id": "polish_glos_i_cisza",
        "display_title": "Głos i cisza",
        "subtitle": "Syrenka, która oddała głos za miłość",
        "blurb": "Marina, najmłodsza córka Króla Mórz, ratuje tonącego księcia i oddaje głos wiedźmie, by zostać człowiekiem — lecz prawdziwa miłość okazuje się dawaniem, nie posiadaniem.",
        "genres": "fairy_tale, short_story",
        "cover_family": "legends",
        "audience": "children_8_12",
        "difficulty": 3,
        "reader_stars": "★★★★☆",
        "trust": "Fiction",
        "tags": "syrenka, baśń, miłość, Collection Eleven",
        "keywords": "Głos i cisza, Marina, syrenka, baśń",
        "editorial_notes": "Adaptacja motywu Małej Syrenki (Andersen); wątek ofiary i noża — klasyczna baśń, nie graficzna przemoc.",
        "inspiration": "Manuskrypt Collection Eleven; YouTube VubCpPqFNPM (21.03.2016).",
        "philosophy_stars": 4,
        "philosophy_note": "Uniwersalna baśń o bezinteresownej miłości — mocny materiał z znanym motywem.",
        "founder_notes": [
            "Founder note: Wątek noża i ofiary — rozważyć age note dla 8–9 lat."
        ],
        "series": "Collection Eleven",
        "quiz": [
            {
                "question": "Jak ma na imię syrenka?",
                "answers": [
                    "Marina",
                    "Ariel",
                    "Kropeia",
                    "Zosia"
                ],
                "correct": "A",
                "explanation": "Najmłodsza córka Króla Mórz nazywa się Marina.",
                "reference": "Marina"
            },
            {
                "question": "Co Marina oddaje wiedźmie?",
                "answers": [
                    "Głos",
                    "Ogon",
                    "Korona",
                    "Perły"
                ],
                "correct": "A",
                "explanation": "Wiedźma każe oddać piękny głos za napój zmieniający ogon w nogi.",
                "reference": "głos"
            },
            {
                "question": "Kogo Marina ratuje podczas burzy?",
                "answers": [
                    "Księcia",
                    "Króla",
                    "Rybaka",
                    "Kapitana"
                ],
                "correct": "A",
                "explanation": "Ratuje tonącego księcia i wynosi na brzeg.",
                "reference": "księcia"
            },
            {
                "question": "Czego Marina nie robi z nożem?",
                "answers": [
                    "Nie zabija księcia",
                    "Zabija wiedźmę",
                    "Rzuca w siostry",
                    "Niszczy statek"
                ],
                "correct": "A",
                "explanation": "Bierze nóż, lecz nie zabija śpiącego księcia — cisnęła go w fale.",
                "reference": "nie może tego zrobić"
            },
            {
                "question": "Kim Marina zostaje na końcu?",
                "answers": [
                    "Córką powietrza",
                    "Królową mórz",
                    "Człowiekiem z duszą od razu",
                    "Pianą na zawsze"
                ],
                "correct": "A",
                "explanation": "Staje się córką powietrza — może zdobyć duszę czyniąc dobro.",
                "reference": "córką powietrza"
            }
        ],
        "motifs": [
            "ocean",
            "voice",
            "sacrifice",
            "love",
            "transformation",
            "dream"
        ]
    },
    "Franek i mały Karolek": {
        "manuscript_title": "Franek i mały Karolek",
        "slug": "franek-i-maly-karolek",
        "pack_id": "polish_franek_i_maly_karolek",
        "display_title": "Franek i mały Karolek",
        "subtitle": "Urwis, który został bratem",
        "blurb": "Dziesięcioletni urwis Franek ze starej kamienicy prosi rodziców, by wzięli osierocony Karolek — i odkrywa, że miłość do małego brata może zmienić nawet największego psotnika.",
        "genres": "short_story",
        "cover_family": "everyday_live",
        "audience": "children_8_12",
        "difficulty": 2,
        "reader_stars": "★★★★★",
        "trust": "Fiction",
        "tags": "rodzeństwo, odpowiedzialność, czytanie, Collection Eleven",
        "keywords": "Franek, Karolek, brat, kamienica",
        "editorial_notes": "Wątek śmierci matki Karolka — delikatnie ujęty; mocny motyw nauki czytania dla brata.",
        "inspiration": "Manuskrypt Collection Eleven; YouTube LdKDbVor0Qk (18.12.2015).",
        "philosophy_stars": 5,
        "philosophy_note": "Wzorcowa opowieść AlephBits o odpowiedzialności, czytaniu i przemianie — najsilniejsza w kolekcji.",
        "founder_notes": [
            "Founder note: Wątek śmierci matki — fiction framing; rozważyć age note 8+."
        ],
        "series": "Collection Eleven",
        "quiz": [
            {
                "question": "Ile lat ma Franek?",
                "answers": [
                    "Siedem",
                    "Dziesięć",
                    "Dwanaście",
                    "Osiem"
                ],
                "correct": "B",
                "explanation": "Tekst: „Franek miał dziesięć lat”.",
                "reference": "dziesięć lat"
            },
            {
                "question": "Co Franek obiecuje, gdy prosi o Karolka?",
                "answers": [
                    "Że nigdy więcej nie zrobi figla",
                    "Że wyjedzie z domu",
                    "Że przestanie chodzić do szkoły",
                    "Że odda wszystkie zabawki"
                ],
                "correct": "A",
                "explanation": "Przysięga, że już nigdy nie zrobi żadnego figla.",
                "reference": "nie zrobię żadnego figla"
            },
            {
                "question": "Kogo Franek prosi, by nauczył go czytać?",
                "answers": [
                    "Tatę",
                    "Pannę Gertrudę",
                    "Pani Gienię",
                    "Nauczyciela"
                ],
                "correct": "A",
                "explanation": "Prosi tatę o naukę czytania dla Karolka.",
                "reference": "Nauczysz mnie?"
            },
            {
                "question": "Co Franek czyta Karolkowi wieczorami?",
                "answers": [
                    "Książki o przyrodzie i przyjaźni",
                    "Gazety",
                    "Komiks grozy",
                    "Mapy"
                ],
                "correct": "A",
                "explanation": "Czyta o wiewiórkach, kasztanach, jesiennych liściach, przyjaźni.",
                "reference": "wiewiórkach"
            },
            {
                "question": "Jak zmienia się Franek w oczach sąsiadów?",
                "answers": [
                    "Z „urwisa” w szanowanego chłopca",
                    "Znika z kamienicy",
                    "Zostaje dorosłym",
                    "Nic się nie zmienia"
                ],
                "correct": "A",
                "explanation": "Mówią o nim „Franek”, a nie „Franek łobuz”.",
                "reference": "Franek łobuz"
            }
        ],
        "motifs": [
            "brotherhood",
            "reading",
            "home",
            "responsibility",
            "forgiveness",
            "community"
        ]
    },
    "Klucz do deszczowej krainy": {
        "manuscript_title": "Klucz do deszczowej krainy",
        "slug": "klucz-do-deszczowej-krainy",
        "pack_id": "polish_klucz_do_deszczowej_krainy",
        "display_title": "Klucz do deszczowej krainy",
        "subtitle": "Zosia, babcia i zamek Kropei",
        "blurb": "Dziewięcioletnia Zosia przechodzi przez trzy magiczne krainy z kluczykiem babci, by obudzić zamrożoną Królową Deszczu Kropeię i uratować wyschnięty ogród mamy.",
        "genres": "fairy_tale, short_story",
        "cover_family": "legends",
        "audience": "children_8_12",
        "difficulty": 2,
        "reader_stars": "★★★☆☆",
        "trust": "Fiction",
        "tags": "bajka, susza, magia, Collection Eleven",
        "keywords": "Klucz do deszczowej krainy, Zosia, Kropeia",
        "editorial_notes": "Wariant tej samej baśni co „Klucz babci Rózi” (Lena, inne imię bohaterki); ta sama struktura trzech domków i Królowej Deszczu.",
        "inspiration": "Manuskrypt Collection Eleven; YouTube 55rrx4XtY8g (06.01.2022).",
        "philosophy_stars": 3,
        "philosophy_note": "Dobra bajka, lecz near-duplicate — słabsza pozycja na półce obok „Klucz babci Rózi”.",
        "founder_notes": [
            "Founder note: Near-duplicate z „Klucz babci Rózi” — ten sam YouTube i ten sam łuk fabularny; founder wybiera jedną wersję."
        ],
        "series": "Collection Eleven",
        "quiz": [
            {
                "question": "Ile lat ma Zosia?",
                "answers": [
                    "Siedem",
                    "Dziewięć",
                    "Jedenastu",
                    "Dwanaście"
                ],
                "correct": "B",
                "explanation": "Tekst: „Zosia miała dziewięć lat”.",
                "reference": "dziewięć lat"
            },
            {
                "question": "Jak nazywa się Królowa Deszczu?",
                "answers": [
                    "Kropeia",
                    "Rózia",
                    "Śnieżynka",
                    "Stella"
                ],
                "correct": "A",
                "explanation": "Królowa nazywa się Kropeia.",
                "reference": "Kropeia"
            },
            {
                "question": "Co otwiera drzwi do zaczarowanej ścieżki?",
                "answers": [
                    "Srebrny kluczyk",
                    "Mapa",
                    "Zaklęcie bez klucza",
                    "Piosenka bez klucza"
                ],
                "correct": "A",
                "explanation": "Babcia wyjmuje mały srebrny kluczyk z fartuszka.",
                "reference": "srebrny kluczyk"
            },
            {
                "question": "Jakie trzy dźwięki zgaduje Zosia u motylka?",
                "answers": [
                    "Kogut, krowa, świerszcze",
                    "Pies, kot, kura",
                    "Deszcz, wiatr, grzmot",
                    "Flet, harfa, bęben"
                ],
                "correct": "A",
                "explanation": "Odgaduje koguta (kukuryku), krowę (muuu) i świerszcze (cyk-cyk).",
                "reference": "kukuryku"
            },
            {
                "question": "Co Kropeia robi nad wyschniętą krainą?",
                "answers": [
                    "Śpiewa piosenkę deszczu",
                    "Rzuca klucz",
                    "Zamraża jezioro",
                    "Ucieka na Księżyc"
                ],
                "correct": "A",
                "explanation": "Kropeia śpiewa, a z chmur spada obfity deszcz.",
                "reference": "piosenkę deszczu"
            }
        ],
        "motifs": [
            "key",
            "rain",
            "journey",
            "grandmother",
            "courage",
            "wonder"
        ]
    },
    "Ognioskoczek": {
        "manuscript_title": "Ognioskoczek",
        "slug": "ognioskoczek",
        "pack_id": "polish_ognioskoczek",
        "display_title": "Ognioskoczek",
        "subtitle": "Duszek z psót i czerwona czapeczka",
        "blurb": "W starym dworze rodzeństwo i poeta-nauczyciel muszą uwięzić Ognioskoczka — duszka zrodzonego z kłótni i psot — zanim zniszczy cały dom; lecz prawdziwa broń to czerwona czapeczka i dobroć.",
        "genres": "fairy_tale, short_story",
        "cover_family": "legends",
        "audience": "children_8_12",
        "difficulty": 3,
        "reader_stars": "★★★★☆",
        "trust": "Fiction",
        "tags": "duchy, przygoda, rodzeństwo, Collection Eleven",
        "keywords": "Ognioskoczek, dwór, duszek, czapeczka",
        "editorial_notes": "Baśń grozy w łagodnym tonie; epizod podziemi ze skarbami i szkieletem ichtiozaura — adventure, nie horror.",
        "inspiration": "Manuskrypt Collection Eleven; YouTube NFtFrlt62Zs (18.03.2016).",
        "philosophy_stars": 4,
        "philosophy_note": "Dobra opowieść o konsekwencjach psot i współpracy rodzeństwa.",
        "founder_notes": [
            "Founder note: Delikatne elementy grozy — age note 8+."
        ],
        "series": "Collection Eleven",
        "quiz": [
            {
                "question": "Skąd bierze moc Ognioskoczek?",
                "answers": [
                    "Z psót i złych myśli dzieci",
                    "Ze słońca",
                    "Z księgi bez psów",
                    "Z wody"
                ],
                "correct": "A",
                "explanation": "Pan Stanisław mówi, że powstał z psót i złych myśli.",
                "reference": "psót i złych myśli"
            },
            {
                "question": "W czym uwięzią Ognioskoczka?",
                "answers": [
                    "W szklanym gąsiorze ze słodyczami",
                    "W worku",
                    "W piwnicy",
                    "W szafie"
                ],
                "correct": "A",
                "explanation": "Przygotowują gąsior z miodem i konfiturami jako pułapkę.",
                "reference": "gąsior"
            },
            {
                "question": "Co traci duszek, gdy traci czapeczkę?",
                "answers": [
                    "Całą swoją siłę",
                    "Głos",
                    "Pamięć",
                    "Skarb"
                ],
                "correct": "A",
                "explanation": "Księga mówi, że bez czerwonej czapeczki traci całą moc.",
                "reference": "czerwonej czapeczce"
            },
            {
                "question": "W kim zamienia się Ognioskoczek na końcu?",
                "answers": [
                    "Mały czerwony kamyczek",
                    "Motyl",
                    "Kot",
                    "Iskra"
                ],
                "correct": "A",
                "explanation": "Kurczy się i zamienia w mały czerwony kamyczek.",
                "reference": "czerwony kamyczek"
            },
            {
                "question": "Jak nazywa się księga zaklęć?",
                "answers": [
                    "O duchach, czarach i zaklęciach — dzieło mistrza Adalberta",
                    "Harry Potter",
                    "Koziołek Matołek",
                    "Pan Tadeusz"
                ],
                "correct": "A",
                "explanation": "Pan Stanisław znajduje księgę mistrza Adalberta o duchach.",
                "reference": "mistrza Adalberta"
            }
        ],
        "motifs": [
            "fire",
            "fear",
            "family",
            "adventure",
            "forgiveness",
            "home"
        ]
    },
    "Cukierek z magicznego drzewa": {
        "manuscript_title": "Cukierek z magicznego drzewa",
        "slug": "cukierek-z-magicznego-drzewa",
        "pack_id": "polish_cukierek_z_magicznego_drzewa",
        "display_title": "Cukierek z magicznego drzewa",
        "subtitle": "Kiedy pomoc musi być szczera",
        "blurb": "Lisek Rudi chce zdobyć cukierki z magicznego drzewa, pomagając innym tylko po to, by dostać nagrodę — dopóki nie odkrywa, że drzewo obdarowuje tylko tych, którzy pomagają bezinteresownie.",
        "genres": "fairy_tale, short_story",
        "cover_family": "nature",
        "audience": "children_8_12",
        "difficulty": 2,
        "reader_stars": "★★★★☆",
        "trust": "Fiction",
        "tags": "leśni przyjaciele, hojność, Collection Eleven",
        "keywords": "Cukierek, magiczne drzewo, Rudi, Kicek, Kolczuś",
        "editorial_notes": "Prosta morałka o bezinteresownej pomocy; postacie zwierzęce.",
        "inspiration": "Manuskrypt Collection Eleven; YouTube 5s-nYusLT9o (21.06.2021).",
        "philosophy_stars": 4,
        "philosophy_note": "Klasyczna opowieść moralna — czytelna i pozytywna.",
        "founder_notes": [],
        "series": "Collection Eleven",
        "quiz": [
            {
                "question": "Jak nazywają się trzej przyjaciele?",
                "answers": [
                    "Kicek, Kolczuś i Rudi",
                    "Burek, Azor i Filek",
                    "Matołek, Tygrys i Terka",
                    "Kicek, Rudi i Terka"
                ],
                "correct": "A",
                "explanation": "To zajączek Kicek, jeżyk Kolczuś i lisek Rudi.",
                "reference": "Kicek, Kolczuś i Rudi"
            },
            {
                "question": "Kto pierwszy dostaje cukierka?",
                "answers": [
                    "Kolczuś",
                    "Rudi",
                    "Kicek",
                    "Nikt"
                ],
                "correct": "A",
                "explanation": "Kolczuś pomaga Kickowi z kolcem bezinteresownie i dostaje cukierka.",
                "reference": "Kolczuś"
            },
            {
                "question": "Dlaczego Rudi początkowo nie dostaje cukierków?",
                "answers": [
                    "Pomaga tylko po to, by dostać nagrodę",
                    "Nie zna drzewa",
                    "Jest chory",
                    "Nie lubi słodyczy"
                ],
                "correct": "A",
                "explanation": "Jego pomoc nie jest bezinteresowna — oczekuje nagrody.",
                "reference": "oczekiwał nagrody"
            },
            {
                "question": "Co robi Rudi, gdy w końcu dostaje cukierki?",
                "answers": [
                    "Dzieli się nimi z innymi",
                    "Je wszystkie sam",
                    "Wyrzuca je",
                    "Chowa na zimę"
                ],
                "correct": "A",
                "explanation": "Mówi, że podzieli się z tymi, którym pomógł, a resztę zjedzą razem.",
                "reference": "Podzielę się"
            },
            {
                "question": "Kiedy liść zamienia się w cukierka?",
                "answers": [
                    "Gdy Kolczuś bezinteresownie pomaga Kickowi",
                    "Gdy pada deszcz",
                    "Gdy Rudi krzyczy",
                    "W nocy"
                ],
                "correct": "A",
                "explanation": "Drzewo reaguje na bezinteresowną pomoc Kolczusia.",
                "reference": "pomógł Kickowi"
            }
        ],
        "motifs": [
            "forest",
            "generosity",
            "friendship",
            "teaching",
            "discovery",
            "home"
        ]
    },
    "Pies Pankracy i sprawy ważne": {
        "manuscript_title": "Pies Pankracy i sprawy ważne",
        "slug": "pies-pankracy-i-sprawy-wazne",
        "pack_id": "polish_pies_pankracy_i_sprawy_wazne",
        "display_title": "Pies Pankracy i sprawy ważne",
        "subtitle": "Starszy brat ma cztery łapy",
        "blurb": "Siedmioletni Franek czuje się najsłabszy na podwórku — dopóki sąsiad nie puszcza kasety z „Piątkiem z Pankracym” i Franek nie rozumie, że jego kudłaty pies może być najlepszym starszym bratem.",
        "genres": "short_story",
        "cover_family": "everyday_live",
        "audience": "children_8_12",
        "difficulty": 2,
        "reader_stars": "★★★★☆",
        "trust": "Fiction",
        "tags": "przyjaźń, pies, rodzeństwo, Collection Eleven",
        "keywords": "Pankracy, Franek, Piątek z Pankracym, pies",
        "editorial_notes": "Nostalgiczna opowieść nawiązująca do programu „Piątek z Pankracym”; imię Franek jak w innej opowieści C11, inny bohater (7 vs 10 lat).",
        "inspiration": "Manuskrypt Collection Eleven; YouTube omVdhhraUiY (27.11.2022); nawiązanie do programu TVP „Piątek z Pankracym”.",
        "philosophy_stars": 4,
        "philosophy_note": "Ciepła opowieść o przyjaźni i odwadze — dobra dla młodszych czytelników.",
        "founder_notes": [
            "Founder note: Imię „Franek” też w „Franek i mały Karolek” — inne postacie; brak kolizji fabularnej."
        ],
        "series": "Collection Eleven",
        "quiz": [
            {
                "question": "Ile lat ma Franek w tej opowieści?",
                "answers": [
                    "Siedem",
                    "Dziesięć",
                    "Pięć",
                    "Dwanaście"
                ],
                "correct": "A",
                "explanation": "Tekst: „Franek miał siedem lat”.",
                "reference": "siedem lat"
            },
            {
                "question": "Jak nazywa się pies?",
                "answers": [
                    "Pankracy",
                    "Burek",
                    "Azor",
                    "Rudi"
                ],
                "correct": "A",
                "explanation": "Pankracy należy do pana Zygmunta z parteru.",
                "reference": "Pankracy"
            },
            {
                "question": "Z jakiego programu puszcza pan Zygmunt kasetę?",
                "answers": [
                    "Piątek z Pankracym",
                    "Słonecznik",
                    "Teleranek",
                    "Klan"
                ],
                "correct": "A",
                "explanation": "Kaseta pochodzi z programu „Piątek z Pankracym”.",
                "reference": "Piątek z Pankracym"
            },
            {
                "question": "Co mówi wrona o bałwanie?",
                "answers": [
                    "Wyglądać a być to dwie różne sprawy",
                    "Bałwan jest żywy",
                    "Bałwan to król",
                    "Bałwan trzeba zniszczyć"
                ],
                "correct": "A",
                "explanation": "Wrona mówi: „Wyglądać a być, to dwie różne sprawy”.",
                "reference": "dwie różne sprawy"
            },
            {
                "question": "Jak Pankracy pomaga Frankowi na podwórku?",
                "answers": [
                    "Staje obok niego — jeden krok wystarcza, by odpłoszyć chłopca",
                    "Gryzie wszystkich",
                    "Uczy go piłki",
                    "Zabiera go do domu"
                ],
                "correct": "A",
                "explanation": "Pankracy robi krok do przodu i chłopiec cofa się.",
                "reference": "krok do przodu"
            }
        ],
        "motifs": [
            "dog",
            "courage",
            "friendship",
            "childhood",
            "home",
            "companionship"
        ]
    }
}


def load_collection_ten_base() -> dict:
    spec = importlib.util.spec_from_file_location("phase119_build_specs", BUILD_SPECS)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {BUILD_SPECS}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return json.loads(mod.COLLECTION_TEN_RAW)


def is_story_header(title: str) -> bool:
    t = title.strip()
    if not t or re.match(r"^\d+\.", t) or re.match(r"^[IVX]+\.$", t):
        return False
    return t.upper() not in ACT_SECTIONS


def parse_manuscript(path: Path) -> dict[str, dict]:
    raw = path.read_text(encoding="utf-8")
    header = re.compile(r'^##\s+(?:"([^"]+)"|([^\n"]+?))\s*$', re.MULTILINE)
    matches = [
        m
        for m in header.finditer(raw)
        if is_story_header((m.group(1) or m.group(2)).strip())
    ]
    stories: dict[str, dict] = {}
    for i, match in enumerate(matches):
        title = (match.group(1) or match.group(2)).strip()
        chunk = raw[match.end() : matches[i + 1].start() if i + 1 < len(matches) else len(raw)]
        source_block = ""
        src = re.search(r"```source\n(.*?)```", chunk, re.DOTALL)
        if src:
            source_block = src.group(1).strip()
        body = ""
        story_match = re.search(r"```story\n(.*?)```", chunk, re.DOTALL)
        if story_match:
            body = story_match.group(1).strip()
        youtube_ids = re.findall(r"[?&]v=([A-Za-z0-9_-]{11})", source_block)
        dates = re.findall(r"(\d{2})\.(\d{2})\.(\d{4})", source_block)
        source_dates = [f"{y}-{m}-{d}" for d, m, y in dates]
        stories[title] = {
            "source_block": source_block,
            "body": body,
            "youtube_ids": youtube_ids,
            "source_dates": source_dates,
            "word_count": len(re.findall(r"\S+", body)),
        }
    return stories


def inspiration_from_story(title: str, story: dict, fallback: str) -> str:
    parts = [fallback.rstrip(".")]
    yt = story.get("youtube_ids") or []
    dates = story.get("source_dates") or []
    if yt:
        tail = f"YouTube {yt[0]}"
        if dates:
            tail += f" ({dates[0]})"
        parts.append(tail)
    return "; ".join(parts) + "."


def validate_entry(title: str, entry: dict) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in entry:
            errors.append(f"{title}: missing {field}")
    quiz = entry.get("quiz", [])
    if len(quiz) != 5:
        errors.append(f"{title}: expected 5 quiz questions, got {len(quiz)}")
    for i, q in enumerate(quiz, 1):
        for qf in ("question", "answers", "correct", "explanation", "reference"):
            if qf not in q:
                errors.append(f"{title}: quiz {i} missing {qf}")
        if len(q.get("answers", [])) != 4:
            errors.append(f"{title}: quiz {i} needs 4 answers")
        if q.get("correct") not in {"A", "B", "C", "D"}:
            errors.append(f"{title}: quiz {i} invalid correct {q.get('correct')!r}")
    if entry.get("manuscript_title") != title:
        errors.append(f"{title}: manuscript_title mismatch")
    if entry.get("series") not in {"Collection Ten", "Collection Eleven"}:
        errors.append(f"{title}: invalid series")
    if not isinstance(entry.get("motifs"), list) or not entry["motifs"]:
        errors.append(f"{title}: motifs must be non-empty list")
    return errors


def build_collection_ten(stories: dict[str, dict]) -> dict:
    base = load_collection_ten_base()
    out: dict = {}
    for title in C10_TITLES:
        if title not in base:
            raise KeyError(f"C10 base missing {title}")
        if title not in C10_QUIZZES:
            raise KeyError(f"C10 quiz missing {title}")
        if title not in stories:
            raise KeyError(f"C10 manuscript missing {title}")
        entry = dict(base[title])
        entry["series"] = "Collection Ten"
        entry["quiz"] = C10_QUIZZES[title]
        entry["inspiration"] = inspiration_from_story(title, stories[title], C10_INSPIRATION[title])
        if title == "Cisza":
            entry["slug"] = "cisza-dom"
            entry["pack_id"] = "polish_cisza_dom"
        errors = validate_entry(title, entry)
        if errors:
            raise ValueError("\n".join(errors))
        out[title] = entry
    return out


def build_collection_eleven(stories: dict[str, dict]) -> dict:
    out: dict = {}
    for title in C11_TITLES:
        if title in C11_SKIP:
            continue
        if title not in COLLECTION_ELEVEN_RAW:
            raise KeyError(f"C11 raw missing {title}")
        if title not in stories:
            raise KeyError(f"C11 manuscript missing {title}")
        entry = dict(COLLECTION_ELEVEN_RAW[title])
        entry["series"] = "Collection Eleven"
        fallback = entry.get("inspiration") or f"Manuskrypt Collection Eleven — {title}"
        entry["inspiration"] = inspiration_from_story(title, stories[title], fallback)
        errors = validate_entry(title, entry)
        if errors:
            raise ValueError("\n".join(errors))
        out[title] = entry
    return out


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    if not C10_MANUSCRIPT.exists():
        raise FileNotFoundError(C10_MANUSCRIPT)
    if not C11_MANUSCRIPT.exists():
        raise FileNotFoundError(C11_MANUSCRIPT)

    c10_stories = parse_manuscript(C10_MANUSCRIPT)
    c11_stories = parse_manuscript(C11_MANUSCRIPT)

    if "Sprawa" in c11_stories:
        print(
            f"Skipping Sprawa in C11 output ({c11_stories['Sprawa']['word_count']} words in manuscript)"
        )

    c10_specs = build_collection_ten(c10_stories)
    c11_specs = build_collection_eleven(c11_stories)

    write_json(OUT_C10, c10_specs)
    write_json(OUT_C11, c11_specs)

    for path in (OUT_C10, OUT_C11):
        loaded = json.loads(path.read_text(encoding="utf-8"))
        print(f"OK {path}: {len(loaded)} stories, json.load validated")

    print(f"C10 Cisza slug: {c10_specs['Cisza']['slug']} pack_id: {c10_specs['Cisza']['pack_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
