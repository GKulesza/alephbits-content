#!/usr/bin/env python3
"""Phase 77 — replace weak quizzes with story-comprehension questions."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKS = ROOT / "official" / "glagolitic" / "pl"


@dataclass
class Question:
    text: str
    answers: tuple[str, str, str, str]
    correct: str
    explanation: str
    reference: str = ""


@dataclass
class Quiz:
    title: str
    questions: tuple[Question, ...]


def fmt_quiz(quiz: Quiz) -> str:
    lines = ["## Quiz", "", f"**Quiz title:** {quiz.title}", ""]
    for i, q in enumerate(quiz.questions, 1):
        lines.extend(
            [
                f"### Question {i}",
                "",
                f"**Question:** {q.text}",
                "",
                "**Answers:**",
                f"- A) {q.answers[0]}",
                f"- B) {q.answers[1]}",
                f"- C) {q.answers[2]}",
                f"- D) {q.answers[3]}",
                "",
                f"**Correct:** {q.correct}",
                f"**Explanation:** {q.explanation}",
            ]
        )
        if q.reference:
            lines.append(f"**Text reference:** {q.reference}")
        lines.append("")
    return "\n".join(lines)


QUIZZES: dict[str, Quiz] = {
    "na-dworcu": Quiz(
        "Sprawdź zrozumienie",
        (
            Question(
                "Skąd Marek jedzie pociągiem?",
                ("Z Poznania do Gdańska", "Z Warszawy do Krakowa", "Z Gdyni do Szczecina", "Z Wrocławia do Berlina"),
                "A",
                "Tekst mówi wprost o trasie z Poznania do Gdańska.",
                "Marek jechał pociągiem z Poznania do Gdańska",
            ),
            Question(
                "Na jakim dworcu Marek postanawia przejść się po holu?",
                ("Gdańsk Główny", "Poznań Główny", "Wrocław Główny", "Tczew"),
                "A",
                "Marek stoi na peronie dworca Gdańsk Główny.",
                "dworca Gdańsk Główny",
            ),
            Question(
                "Co ojciec Mareka mówi o dawnym jeździe koleją?",
                (
                    "Że bycie na dworcu znaczyło być w mieście",
                    "Że dworce zawsze były galeriami",
                    "Że nigdy nie jeździł pociągiem",
                    "Że podróże koleją się skończyły",
                ),
                "A",
                "Ojciec wspomina, że kiedyś bycie na dworcu znaczyło być w mieście.",
                "Było się na dworcu",
            ),
            Question(
                "Co Marek zapisuje w notatkach w telefonie?",
                (
                    "Że dworzec to próg podróży",
                    "Że nie lubi pociągów",
                    "Że wraca do Poznania na stałe",
                    "Że Gdańsk jest brzydki",
                ),
                "A",
                "Notatka mówi, że dworzec to próg, nie tylko budynek.",
                "Dworzec to próg",
            ),
            Question(
                "Dlaczego Marek broni Poznania w komentarzach?",
                (
                    "Bo stamtąd pochodzi",
                    "Bo ma najpiękniejszy dworzec w Polsce",
                    "Bo tam pracuje",
                    "Bo nigdy nie był w Gdańsku",
                ),
                "A",
                "Marek pochodzi z Poznania i broni go w sporze o dworce.",
                "Marek pochodził z Poznania",
            ),
        ),
    ),
    "w-kawiarni": Quiz(
        "Sprawdź zrozumienie",
        (
            Question(
                "Po co Marek przychodzi do kawiarni?",
                (
                    "Żeby mieć chwilę innego życia",
                    "Żeby odebrać pensję",
                    "Żeby pracować za barem",
                    "Żeby kupić kawę na wynos dla syna",
                ),
                "A",
                "Marek szuka miejsca, w którym może udawać kogoś innego.",
                "miejsca, w którym mógłby przez godzinę udawać",
            ),
            Question(
                "Co Marek zamawia przy barze?",
                ("Cappuccino z mlekiem owsianym", "Herbatę z cytryną", "Podwójne espresso", "Sernik"),
                "A",
                "Zamawia duże cappuccino z mlekiem owsianym.",
                "cappuccino z mlekiem owsianym",
            ),
            Question(
                "O kim Marek myśli, czekając w kawiarni?",
                ("O synu Kubie", "O szefie z biura", "O matce", "O lekarzu"),
                "A",
                "Wspomina rozmowę, w której Kuba pyta, czy tata wróci.",
                "Tato, ale ty wrócisz?",
            ),
            Question(
                "Co baristka daje Marekowi przy drugiej wizycie?",
                ("Kawę na koszt firmy", "Rachunek do zapłaty", "Wizytówkę z pracy", "Sernik gratis"),
                "A",
                "Wraca z kubkiem i mówi: „Na koszt firmy”.",
                "Na koszt firmy",
            ),
            Question(
                "Co Marek robi z wizytówką fundacji?",
                (
                    "Dzwoni i pyta, jak zacząć od nowa",
                    "Wyrzuca ją w kosz",
                    "Oddaje baristce",
                    "Wysyła SMS do byłej żony",
                ),
                "A",
                "Na końcu dzwoni i pyta o fundację.",
                "pytanie o tę... fundację",
            ),
        ),
    ),
    "oczy-ktore-nie-widza": Quiz(
        "Sprawdź zrozumienie",
        (
            Question(
                "Kim jest pani Anna?",
                ("Nauczycielką czytania w zerówce", "Lekarką", "Dyrektorką szkoły", "Autorką podręczników"),
                "A",
                "Prowadzi zajęcia z czytania w zerówce od dwudziestu lat.",
                "zajęcia z czytania w zerówce",
            ),
            Question(
                "Co chłopiec mówi o sylabie „ma”?",
                ('„Em a”', '„Ma-ma”', '„A em”', '„Ma” bez łączenia'),
                "A",
                "Nazywa litery zamiast łączyć je w sylabę.",
                "Mówi się em a",
            ),
            Question(
                "Dlaczego pani Anna mówi, że chłopiec nie czyta?",
                (
                    "Rozpoznaje obrazki z aplikacji",
                    "Nie zna alfabetu",
                    "Nie chodzi do szkoły",
                    "Ma wadę wzroku",
                ),
                "A",
                "Aplikacja pokazuje słowa z obrazkami — to kojarzenie, nie czytanie.",
                "On rozpoznaje obrazy",
            ),
            Question(
                "Co matka zmienia po rozmowie z pani Anną?",
                (
                    "Czyta dziecku książki i ćwiczy sylaby",
                    "Kupuje nowy tablet",
                    "Zapisuje syna na sport",
                    "Zmienia szkołę",
                ),
                "A",
                "Po miesiącu matka czyta książki i pokazuje sylaby — chłopiec zaczyna czytać.",
                "Czytałam mu książki",
            ),
            Question(
                "Co pani Anna mówi matce na końcu?",
                (
                    "To pani nauczyła chłopca czytać",
                    "Aplikacja wystarczy",
                    "Dziecko nie nadaje się do nauki",
                    "Szkoła jest winna",
                ),
                "A",
                "Mówi: „To nie ja. To pani.”",
                "To pani",
            ),
        ),
    ),
    "pierwszy-lot-na-marsa": Quiz(
        "Sprawdź zrozumienie",
        (
            Question(
                "Ile lat ma Marek, gdy słyszy o Marsie?",
                ("Osiem", "Szesnaście", "Sześćdziesiąt", "Trzydzieści"),
                "A",
                "Marek ma osiem lat, gdy Viking przesyła pierwsze zdjęcia.",
                "Marek miał osiem lat",
            ),
            Question(
                "Co Marek widzi na pierwszym zdjęciu z Viking?",
                ("Coś jak twarz", "Kanały wody", "Miasto", "Statek kosmiczny"),
                "A",
                "Wskazuje formację skalną wyglądającą jak twarz.",
                "To twarz",
            ),
            Question(
                "Co odkrywa łazik Perseverance w kraterze Jezero?",
                ("Starożytną deltę rzeki", "Bazę obcych", "Lodowiec", "Wulkan"),
                "A",
                "Marek mówi o starożytnej delcie rzeki — dobrym miejscu na ślady życia.",
                "starożytna delta rzeki",
            ),
            Question(
                "Jak nazywa się skała z okrągłymi plamami?",
                ("Cheyava Falls", "ALH84001", "Twarz z Cydonii", "Viking Rock"),
                "A",
                "Perseverance znalazł skałę Cheyava Falls.",
                "Cheyava Falls",
            ),
            Question(
                "Co ojciec mówi o błędzie z kanałami na Marsie?",
                (
                    "Sprawił, że ludzie zaczęli marzyć",
                    "Udowodnił, że na Marsie jest życie",
                    "Zniszczył astronomię",
                    "Był ważniejszy niż prawda",
                ),
                "A",
                "Ojciec mówi, że błąd sprawił, że ludzie zaczęli marzyć.",
                "ludzie zaczęli marzyć",
            ),
        ),
    ),
    "rozmowa-z-lekarzem": Quiz(
        "Sprawdź zrozumienie",
        (
            Question(
                "Co alarmuje Kasię przed wizytą u lekarza?",
                ("Pierwszy gruby żylak", "Złamanie nogi", "Alergia skórna", "Skurcz ramienia"),
                "A",
                "Pojawia się pierwszy gruby, kręty żylak.",
                "pierwszy żylak",
            ),
            Question(
                "Jak działają zastawki w żyłach według lekarza?",
                (
                    "Otwierają się tylko w górę",
                    "Puszczają krew w obie strony",
                    "Zamykają żyłę na stałe",
                    "Nie występują u ludzi",
                ),
                "A",
                "Zastawki otwierają się tylko w kierunku serca.",
                "tylko w jednym kierunku: w górę",
            ),
            Question(
                "Na czym polega skleroterapia?",
                (
                    "Wstrzyknięcie płynu zamykającego żyłę",
                    "Operacja w szpitalu z narkozą",
                    "Stosowanie kremu na pajączki",
                    "Gorąca kąpiel na nogi",
                ),
                "A",
                "Pianka wypiera krew i zamyka naczynie.",
                "wstrzyknięciu do żylaka specjalnego płynu",
            ),
            Question(
                "Co Kasia dostaje wychodząc z pierwszej wizyty?",
                ("Skierowanie i zalecenia", "Zwolnienie lekarskie", "Tylko receptę na krem", "Umowę na operację"),
                "A",
                "Wychodzi z kartką zaleceń i skierowaniem na USG.",
                "skierowaniem na USG",
            ),
            Question(
                "Jak wyglądają nogi Kasi po trzech miesiącach?",
                ("Bez śladu żylaków", "Gorzej niż wcześniej", "Nadal bardzo bolą", "Wymagają amputacji"),
                "A",
                "Na kontroli nie ma śladu po żylakach.",
                "Nie miała śladu po żylakach",
            ),
        ),
    ),
    "jak-ugotowac-herbate": Quiz(
        "Sprawdź zrozumienie",
        (
            Question(
                "Co Patryk myśli o podwójnym czajniku tureckim?",
                ("Że to sprytny wynalazek", "Że służy do kawy", "Że jest zepsuty", "Że parzy tylko zioła"),
                "A",
                "Patryk uważa podwójny czajnik za genialny.",
                "podwójny czajnik turecki",
            ),
            Question(
                "Co Furkan mówi Patrykowi o parzeniu?",
                ("Za mało herbaty i za krótko", "Za dużo cukru", "Zimna woda", "Złe liście"),
                "A",
                "Furkan radzi: więcej liści i dłuższe parzenie.",
                "Za mało herbaty",
            ),
            Question(
                "Co mistrzyni matcha mówi o herbacie?",
                ("Że to harmonia i szacunek", "Że trzeba pić szybko", "Że jest tylko napojem", "Że jest zawsze gorzka"),
                "A",
                "Mówi: harmonia, szacunek, czystość, spokój.",
                "To harmonia. Szacunek",
            ),
            Question(
                "Jak pije się herbatę w Turcji według tekstu?",
                ("Mocna i słodka w małych szklankach", "Zimna bez cukru", "Tylko wieczorem", "Wyłącznie w ceremonii"),
                "A",
                "W Turcji piją ją mocną, słodką, w małych szklankach.",
                "mocną i słodką",
            ),
            Question(
                "Jaki wniosek wyciąga Patryk na końcu?",
                (
                    "Każdy ma swój dobry sposób parzenia",
                    "Tylko matcha się liczy",
                    "Herbata jest wszędzie taka sama",
                    "Polska herbata jest najlepsza",
                ),
                "A",
                "Każdy ma swój sposób — i każdy jest dobry.",
                "Każdy ma swój sposób",
            ),
        ),
    ),
    "maria-sklodowska-curie": Quiz(
        "Sprawdź zrozumienie",
        (
            Question(
                "Gdzie rodzi się Maria?",
                ("W Warszawie", "W Paryżu", "W Krakowie", "We Francji"),
                "A",
                "Warszawa, rok 1867 — rodzina Skłodowskich.",
                "Warszawa, rok 1867",
            ),
            Question(
                "Dlaczego Maria traci wiarę w Boga?",
                ("Po śmierci matki", "Po wojnie", "Po śmierci ojca", "Po rozwodzie"),
                "A",
                "Po śmierci matki na gruźlicę przestaje wierzyć.",
                "umiera na gruźlicę",
            ),
            Question(
                "Jak Maria dociera na Sorbonę?",
                (
                    "Pracuje i wspiera siostrę Bronię",
                    "Dostaje stypendium od cara",
                    "Jedzie z mężem Pierre'em",
                    "Wygrywa konkurs naukowy",
                ),
                "A",
                "Z Bronią zawiera pakt: najpierw jedna studiuje, druga pracuje.",
                "pracuje jako guwernantka",
            ),
            Question(
                "Jak nazwała pierwiastek ku czci Polski?",
                ("Polon", "Radium", "Uran", "Curium"),
                "A",
                "Maria nazywa go Polonem — hołd dla Polski.",
                "Nazywa go Polonem",
            ),
            Question(
                "Ile razy Maria dostała Nagrodę Nobla?",
                ("Dwa razy", "Raz", "Trzy razy", "Nigdy"),
                "A",
                "Nobel z fizyki i z chemii.",
                "drugą Nagrodę Nobla",
            ),
        ),
    ),
    "dlaczego-niebo-jest-niebieskie": Quiz(
        "Sprawdź zrozumienie",
        (
            Question(
                "Dlaczego niebo wygląda na niebieskie?",
                ("Rozpraszanie krótkofalowego światła", "Farba w chmurach", "Odbicie morza", "Iluzja o zmierzchu"),
                "A",
                "Tekst wyjaśnia rozpraszanie Rayleigha — niebieskie fale rozpraszają się mocniej.",
                "rozpraszanie Rayleigha",
            ),
            Question(
                "Co Gladstone zauważa u Homera?",
                ("Brak słowa na niebieski", "Setki opisów nieba", "Tylko biały kolor", "Opis tęczy"),
                "A",
                "Gladstone liczy kolory u Homera — niebieski nie występuje.",
                "Niebieski – zero",
            ),
            Question(
                "Kogo tekst wspomina przy trudnym problemie świadomości?",
                ("Feynmana", "Newtona", "Einsteina", "Kopernika"),
                "A",
                "Feynman wraca do pokory wobec tego, czego nie rozumiemy.",
                "Feynman",
            ),
            Question(
                "Co Himba robi inaczej niż Europejczycy?",
                ("Lepiej widzą odcienie zieleni", "Nie widzą w ogóle", "Nie rozróżniają czerwieni", "Widzą tylko czarno-białe"),
                "A",
                "Himba szybciej wskazują różne odcienie zieleni.",
                "Himba wskazywali go natychmiast",
            ),
            Question(
                "Jakie pytanie Feynman zadaje kelnerce?",
                ("Skąd wiesz, że niebo jest niebieskie?", "Ile kosztuje kawa?", "Gdzie jest Berkeley?", "Czy lubi fizykę?"),
                "A",
                "Pyta: skąd wiesz — i kelnerka wzrusza ramionami.",
                "Skąd wiesz?",
            ),
        ),
    ),
    "legenda-o-smoku-wawelskim": Quiz(
        "Sprawdź zrozumienie",
        (
            Question(
                "Kim jest Skuba?",
                ("Szewczykiem", "Królem", "Rycerzem od razu", "Kupcem z rynku"),
                "A",
                "Skuba to prosty szewczyk z Krakowa.",
                "prosty szewczyk",
            ),
            Question(
                "Co Skuba wkłada do barana?",
                ("Siarkę i smołę", "Złoto", "Truciznę z apteki", "Kamienie"),
                "A",
                "Wypełnia barana siarką i smołą.",
                "siarką i smołą",
            ),
            Question(
                "Dlaczego smok ginie?",
                ("Pije za dużo wody i pęka", "Spada z wieży", "Ginie od miecza", "Ucieka w góry"),
                "A",
                "Pił z Wisły, aż pękł.",
                "pękł",
            ),
            Question(
                "Jaki tytuł dostaje Skuba?",
                ("Szczyciel Smoka", "Król Krakowa", "Wódz wojska", "Strażnik Wisły"),
                "A",
                "Król nadaje mu tytuł Szczyciela Smoka.",
                "Szczyciel Smoka",
            ),
            Question(
                "Co ogłasza król na końcu?",
                ("Wielkie wesele", "Nową wojnę", "Zburzenie zamku", "Zbanowanie Skuby"),
                "A",
                "Król ogłasza wielkie wesele ze księżniczką Wandą.",
                "Otwieram wielkie wesele",
            ),
        ),
    ),
    "spacer-po-krakowie": Quiz(
        "Sprawdź zrozumienie",
        (
            Question(
                "Gdzie autor zatrzymał się przy studni?",
                ("Na Małym Rynku", "Na Wawelu", "Na Plantach", "Przy Wiśle"),
                "A",
                "Autor pisze o Małym Rynku.",
                "Na Małym Rynku",
            ),
            Question(
                "Co autor kupił w kawiarni?",
                ("Bułkę", "Kawę", "Wodę", "Ciastko"),
                "A",
                "Kupił bułkę i jadł ją powoli.",
                "Kupiłem bułkę",
            ),
            Question(
                "Co autor widzi na wzgórzu?",
                ("Wawel", "Planty", "Muzeum", "Most"),
                "A",
                "Na wzgórzu zobaczył Wawel.",
                "Wawel",
            ),
            Question(
                "Co słyszy autor idąc do Plant?",
                ("Grajków na skrzypcach", "Dzwony kościelne", "Syrenę tramwaju", "Fale Wisły"),
                "A",
                "Usłyszał grajków grających starą melodię.",
                "grajków",
            ),
            Question(
                "Jaki wniosek wyciąga autor na końcu?",
                (
                    "Czytanie o znanym miejscu pomaga zapamiętać znaki",
                    "Najlepiej uczyć się tylko w muzeum",
                    "Kraków nie ma historii",
                    "Grajkowie przeszkadzają w nauce",
                ),
                "A",
                "Ostatni akapit podsumowuje korzyść z czytania o znanym miejscu.",
                "pomaga zapamiętać nowe znaki",
            ),
        ),
    ),
    "na-targu": Quiz(
        "Sprawdź zrozumienie",
        (
            Question(
                "Gdzie odbywa się opisywany targ?",
                ("W Nowym Targu", "W Elblągu", "W Krakowie", "W Budapeszcie"),
                "A",
                "Adam jedzie na targ w Nowym Targu.",
                "targu w Nowym Targu",
            ),
            Question(
                "Dlaczego ceny podawano w euro?",
                ("Węgrzy i Słowacy nie chcieli przeliczać", "Euro jest walutą Polski", "Bankomaty nie działały", "Sprzedawcy nie znali polskiego"),
                "A",
                "Sprzedawca wyjaśnia, że klienci z Węgier i Słowacji wolą euro.",
                "Węgrzy nie chcą przeliczać",
            ),
            Question(
                "Czym handluje Adam na końcu?",
                ("Skórzanymi kurtkami i butami", "Kaszmirem", "Elektroniką", "Warzywami"),
                "A",
                "Ma własne stoisko ze skórzanymi kurtkami i butami.",
                "skórzane kurtki i buty",
            ),
            Question(
                "Skąd przyjeżdżają kupcy na targ?",
                ("Z Węgier, Czech i Słowacji", "Tylko z Polski", "Z Japonii", "Z USA"),
                "A",
                "Tekst wspomina Węgrów, Czechów i Słowaków.",
                "Węgrzy, Czechy, Słowacja",
            ),
            Question(
                "Ile kosztował kaszmir na stoisku?",
                ("270 złotych", "50 euro", "100 złotych", "10 złotych"),
                "A",
                "Sprzedawca podaje kaszmir za 270 złotych.",
                "Kaszmir za 270 złotych",
            ),
        ),
    ),
    "cien-skrzydel-nad-oceanem": Quiz(
        "Sprawdź zrozumienie",
        (
            Question(
                "Kim był James M. Huston Jr.?",
                ("Pilotem US Navy zabitym w 1945", "Lekarzem z Luizjany", "Niemieckim żołnierzem", "Konstruktorem Enigmy"),
                "A",
                "Tekst identyfikuje go jako pilota lotnictwa morskiego.",
                "pilotem amerykańskiego lotnictwa morskiego",
            ),
            Question(
                "Co dzieje Jamesa budzi u matki?",
                ("Koszmar o ogniu i zablokowanej kabinie", "Spokojny sen", "Prośba o wodę", "Radość z zabawki"),
                "A",
                "Andrea budzi się na krzyk o płomieniach.",
                "ogień, pamiętał dym",
            ),
            Question(
                "Skąd James zna szczegóły poprzedniego życia?",
                ("Po prostu wiedział — nikt mu nie mówił", "Rodzice opowiedzieli", "Z lekcji w przedszkolu", "Z gazety"),
                "A",
                "Tekst podkreśla: nikt mu tego nie powiedział.",
                "Po prostu wiedział",
            ),
            Question(
                "Jak nazywa się matka chłopca?",
                ("Andrea", "Maria", "Anna", "Joanna"),
                "A",
                "Andrea budzi się na krzyk syna.",
                "Andrea",
            ),
            Question(
                "Nad jaką wyspą zginął pilot w poprzednim życiu?",
                ("Chichi Jima", "Okinawa", "Hawaii", "Guam"),
                "A",
                "Tekst podaje Chichi Jimę jako miejsce śmierci.",
                "Chichi Jimą",
            ),
        ),
    ),
    "cisza-przed-burza": Quiz(
        "Sprawdź zrozumienie",
        (
            Question(
                "Jakie podejście Rejewski proponuje wobec Enigmy?",
                ("Zrozumieć działanie urządzenia", "Analizować tylko teksty", "Czekać na komputer", "Ignorować dokumentację"),
                "A",
                "Rejewski mówi, że trzeba zrozumieć maszynę — to matematyka.",
                "zrozumieć, jak działa samo urządzenie",
            ),
            Question(
                "Jaką słabość Niemców odkrywa Rejewski?",
                ("Porządek alfabetyczny w połączeniach", "Losowe połączenia", "Brak wirników", "Jeden klucz rocznie"),
                "A",
                "Konstruktorzy wybrali porządek alfabetyczny.",
                "Porządek alfabetyczny",
            ),
            Question(
                "Czym jest bomba kryptologiczna?",
                ("Urządzeniem symulującym Enigmy", "Bronią palną", "Instrumentem pogodowym", "Książką instruktażową"),
                "A",
                "Bomba symuluje działanie wielu Enigm.",
                "elektromechaniczne urządzenie",
            ),
            Question(
                "Kto jest głównym bohaterem opowieści?",
                ("Marian Rejewski", "Alan Turing", "Hitler", "Generał Sikorski"),
                "A",
                "Rejewski prowadzi prace nad łamaniem Enigmy.",
                "Rejewski",
            ),
            Question(
                "Co Rejewski mówi o Enigmie na początku?",
                ("To matematyka, nie język", "To niemożliwe do złamania", "To tylko legenda", "To amerykański wynalazek"),
                "A",
                "Podkreśla, że trzeba myśleć matematycznie.",
                "to matematyka, nie język",
            ),
        ),
    ),
    "domysl-sie": Quiz(
        "Sprawdź zrozumienie",
        (
            Question(
                "Jaki problem mają Magda i Grzesiek?",
                ("Unikają szczerej rozmowy o potrzebach", "Magda nie lubi jazzu", "Grzesiek nie kupuje mleka", "Magda nie chce się przytulać"),
                "A",
                "Oboje reagują urazą zamiast mówić wprost.",
                "nie umiała powiedzieć",
            ),
            Question(
                "Co Magda zrozumiała na spotkaniu Kapci?",
                ("Udawała zainteresowania Grześkowi", "Powinna częściej kupować mleko", "Grzesiek jest idealny", "Jazz jest lepszy od popu"),
                "A",
                "Przypomniała sobie udawanie zainteresowania spacerami i jazzem.",
                "Udawała, że interesuje się",
            ),
            Question(
                "Jak kończy się opowiadanie?",
                ("Zaczynają mówić wprost o potrzebach", "Rozstają się", "Grzesiek wyjeżdża", "Magda wraca do udawania"),
                "A",
                "Epilog opisuje szczerą komunikację.",
                "mówić wprost",
            ),
            Question(
                "Co Grzesiek zaczyna robić po zmianie?",
                ("Zapisuje prośby Magdy", "Sprzedaje jazzowe płyty", "Przeprowadza się", "Przestaje słuchać muzyki"),
                "A",
                "Grzesiek zapisuje prośby, by ich nie zapomnieć.",
                "zapisuje prośby",
            ),
            Question(
                "Dlaczego Magda udawała zainteresowanie jazzem?",
                ("Bała się odrzucenia", "Uwielbiała ten gatunek", "Grzesiek tego wymagał", "Chciała zostać muzykiem"),
                "A",
                "Udawała z lęku przed odrzuceniem.",
                "z lęku przed odrzuceniem",
            ),
        ),
    ),
    "dziewczyna-ktora-zniknela-o-swicie": Quiz(
        "Sprawdź zrozumienie",
        (
            Question(
                "Co Joanna widzi na nagraniu monitoringu?",
                ("Agnieszka idzie ze spadkiem czujności", "Agnieszka jedzie taksówką", "Agnieszka tańczy wesoło", "Agnieszka rozmawia przez telefon"),
                "A",
                "Joanna mówi o fałszywym syndromie bezpiecznego progu.",
                "Fałszywy syndrom bezpiecznego progu",
            ),
            Question(
                "Dlaczego pierwsze godziny poszukiwań poszły na marne?",
                ("Sprawę potraktowano jak ucieczkę nastolatki", "Nie było zgłoszenia", "Monitoring nie działał", "Agnieszka zadzwoniła na policję"),
                "A",
                "Pierwsze zgłoszenie traktowano jak standardową ucieczkę.",
                "ucieczkę nastolatki",
            ),
            Question(
                "O której kamera widzi Agnieszkę ostatni raz?",
                ("4:12 nad ranem", "2:00 w nocy", "Południe", "22:30"),
                "A",
                "Sekcja „Punkt zero” podaje 4:12.",
                "Godzina 4:12",
            ),
            Question(
                "Kim jest Joanna w opowieści?",
                ("Doświadczoną śledczą", "Matką Agnieszki", "Dziennikarką", "Sąsiadką"),
                "A",
                "Joanna analizuje nagrania i procedury policyjne.",
                "Joanna",
            ),
            Question(
                "Co Joanna mówi o bezpiecznym progu?",
                ("To fałszywe poczucie bezpieczeństwa", "Agnieszka była w domu", "Monitoring kłamie", "Nastolatki zawsze wracają"),
                "A",
                "Fałszywy syndrom bezpiecznego progu obniża czujność.",
                "Fałszywy syndrom",
            ),
        ),
    ),
    "dziewczyna-z-jelania": Quiz(
        "Sprawdź zrozumienie",
        (
            Question(
                "Dlaczego Anastazja jedzie do Polski?",
                ("Chce nauczyć się polskiego", "Odwiedza rodzinę w Jełaniu", "Studiuje medycynę", "Pracuje w taxi"),
                "A",
                "Nie ma tu rodziny ani planów kariery — chce język „w sobie”.",
                "nauczyć się polskiego",
            ),
            Question(
                "Skąd pochodzi Anastazja?",
                ("Z Rosji, mieszka w Niemczech", "Z Polski", "Z USA", "Z Ukrainy"),
                "A",
                "Mówi kierowcy, że jest z Rosji, ale mieszka w Niemczech.",
                "z Rosji, ale mieszkam w Niemczech",
            ),
            Question(
                "Jaką książkę czyta w pokoju na Pradze?",
                ("„Lalkę” Prusa", "„Quo vadis”", "„Pana Tadeusza”", "Podręcznik gramatyki"),
                "A",
                "Czyta „Lalkę” w oryginale.",
                "Lalkę",
            ),
            Question(
                "Gdzie wynajmuje pokój?",
                ("Na Pradze w Warszawie", "W Jełaniu", "W Krakowie", "W Berlinie"),
                "A",
                "Wynajęty pokój na Pradze jest opisany wprost.",
                "pokój na Pradze",
            ),
            Question(
                "Od ilu lat mieszka poza Rosją?",
                ("Od dziewięciu lat", "Od roku", "Od dwudziestu lat", "Od trzech miesięcy"),
                "A",
                "Mieszka w Niemczech od dziewięciu lat.",
                "od dziewięciu lat",
            ),
        ),
    ),
    "jak-bor-z-jasnego-nieba": Quiz(
        "Sprawdź zrozumienie",
        (
            Question(
                "Jak Żuk tłumaczy różnicę żołnierz vs operator?",
                ("To praktycznie to samo", "To zupełnie inne zawody", "Operatorzy nie używają broni", "Żołnierze nie szkolą się"),
                "A",
                "Żuk mówi, że to tak naprawdę to samo.",
                "Tak naprawdę to jest to samo",
            ),
            Question(
                "Gdzie toczy się rozmowa?",
                ("W studiu podcastu „Bez Sekretów”", "Na poligonie", "W sali sądowej", "W telewizji"),
                "A",
                "Piotr i Marcin rozmawiają w studiu podcastu.",
                "Bez Sekretów",
            ),
            Question(
                "Co tekst sugeruje o jednostce BOR?",
                ("Są tematy, o których nie można mówić", "Wszystko można opowiedzieć publicznie", "BOR nie istnieje", "Wszyscy chcą wywiadów"),
                "A",
                "Już w podtytule pada zdanie o rzeczach, o których nie można mówić.",
                "NIGDY NIE BĘDĘ MÓGŁ POWIEDZIEĆ",
            ),
            Question(
                "Jak nazywają się prowadzący podcast?",
                ("Piotr i Marcin", "Adam i Jan", "Marek i Tomek", "Kasia i Ania"),
                "A",
                "Piotr i Marcin rozmawiają z Żukiem.",
                "Piotr i Marcin",
            ),
            Question(
                "Kogo rozmowa dotyczy głównie?",
                ("Operatora Żuka z BOR", "Prezydenta", "Lekarza", "Nauczyciela"),
                "A",
                "Gościem jest operator Żuk.",
                "Żuk",
            ),
        ),
    ),
    "prolog-wiatru": Quiz(
        "Sprawdź zrozumienie",
        (
            Question(
                "Jak nazywa się utwór w opowieści?",
                ("Kaze no Prologue", "Cisza przed burzą", "Prolog wiatru", "Zakazana Energia"),
                "A",
                "Yumiko nagrywa teledysk do Kaze no Prologue.",
                "Kaze no Prologue",
            ),
            Question(
                "Gdzie kręcą teledysk?",
                ("Na plaży w Chiba o świcie", "W studiu w Los Angeles", "Na dworcu w Warszawie", "W górach Hokkaido"),
                "A",
                "Menedżer pisze o plaży w Chiba o 5:00 rano.",
                "plaża w Chiba",
            ),
            Question(
                "Jakie przesłanie niesie piosenka?",
                ("Można zacząć od nowa", "Wiatr jest niebezpieczny", "Kariera się kończy", "Plaża jest zła"),
                "A",
                "Piosenka mówi o nowym początku.",
                "zacząć od nowa",
            ),
            Question(
                "Kim jest główna bohaterka?",
                ("Yumiko", "Maria", "Anna", "Kasia"),
                "A",
                "Yumiko słyszy piosenkę i nagrywa teledysk.",
                "Yumiko",
            ),
            Question(
                "O której godzinie mają być zdjęcia?",
                ("O piątej rano", "O południu", "O północy", "O dwudziestej"),
                "A",
                "Menedżer podaje 5:00 rano.",
                "5:00 rano",
            ),
        ),
    ),
    "siedem-gor-i-jeden-ocean": Quiz(
        "Sprawdź zrozumienie",
        (
            Question(
                "Co zaskakuje Marka w nagłówkach?",
                ("Korea kupuje od Polski tysiąc czołgów", "Polska kupuje czołgi od Korei", "Korea znika z mapy", "Marek dostaje mandat"),
                "A",
                "Czyta o Korei Południowej kupującej czołgi od Polski.",
                "Korea Południowa kupiła od Polski",
            ),
            Question(
                "Dlaczego Marek jedzie do Korei?",
                ("Modernizacja muzeum", "Wycieczka z rodziną", "Nauka koreańskiego", "Start kariery K-pop"),
                "A",
                "Biuro wygrało przetarg na modernizację muzeum.",
                "modernizację jednego z koreańskich muzeów",
            ),
            Question(
                "Co Marek znajduje w wynikach o Polsce?",
                ("Chopin, Wiedźmin, Lewandowski", "Tylko Auschwitz", "Polska nie istnieje w mediach", "Wyłącznie nauka polskiego"),
                "A",
                "Wymienia Chopina, Lewandowskiego i Wiedźmina.",
                "Lewandowski",
            ),
            Question(
                "Jak długo ma pracować w Korei?",
                ("Miesiąc", "Rok", "Tydzień", "Pięć lat"),
                "A",
                "Marek ma jechać na miesiąc.",
                "na miesiąc",
            ),
            Question(
                "Kim jest Marek zawodowo?",
                ("Pracuje przy projektach muzealnych", "Jest żołnierzem", "Jest dziennikarzem", "Jest nauczycielem"),
                "A",
                "Biuro wygrało przetarg na muzeum — Marek reprezentuje firmę.",
                "koreańskich muzeów",
            ),
        ),
    ),
    "trzynascie-zasad": Quiz(
        "Sprawdź zrozumienie",
        (
            Question(
                "Jak tekst wyjaśnia polski uśmiech?",
                ("Nie jest domyślny — pojawia się z powodem", "Polacy uśmiechają się stale", "Uśmiech jest zakazany", "Uśmiech zawsze oznacza flirt"),
                "A",
                "Przyjaciel tłumaczy, że uśmiech to nie domyślne ustawienie twarzy.",
                "Uśmiech to nie jest domyślne ustawienie twarzy",
            ),
            Question(
                "Dlaczego bohaterka czuje się zagubiona?",
                ("Amerykański uśmiech nie otwiera kontaktu", "Nie zna polskich słów", "Nie ma pieniędzy", "Jechała do Krakowa"),
                "A",
                "Ludzie nie reagują na jej ciągły uśmiech.",
                "Nikt się do mnie nie uśmiecha",
            ),
            Question(
                "Co robią Polacy wchodząc do domu?",
                ("Zdejmują buty", "Zostawiają buty na nogach", "Myją okna", "Jedzą obiad"),
                "A",
                "Zasada dziesiąta mówi o zdejmowaniu butów w domu.",
                "Zdejmij buty w domu",
            ),
            Question(
                "Co bohaterka uważa za małe zwycięstwo?",
                ("Powiedzenie „dziękuję” po polsku", "Kupno kawy", "Jazda metrem", "Znalezienie hotelu"),
                "A",
                "Pierwsze „dziękuję” w sklepie to małe zwycięstwo.",
                "dziękuję",
            ),
            Question(
                "Jaka jest różnica między turystą a mieszkańcem?",
                ("Mieszkaniec akceptuje kraj takim, jaki jest", "Turyści uczą się polskiego", "Mieszkańcy nie uśmiechają się", "Turyści zawsze wracają"),
                "A",
                "Turysta domaga się, by kraj był jak jego własny; mieszkaniec akceptuje.",
                "musi się dostosować",
            ),
        ),
    ),
    "wiatr-nad-rzeka": Quiz(
        "Sprawdź zrozumienie",
        (
            Question(
                "Gdzie rozgrywa się scena?",
                ("Na bulwarze nad Wisłą", "Na rynku w Krakowie", "W lesie", "Na dworcu"),
                "A",
                "Anna stoi na bulwarze nad Wisłą.",
                "bulwarze",
            ),
            Question(
                "Co mówi starszy pan o wietrze?",
                ("Wiatr pamięta to, co niosła woda", "Wiatr jest zawsze zimny", "Wiatr zatrzymuje most", "Wiatr nie wraca"),
                "A",
                "Pan mówi, że wiatr pamięta wszystko, co niosła woda.",
                "Wiatr dziś pamięta",
            ),
            Question(
                "Co Anna postanawia na końcu?",
                ("Wrócić jutro", "Nigdy tu nie wracać", "Pojechać nad morze", "Zadzwonić do przyjaciela"),
                "A",
                "Ostatnie zdanie mówi, że wróci jutro.",
                "wróci tu jutro",
            ),
            Question(
                "Jak ma na imię bohaterka?",
                ("Anna", "Maria", "Kasia", "Ewa"),
                "A",
                "Anna stoi na bulwarze.",
                "Anna",
            ),
            Question(
                "Nad jaką rzeką stoi Anna?",
                ("Wisłą", "Odrą", "Wartą", "Sanem"),
                "A",
                "Scena toczy się nad Wisłą.",
                "Wisłą",
            ),
        ),
    ),
    "zakazana-energia": Quiz(
        "Sprawdź zrozumienie",
        (
            Question(
                "Co Helena znajduje w archiwum Dworca Głównego?",
                ("Dokument z 1889 o systemie rezonansowym", "Plany z 2024 roku", "List od Tesli", "Zdjęcia bez adnotacji"),
                "A",
                "Natrafia na projekt z adnotacją o systemie rezonansowym.",
                "System rezonansowy nr 4",
            ),
            Question(
                "Jaki wzorzec Helena widzi w innych miastach?",
                ("Tajne systemy sprzed ery elektrycznej", "Identyczne zegary", "Brak powtarzalności", "Tylko oświetlenie gazowe"),
                "A",
                "W Krakowie, Poznaniu i Wrocławiu widzi podobne systemy.",
                "systemy, które nie powinny istnieć",
            ),
            Question(
                "Jak reaguje Helena na dowody?",
                ("Powtarza, że to niemożliwe", "Od razu publikuje w mediach", "Porzuca zawód", "Udaje, że nic nie znalazła"),
                "A",
                "Wielokrotnie mówi „to niemożliwe”, choć dowody rosną.",
                "To niemożliwe",
            ),
            Question(
                "Kim jest Helena?",
                ("Architektką badającą archiwa", "Dziennikarką", "Kolejarką", "Studentką medycyny"),
                "A",
                "Helena przeszukuje archiwa dworców.",
                "Helena",
            ),
            Question(
                "W którym mieście zaczyna poszukiwania?",
                ("W Warszawie", "W Krakowie", "W Gdańsku", "We Wrocławiu"),
                "A",
                "Zaczyna od archiwów Dworca Głównego w Warszawie.",
                "Dworca Głównego w Warszawie",
            ),
        ),
    ),
    "zasady": Quiz(
        "Sprawdź zrozumienie",
        (
            Question(
                "Jaki problem Kadysz nazywa w liście?",
                ("Postanawiamy sobie rzeczy, z których nic nie wynika", "Brak czasu na czytanie", "Zbyt wiele spotkań", "Brak internetu"),
                "A",
                "List pyta, jak często postanawiamy coś, z czego nic nie wychodzi.",
                "nic nie wychodzi",
            ),
            Question(
                "Co dzieje się, gdy dajemy sobie wybór?",
                ("Umysł znajduje wymówki", "Zawsze wybieramy trudne zadanie", "Motywacja rośnie bez limitu", "Nie ma to wpływu"),
                "A",
                "Przy zastanawianiu się umysł szybko znajduje wymówki.",
                "tysiąc wymówek",
            ),
            Question(
                "Co Łukasz robi zamiast pracować?",
                ("Szuka w internecie nowych metod", "Idzie spać cały dzień", "Dzwoni po urlop", "Sprzedaje komputer"),
                "A",
                "Zamiast pracować czyta o pracy w internecie.",
                "szukał w internecie",
            ),
            Question(
                "Kto napisał list w opowieści?",
                ("Kadysz", "Łukasz", "Maria", "Adam"),
                "A",
                "List otwiera cytat od Kadysza.",
                "Kadysz",
            ),
            Question(
                "Co Łukasz robi, gdy zaczyna wątpić?",
                ("Czyta o aplikacjach i lifehackach", "Od razu kończy pracę", "Jedzie na urlop", "Zatrudnia asystenta"),
                "A",
                "Szuka nowych aplikacji zamiast działać.",
                "nowe aplikacje",
            ),
        ),
    ),
}


def replace_quiz(content: str, quiz_md: str) -> str:
    pattern = r"## Quiz\b.*?(?=\n## Future|\n---\n\n---\n\n## Future|\Z)"
    if not re.search(pattern, content, re.S):
        raise ValueError("No ## Quiz section found")
    return re.sub(pattern, quiz_md.rstrip() + "\n", content, count=1, flags=re.S)


def main() -> None:
    updated = 0
    for slug, quiz in QUIZZES.items():
        path = PACKS / slug / "reading-pack.md"
        if not path.exists():
            print(f"SKIP missing: {slug}")
            continue
        text = path.read_text(encoding="utf-8")
        new_text = replace_quiz(text, fmt_quiz(quiz))
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            updated += 1
            print(f"OK {slug} ({len(quiz.questions)} questions)")
    print(f"\nUpdated {updated} packs")


if __name__ == "__main__":
    main()
