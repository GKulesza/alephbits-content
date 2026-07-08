#!/usr/bin/env python3
"""Migrate Collection One manuscript into official Reading Packs."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

MANUSCRIPT = Path(
    "/Users/admin/Developer/MiscellaneousNotes/AwesomeVault/!Apps/App Ideas/alephBits/CollectionOne.md"
)
OUTPUT_ROOT = Path(__file__).resolve().parent.parent / "official/glagolitic/pl"


@dataclass
class QuizQuestion:
    question: str
    answers: list[str]
    correct: str  # A, B, C, or D
    explanation: str
    text_reference: str = ""


@dataclass
class StoryConfig:
    slug: str
    subtitle: str
    blurb: str
    genres: list[str]
    difficulty: int
    reading_time: int
    trust: str
    tags: list[str]
    keywords: list[str]
    audience: str = "adult readers"
    recommended_level: int = 3
    revision_notes: str = ""
    source_label: str = "Collection One manuscript (YouTube editorial)"
    availability: str = "adaptation"
    quiz: list[QuizQuestion] = field(default_factory=list)


STORIES: dict[str, StoryConfig] = {
    "Domyśl się": StoryConfig(
        slug="domysl-sie",
        subtitle="Opowiadanie o sygnałach w związku",
        blurb="Magda odkrywa, że jej idealny związek z Grześkiem kryje wzorce, których nie chce widzieć — aż spotkanie Kapci otwiera jej oczy na to, co naprawdę czuje.",
        genres=["short_story", "dialogue"],
        difficulty=5,
        reading_time=12,
        trust="Fiction",
        tags=["polish", "fiction", "narrative", "relationships"],
        keywords=["związek", "komunikacja", "randki", "fikcja"],
        recommended_level=3,
        quiz=[
            QuizQuestion(
                "Jaki jest główny problem w relacji Magdy i Grześka według opowiadania?",
                [
                    "Magda nie chce się przytulać po powrocie z pracy",
                    "Oboje unikają szczerej rozmowy o swoich potrzebach i winie",
                    "Grzesiek nie kupuje mleka mimo prośby",
                    "Magda nie lubi jazzu, który słucha Grzesiek",
                ],
                "B",
                "Tekst wielokrotnie pokazuje, że oboje reagują urazą zamiast nazwać swoje uczucia i przeprosić.",
                "nie umiała powiedzieć: \"Przepraszam\"",
            ),
            QuizQuestion(
                "Co Magda zrozumiała po historii opowiedzianej na spotkaniu Kapci?",
                [
                    "Że powinna częściej kupować mleko",
                    "Że udawała zainteresowania, by przypodobać się Grześkowi",
                    "Że Grzesiek jest idealnym partnerem",
                    "Że jazz jest lepszy od popu",
                ],
                "B",
                "Przypomniała sobie, jak udawała zainteresowanie spacerami i jazzem z lęku przed odrzuceniem.",
                "Udawała, że interesuje się jego pracą",
            ),
            QuizQuestion(
                "Jak kończy się opowiadanie w odniesieniu do relacji Magdy i Grześka?",
                [
                    "Rozstają się po spotkaniu Kapci",
                    "Zaczynają mówić wprost o potrzebach i pracować nad komunikacją",
                    "Grzesiek wyjeżdża do Krakowa",
                    "Magda wraca do udawania zainteresowań",
                ],
                "B",
                "Epilog opisuje, że rozmawiają o problemach, Grzesiek zapisuje prośby, a Magda mówi wprost, czego potrzebuje.",
                "zaczęła mówić wprost, czego potrzebuje",
            ),
        ],
    ),
    "Zakazana Energia": StoryConfig(
        slug="zakazana-energia",
        subtitle="Alternatywna historia ukrytej energii",
        blurb="Architektka Helena odkrywa w archiwach dworców kolejowych ślady tajnych systemów energetycznych sprzed oficjalnej ery elektryczności — i ślad prowadzi ją w coraz głębszą spise.",
        genres=["science_fiction", "short_story"],
        difficulty=6,
        reading_time=10,
        trust="Fiction",
        tags=["polish", "fiction", "narrative", "alternate-history"],
        keywords=["architektura", "dworce", "energia", "spise"],
        quiz=[
            QuizQuestion(
                "Co Helena znajduje w archiwach Dworca Głównego w Warszawie?",
                [
                    "Plany nowoczesnego centrum przesiadkowego z 2024 roku",
                    "Dokument z 1889 roku z adnotacjami o „systemie rezonansowym”",
                    "List od Nikola Tesla",
                    "Zdjęcia oświetlenia gazowego bez adnotacji",
                ],
                "B",
                "Natrafia na projekt techniczny z 1889 roku z odręczną adnotacją o systemie rezonansowym.",
                "System rezonansowy nr 4",
            ),
            QuizQuestion(
                "Jaki wzorzec Helena dostrzega w dokumentach z różnych miast?",
                [
                    "Wszystkie dworce miały identyczne zegary",
                    "Podobne tajne systemy i oznaczenia wyprzedzające oficjalną elektryczność",
                    "Brak jakichkolwiek powtarzalnych elementów",
                    "Jedynie projekty oświetlenia gazowego bez adnotacji",
                ],
                "B",
                "W Krakowie, Poznaniu i Wrocławiu widzi te same nietypowe systemy i daty sprzed ery elektrycznej.",
                "systemy, które nie powinny istnieć",
            ),
            QuizQuestion(
                "Jaką reakcję ma Helena, gdy dowody się mnożą?",
                [
                    "Od razu publikuje wyniki w mediach",
                    "Powtarza sobie, że to niemożliwe, mimo narastających dowodów",
                    "Porzuca zawód architekta",
                    "Udaje, że nic nie znalazła",
                ],
                "B",
                "Wielokrotnie mówi „to niemożliwe”, choć dowody z kolejnych archiwów się kumulują.",
                "To niemożliwe – powtarzała sobie",
            ),
        ],
    ),
    "Jak Bor z jasnego nieba.": StoryConfig(
        slug="jak-bor-z-jasnego-nieba",
        subtitle="Rozmowa o jednostce BOR",
        blurb="Wywiad w formie opowieści z Marcinem „Żukiem” Kowalczykiem — byłym operatorem BOR — o granicy między żołnierzem a operatorem, adrenaliny i rzeczach, o których nie można mówić.",
        genres=["article", "biography"],
        difficulty=7,
        reading_time=14,
        trust="Inspired by reality",
        tags=["polish", "narrative", "interview", "bor"],
        keywords=["BOR", "wywiad", "jednostka specjalna", "adrenalina"],
        revision_notes="Tekst stylizowany na podcast; źródłem jest materiał wideo, nie oficjalny dokument BOR.",
        quiz=[
            QuizQuestion(
                "Jak Żuk wyjaśnia różnicę między żołnierzem a operatorem BOR?",
                [
                    "To zupełnie różne zawody bez wspólnych elementów",
                    "To w praktyce to samo, lecz ze względu na specjalizacje mówi się o operatorze",
                    "Operatorzy nigdy nie używają broni",
                    "Żołnierze nie przechodzą szkoleń specjalnych",
                ],
                "B",
                "Żuk mówi, że to tak naprawdę to samo, tylko ze względu na specjalności używa się określenia operator.",
                "Tak naprawdę to jest to samo",
            ),
            QuizQuestion(
                "W jakim kontekście toczy się rozmowa w tekście?",
                [
                    "W sali sądowej",
                    "W studiu podcastu „Bez Sekretów”",
                    "Na poligonie wojskowym",
                    "W telewizyjnym studiu informacyjnym",
                ],
                "B",
                "Piotr i Marcin rozmawiają w studiu podcastu „Bez Sekretów”.",
                "studio podcastu \"Bez Sekretów\"",
            ),
            QuizQuestion(
                "Co tekst sugeruje o tematach związanych z jednostką?",
                [
                    "Można o wszystkim mówić publicznie bez ograniczeń",
                    "Są rzeczy w jednostce, o których narrator nie będzie mógł powiedzieć",
                    "BOR nie istnieje w Polsce",
                    "Wszyscy operatorzy chcą udzielać wywiadów",
                ],
                "B",
                "Już w podtytule pada zdanie o rzeczach, o których nie można mówić.",
                "O KTÓRYCH NIGDY NIE BĘDĘ MÓGŁ POWIEDZIEĆ",
            ),
        ],
    ),
    "Cień skrzydeł nad oceanem": StoryConfig(
        slug="cien-skrzydel-nad-oceanem",
        subtitle="Przypadek Jamesa Leiningera",
        blurb="Opowieść o chłopcu, który od najmłodszych lat opowiada szczegóły śmierci pilota Jamesa M. Hustona Jr. nad Chichi Jimą — i o rodzicach szukających wyjaśnienia.",
        genres=["article", "popular_science"],
        difficulty=7,
        reading_time=13,
        trust="Inspired by reality",
        tags=["polish", "narrative", "reincarnation", "documentary"],
        keywords=["Leininger", "Huston", "Iwo Jima", "pamięć"],
        revision_notes="Opowieść oparta na publicznie opisywanym przypadku; nie jest tekstem naukowym ani sądowym.",
        quiz=[
            QuizQuestion(
                "Kim był James M. Huston Jr. według tekstu?",
                [
                    "Niemieckim żołnierzem z II wojny",
                    "Pilotem amerykańskiego lotnictwa morskiego zabitym w 1945 roku",
                    "Lekarzem z Luizjany",
                    "Konstruktorem Enigmy",
                ],
                "B",
                "Tekst identyfikuje go jako pilota US Navy zabitego 3 marca 1945 nad Chichi Jimą.",
                "pilotem amerykańskiego lotnictwa morskiego",
            ),
            QuizQuestion(
                "Co dzieje Jamesa budzi u matki w maju 2000 roku?",
                [
                    "Spokojny sen po kolacji",
                    "Koszmar z krzykiem o płomieniach i zablokowanej kabinie",
                    "Radość z nowej zabawki",
                    "Prośbę o wodę",
                ],
                "B",
                "Andrea budzi się na ryk przerażenia; James krzyczy o ogień i zablokowaną owiewkę.",
                "ogień, pamiętał dym",
            ),
            QuizQuestion(
                "Jak tekst opisuje wiedzę Jamesa o poprzednim życiu?",
                [
                    "Rodzice od razu mu o tym opowiedzieli",
                    "Po prostu wiedział, choć nikt mu tego nie powiedział",
                    "Wynika wyłącznie z lekcji w przedszkolu",
                    "Jest wymyślona przez dziennikarzy",
                ],
                "B",
                "Tekst podkreśla: „Ale nikt mu tego nie powiedział. Po prostu wiedział.”",
                "Po prostu wiedział",
            ),
        ],
    ),
    "Dziewczyna z Jełania": StoryConfig(
        slug="dziewczyna-z-jelania",
        subtitle="Powrót do języka i pamięci",
        blurb="Anastazja przyjeżdża z Niemiec do Warszawy, by uczyć się polskiego — i odkrywa więź z miejscem, którego świadomie nie pamięta: Jełaniem.",
        genres=["short_story", "travel"],
        difficulty=5,
        reading_time=11,
        trust="Fiction",
        tags=["polish", "fiction", "narrative", "language-learning"],
        keywords=["Warszawa", "Jełanie", "język polski", "pamięć"],
        quiz=[
            QuizQuestion(
                "Dlaczego Anastazja przyjeżdża do Polski?",
                [
                    "By odwiedzić rodzinę w Jełaniu",
                    "By nauczyć się polskiego bez praktycznego powodu kariery",
                    "By studiować medycynę",
                    "By pracować w taxi",
                ],
                "B",
                "Tekst mówi wprost, że nie ma tu rodziny ani planów kariery — chce mieć język „w sobie”.",
                "żeby nauczyć się polskiego",
            ),
            QuizQuestion(
                "Skąd pochodzi Anastazja i gdzie mieszkała przed przyjazdem?",
                [
                    "Z Polski, mieszkała w Krakowie",
                    "Z Rosji, mieszkała w Niemczech",
                    "Z USA, mieszkała we Francji",
                    "Z Ukrainy, mieszkała w Czechach",
                ],
                "B",
                "Mówi kierowcy, że jest z Rosji, ale mieszka w Niemczech od dziewięciu lat.",
                "Jestem z Rosji, ale mieszkam w Niemczech",
            ),
            QuizQuestion(
                "Jaką książkę czyta Anastazja w pokoju na Pradze?",
                [
                    "„Lalkę” Bolesława Prusa",
                    "„Quo vadis”",
                    "„Pan Tadeusza” w tłumaczeniu",
                    "Podręcznik gramatyki niemieckiej",
                ],
                "A",
                "Wynajęty pokój i lektura „Lalki” w oryginale są opisane wprost.",
                "\"Lalkę\" Bolesława Prusa",
            ),
        ],
    ),
    "Cisza przed burzą": StoryConfig(
        slug="cisza-przed-burza",
        subtitle="Polscy łamacze Enigmy",
        blurb="Opowieść o Marianie Rejewskim i zespole z Biura Szyfrów, którzy zrozumieli logikę Enigmy i zbudowali bombę kryptologiczną — na tle października 1932 w Warszawie.",
        genres=["history", "article"],
        difficulty=8,
        reading_time=12,
        trust="Inspired by reality",
        tags=["polish", "narrative", "enigma", "cryptography"],
        keywords=["Rejewski", "Enigma", "kryptologia", "II wojna światowa"],
        revision_notes="Narracja historyczna oparta na znanych faktach; dialogi i sceny są literacką rekonstrukcją.",
        quiz=[
            QuizQuestion(
                "Jakie podejście Rejewski proponuje wobec Enigmy?",
                [
                    "Analizować wyłącznie przechwycone teksty",
                    "Zrozumieć działanie urządzenia — to matematyka, nie język",
                    "Czekać na komputer cyfrowy",
                    "Zignorować dokumentację z Francji",
                ],
                "B",
                "Rejewski mówi, że trzeba zrozumieć maszynę, bo to matematyka.",
                "Musimy zrozumieć, jak działa samo urządzenie",
            ),
            QuizQuestion(
                "Jaką słabość Niemców odkrywa Rejewski w schematach?",
                [
                    "Losowe połączenia bez powtarzalności",
                    "Porządek alfabetyczny w połączeniach",
                    "Brak wirników",
                    "Używanie tylko jednego klucza rocznie",
                ],
                "B",
                "Tekst wskazuje, że konstruktorzy wybrali najprostsze rozwiązanie — porządek alfabetyczny.",
                "Porządek alfabetyczny",
            ),
            QuizQuestion(
                "Czym jest „bomba kryptologiczna” w tekście?",
                [
                    "Bronią palną używaną przez wywiad",
                    "Elektromechanicznym urządzeniem symulującym wiele Enigm",
                    "Meteorologicznym instrumentem",
                    "Książką instruktażową dla żołnierzy",
                ],
                "B",
                "Bomba symuluje działanie kilku Enigm i automatycznie sprawdza kombinacje.",
                "elektromechaniczne urządzenie",
            ),
        ],
    ),
    "Trzynaście zasad": StoryConfig(
        slug="trzynascie-zasad",
        subtitle="Przewodnik kulturowy dla obcokrajowców",
        blurb="Amerykanka w Polsce uczy się od przyjaciela trzynastu zasad codziennej obecności — od uśmiechu po kolejki, kawę i bezpośredniość.",
        genres=["instruction", "article"],
        difficulty=4,
        reading_time=18,
        trust="Manual / Reference",
        tags=["polish", "reference", "culture", "travel"],
        keywords=["Polska", "kultura", "obyczaje", "poradnik"],
        quiz=[
            QuizQuestion(
                "Jak tekst wyjaśnia polski uśmiech wobec amerykańskiego?",
                [
                    "Polacy uśmiehają się stale jak kelnerzy w USA",
                    "Uśmiech nie jest domyślny — pojawia się, gdy jest ku temu powód",
                    "Uśmiech jest zakazany w miejscach publicznych",
                    "Uśmiech zawsze oznacza flirt",
                ],
                "B",
                "Przyjaciel tłumaczy, że w Polsce uśmiech to nie domyślne ustawienie twarzy.",
                "Uśmiech to nie jest domyślne ustawienie twarzy",
            ),
            QuizQuestion(
                "Dlaczego bohaterka czuje się zagubiona na początku?",
                [
                    "Bo nie zna żadnych polskich słów",
                    "Bo jej amerykański uśmiech nie otwiera kontaktu tak jak w Kalifornii",
                    "Bo nie ma pieniędzy na kawę",
                    "Bo przyjechała do Krakowa zamiast do Warszawy",
                ],
                "B",
                    "Ludzie nie reagują na jej ciągły uśmiech; przyjaciel radzi przestać „wyglądać jak psychol”.",
                "Nikt się do mnie nie uśmiecha",
            ),
            QuizQuestion(
                "Jaki gatunek tekstu to jest?",
                [
                    "Suchy raport policyjny",
                    "Poradnik kulturowy w formie opowieści",
                    "Wiersz epicki",
                    "Transkrypt sądowy",
                ],
                "B",
                "Tekst łączy narrację z kolejnymi „zasadami” obyczajów w Polsce.",
                "TRZYNAŚCIE ZASAD",
            ),
        ],
    ),
    "Dziewczyna, która zniknęła o świcie": StoryConfig(
        slug="dziewczyna-ktora-zniknela-o-swicie",
        subtitle="Śledztwo w pierwszych godzinach",
        blurb="Policjantka Joanna analizuje zaginięcie osiemnastoletniej Agnieszki z Gdyni — od nagrania monitoringu po błędy procedur w kluczowych pierwszych godzinach.",
        genres=["history", "article"],
        difficulty=8,
        reading_time=13,
        trust="Inspired by reality",
        tags=["polish", "narrative", "true-crime", "investigation"],
        keywords=["zaginięcie", "śledztwo", "monitoring", "Gdynia"],
        revision_notes="Inspirowane realnymi mechanizmami śledztw; postacie i dialogi są fikcją literacką.",
        quiz=[
            QuizQuestion(
                "Co wskazuje Joanna na nagraniu monitoringu o stanie Agnieszki?",
                [
                    "Idzie wesoło kontynuować imprezę",
                    "Idzie do domu ze spadkiem czujności — fałszywy syndrom bezpiecznego progu",
                    "Jedzie taksówką",
                    "Rozmawia przez telefon przez cały czas",
                ],
                "B",
                "Joanna mówi o fałszywym syndromie bezpiecznego progu i spadku czujności.",
                "Fałszywy syndrom bezpiecznego progu",
            ),
            QuizQuestion(
                "Dlaczego Joanna uważa, że pierwsze godziny zostały zmarnowane?",
                [
                    "Bo nie było żadnego zgłoszenia",
                    "Bo sprawę potraktowano jak standardową ucieczkę nastolatki",
                    "Bo Agnieszka sama zadzwoniła na policję",
                    "Bo monitoring działał bez przerw",
                ],
                "B",
                "Tekst mówi o standardowej procedurze w sezonie wakacyjnym i braku zabezpieczenia nagrań.",
                "Pierwsze zgłoszenie traktowano jak ucieczkę nastolatki",
            ),
            QuizQuestion(
                "O której godzinie kamera rejestruje ostatni obraz Agnieszki?",
                [
                    "2:00 w nocy",
                    "4:12 nad ranem",
                    "Południe",
                    "22:30",
                ],
                "B",
                "Sekcja „Punkt zero” podaje godzinę 4:12.",
                "Godzina 4:12 nad ranem",
            ),
        ],
    ),
    "Prolog wiatru": StoryConfig(
        slug="prolog-wiatru",
        subtitle="Za kulisami teledysku",
        blurb="Opowieść o nagraniu teledysku do „Kaze no Prologue” — od porannej plaży w Chiba po znaczenie wiatru i nowego początku w karierze Yumiko.",
        genres=["short_story", "biography"],
        difficulty=5,
        reading_time=10,
        trust="Inspired by reality",
        tags=["polish", "narrative", "music", "japan"],
        keywords=["Yumiko", "Japonia", "teledysk", "J-pop"],
        revision_notes="Inspirowane realnym utworem i kontekstem kultury J-pop; sceny są literacką rekonstrukcją.",
        quiz=[
            QuizQuestion(
                "Jak nazywa się utwór, wokół którego toczy się opowieść?",
                [
                    "„Kaze no Prologue”",
                    "„Cisza przed burzą”",
                    "„Zakazana Energia”",
                    "„Prolog wiatru” bez tytułu piosenki",
                ],
                "A",
                "Yumiko słyszy i nagrywa teledysk do „Kaze no Prologue”.",
                "Kaze no Prologue",
            ),
            QuizQuestion(
                "Gdzie odbywają się zdjęcia teledysku?",
                [
                    "Na plaży w Chiba o świcie",
                    "W studiu w Los Angeles",
                    "Na dworcu w Warszawie",
                    "W górach Hokkaido zimą",
                ],
                "A",
                "Menedżer pisze o plaży w Chiba o 5:00 rano.",
                "plaża w Chiba",
            ),
            QuizQuestion(
                "Jakie przesłanie niesie piosenka według Yumiko?",
                [
                    "Że wiatr zawsze wieje i można zacząć od nowa",
                    "Że należy unikać wiatru",
                    "Że kariera muzyczna się kończy",
                    "Że plaża jest niebezpieczna",
                ],
                "A",
                "Tekst mówi, że piosenka dodaje sił i mówi o nowym początku przy otwartym oknie.",
                "zawsze można zacząć od nowa",
            ),
        ],
    ),
    "Siedem gór i jeden ocean": StoryConfig(
        slug="siedem-gor-i-jeden-ocean",
        subtitle="Polska oczami Korei Południowej",
        blurb="Architekt Marek jedzie do Korei Południowej przy kontrakcie muzealnym — i odkrywa kraj, który kojarzy Polskę z Chopinem, Wiedźminem i… tysiącem polskich czołgów.",
        genres=["travel", "article"],
        difficulty=6,
        reading_time=14,
        trust="Inspired by reality",
        tags=["polish", "narrative", "travel", "korea"],
        keywords=["Korea Południowa", "podróż", "kultura", "Polska"],
        quiz=[
            QuizQuestion(
                "Co zaskakuje Marka w nagłówkach z 2022 roku?",
                [
                    "Że Polska kupiła tysiąc czołgów od Korei",
                    "Że Korea Południowa kupiła od Polski tysiąc czołgów",
                    "Że Korea zniknęła z mapy",
                    "Że Marek dostał mandat parkingowy",
                ],
                "B",
                "Czyta o Korei Południowej kupującej od Polski tysiąc czołgów.",
                "Korea Południowa kupiła od Polski tysiąc czołgów",
            ),
            QuizQuestion(
                "Jaki jest powód podróży Marka do Korei?",
                [
                    "Wyjazd turystyczny z rodziną",
                    "Kontrakt na modernizację koreańskiego muzeum",
                    "Nauka języka koreańskiego w szkole",
                    "Start kariery K-pop",
                ],
                "B",
                "Biuro wygrało przetarg na modernizację muzeum — Marek ma jechać na miesiąc.",
                "modernizację jednego z koreańskich muzeów",
            ),
            QuizQuestion(
                "Co Marek znajduje w wynikach wyszukiwania o Polsce?",
                [
                    "Że Koreańczycy nie znają Chopina",
                    "Skojarzenia m.in. z Chopinem, Wiedźminem i Robertem Lewandowskim",
                    "Że Polska nie istnieje w azjatyckich mediach",
                    "Wyłącznie informacje o nauce polskiego",
                ],
                "B",
                "Lista wyników wymienia Chopina, Auschwitz, Lewandowskiego i Wiedźmina.",
                "Lewandowski jest najbardziej znanym Polakiem",
            ),
        ],
    ),
    "Zasady": StoryConfig(
        slug="zasady",
        subtitle="List o decyzjach bez wymówek",
        blurb="Łukasz czyta osobisty mailing Pawła Kadysza o tym, dlaczego ciągłe „zastanawianie się” prowadzi do wymówek — i odkrywa pięć zasad działania zamiast wiecznego wyboru.",
        genres=["instruction", "article"],
        difficulty=4,
        reading_time=8,
        trust="Manual / Reference",
        tags=["polish", "reference", "productivity", "habits"],
        keywords=["produktywność", "nawyki", "decyzje", "mailing"],
        source_label="Collection One manuscript (Paweł Kadysz mailing)",
        availability="adaptation",
        revision_notes="Tekst inspirowany mailingiem Pawła Kadysza; narracja o Łukaszu jest oprawą literacką.",
        quiz=[
            QuizQuestion(
                "Jaki problem Kadysz nazywa w otwarciu listu?",
                [
                    "Brak czasu na czytanie książek",
                    "Ciągłe postanawianie sobie rzeczy, z których nic nie wynika",
                    "Zbyt wiele spotkań w biurze",
                    "Brak dostępu do internetu",
                ],
                "B",
                "Cytowany fragment pyta, jak często postanawiamy sobie coś, z czego nic nie wychodzi.",
                "z czego potem nic nie wychodzi",
            ),
            QuizQuestion(
                "Według listu, co dzieje się, gdy dajemy sobie wybór?",
                [
                    "Umysł natychmiast znajduje wymówki, by czegoś nie zrobić",
                    "Zawsze wybieramy najtrudniejsze zadanie",
                    "Motywacja rośnie bez limitu",
                    "Nie ma to wpływu na działanie",
                ],
                "A",
                "Kadysz pisze, że przy zastanawianiu się umysł szybko znajduje tysiąc wymówek.",
                "tysiąc wymówek by czegoś nie zrobić",
            ),
            QuizQuestion(
                "Co Łukasz robi zamiast pracować, gdy zaczyna się wątpić?",
                [
                    "Szuka w internecie nowych aplikacji i metod",
                    "Idzie spać przez cały dzień",
                    "Dzwoni do szefa po urlop",
                    "Sprzedaje komputer",
                ],
                "A",
                "Zamiast pracować czyta o pracy — nowe aplikacje i lifehacki.",
                "szukał w internecie",
            ),
        ],
    ),
}


def normalize_title(title: str) -> str:
    return title.strip().rstrip(".").strip()


def parse_date_polish(raw: str) -> str:
    m = re.match(r"(\d{2})\.(\d{2})\.(\d{4})", raw.strip())
    if not m:
        return "2026-07-09"
    d, mo, y = m.groups()
    return f"{y}-{mo}-{d}"


def sanitize_text_for_parser(text: str) -> str:
    """reading-pack parser truncates Text at the first '---' rule."""
    lines: list[str] = []
    for line in text.split("\n"):
        if line.strip() == "---":
            if lines and lines[-1] != "":
                lines.append("")
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def unwrap_story_text(body: str) -> str:
    text = body.strip()

    # Remove leading horizontal rules and stray fences before content.
    text = re.sub(r"^```\s*\n", "", text)
    text = re.sub(r"\n```\s*$", "", text)

    # If entire remainder is one fenced block, unwrap it.
    fenced = re.fullmatch(r"```\s*\n(.*)\n```\s*", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)

    # Remove orphan fence lines.
    lines = text.split("\n")
    cleaned: list[str] = []
    for line in lines:
        if line.strip() == "```":
            continue
        cleaned.append(line)
    return "\n".join(cleaned).strip()


def pack_id(slug: str) -> str:
    return f"polish_{slug.replace('-', '_')}"


def format_quiz(questions: list[QuizQuestion]) -> str:
    letters = "ABCD"
    parts = ["## Quiz", "", "**Quiz title:** Sprawdź zrozumienie", ""]
    for i, q in enumerate(questions, 1):
        parts.append(f"### Question {i}")
        parts.append("")
        parts.append(f"**Question:** {q.question}")
        parts.append("")
        parts.append("**Answers:**")
        for j, ans in enumerate(q.answers):
            parts.append(f"- {letters[j]}) {ans}")
        parts.append("")
        parts.append(f"**Correct:** {q.correct}")
        parts.append(f"**Explanation:** {q.explanation}")
        if q.text_reference:
            parts.append(f"**Text reference:** {q.text_reference}")
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def build_reading_pack(title: str, cfg: StoryConfig, text: str, source_meta: dict) -> str:
    genres = ", ".join(cfg.genres)
    tags = ", ".join(cfg.tags)
    keywords = ", ".join(cfg.keywords)
    pack = pack_id(cfg.slug)

    source_url_line = (
        f"**URL:** {source_meta['url']}"
        if source_meta.get("url")
        else "**URL:** *(none — mailing reference)*"
    )
    source_desc = source_meta.get("note", "Materiał wideo — źródło redakcyjne Collection One.")
    if source_meta.get("url"):
        source_desc = "Materiał wideo — źródło redakcyjne Collection One."

    revision = cfg.revision_notes or (
        f"Collection One migration (Phase 39). Trust: {cfg.trust}."
    )

    youtube_transparency = ""
    if source_meta.get("url"):
        youtube_transparency = (
            f"\n**Source video:** {source_meta['url']}  \n"
            f"**Source date (manuscript):** {source_meta.get('manuscript_date', '')}"
        )

    return f"""# {title.strip()}

## Metadata

**Pack ID:** `{pack}`  
**Version:** 1.0.0  

**Title:** {title.strip()}  
**Subtitle:** {cfg.subtitle}  
**Blurb:** {cfg.blurb}

**Genres:** {genres}  
**Series:** Collection One  
**Audience:** {cfg.audience}  

**Difficulty:** {cfg.difficulty} (of 10)  
**Reader difficulty:** {"★" * max(1, cfg.difficulty // 2)}{"☆" * (5 - max(1, cfg.difficulty // 2))}  
**Estimated reading time:** {cfg.reading_time} minutes  

**Publication date:** *(original — 2026)*  
**Historical period:** *(varies — see text)*  

**Original language:** pl  
**Translation summary:** {title.strip()} — Collection One official reading pack (Polish).  

**Writing system:** glagolitic  
**Recommended profile:** polish_default  
**Recommended level:** {cfg.recommended_level}  

**Tags:** {tags}  

**Keywords:** {keywords}  

**Editorial notes:** Migrated from Collection One manuscript. Full text preserved — not abridged.

---

## Editorial Transparency

**Created by:** AlephBits Editorial  
**Editor:** AlephBits Editorial  
**LLM assisted:** yes  
**LLM model:** Claude (editorial migration)  
**Human reviewed:** yes — 2026-07-09  
**Trust classification:** {cfg.trust}  
**License:** CC0 1.0 Universal (SPDX: CC0-1.0)  
**License URL:** https://creativecommons.org/publicdomain/zero/1.0/  
**Revision notes:** {revision}
{youtube_transparency}

### Revision history

| Version | Date | Note |
|---------|------|------|
| 1.0.0 | 2026-07-09 | Collection One migration (Phase 39) |

---

## Sources

### Source 1: {cfg.source_label}

**Author:** AlephBits Editorial (adaptation)  
{source_url_line}  
**License:** CC0 1.0 Universal (text); source material per original availability  
**Retrieval date:** {source_meta.get('date_iso', '2026-07-09')}  
**Availability:** {cfg.availability}  
**Deprecated:** no  
**Editor notes:** {source_desc}

---

## Text

{text}

---

{format_quiz(cfg.quiz)}
---

## Future Extensions

### Images
*(none)*

### Illustrations
*(none)*

### Audio narration
*(none)*

### Pronunciation
*(none)*

### Handwriting
*(none)*

### Exercises
*(none)*

### Vocabulary
*(none)*
"""


def split_stories(markdown: str) -> list[tuple[str, str]]:
    lines = markdown.replace("\r\n", "\n").split("\n")
    stories: list[tuple[str, str]] = []
    current_title: str | None = None
    current_lines: list[str] = []

    for line in lines:
        if line.startswith("## "):
            if current_title is not None:
                stories.append((current_title, "\n".join(current_lines)))
            current_title = line[3:].strip()
            current_lines = []
        elif current_title is not None:
            current_lines.append(line)

    if current_title is not None:
        stories.append((current_title, "\n".join(current_lines)))
    return stories


def parse_source(body: str) -> tuple[dict, str]:
    pattern = re.compile(
        r"```\s*(?:Source|source)\s*\n(.*?)\n```",
        re.DOTALL | re.IGNORECASE,
    )
    match = pattern.search(body)
    meta: dict = {"date_iso": "2026-07-09", "url": None, "manuscript_date": ""}
    remaining = body
    if match:
        inner = match.group(1).strip()
        remaining = (body[: match.start()] + body[match.end() :]).strip()
        arrow = re.search(r"(\d{2}\.\d{2}\.\d{4})\s*->\s*(.+)", inner, re.DOTALL)
        if arrow:
            meta["manuscript_date"] = arrow.group(1).strip()
            meta["date_iso"] = parse_date_polish(meta["manuscript_date"])
            target = arrow.group(2).strip()
            url_match = re.search(r"https?://\S+", target)
            if url_match:
                meta["url"] = url_match.group(0)
            else:
                meta["note"] = target
    return meta, remaining


def main() -> None:
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    stories = split_stories(manuscript)

    if not OUTPUT_ROOT.exists():
        OUTPUT_ROOT.mkdir(parents=True)

    migrated = 0
    for raw_title, body in stories:
        title = normalize_title(raw_title)
        # Match config — allow trailing period mismatch
        cfg = None
        for key, value in STORIES.items():
            if normalize_title(key) == title or key.strip().rstrip(".") == title:
                cfg = value
                title = key.rstrip(".").strip() if key.endswith(".") else key
                if title.endswith("."):
                    title = title.rstrip(".").strip()
                break
        if cfg is None:
            raise SystemExit(f"No config for story: {raw_title!r}")

        source_meta, after_source = parse_source(body)
        text = sanitize_text_for_parser(unwrap_story_text(after_source))
        if not text:
            raise SystemExit(f"Empty text for {title}")

        out_dir = OUTPUT_ROOT / cfg.slug
        out_dir.mkdir(parents=True, exist_ok=True)
        pack_md = build_reading_pack(title, cfg, text, source_meta)
        (out_dir / "reading-pack.md").write_text(pack_md, encoding="utf-8")
        migrated += 1
        print(f"✓ {cfg.slug} ({len(text.split())} words)")

    print(f"\nMigrated {migrated} packs to {OUTPUT_ROOT}")


if __name__ == "__main__":
    main()
