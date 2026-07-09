#!/usr/bin/env python3
"""Generic AlephBits collection migrator for production Reading Packs."""

from __future__ import annotations

import math
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

OUTPUT_ROOT = Path(__file__).resolve().parent.parent / "official/glagolitic/pl"
TODAY = "2026-07-09"


@dataclass
class QuizQuestion:
    question: str
    answers: list[str]
    correct: str
    explanation: str
    text_reference: str = ""


@dataclass
class StoryConfig:
    subtitle: str
    blurb: str
    genres: list[str]
    difficulty: int
    trust: str
    tags: list[str]
    keywords: list[str]
    recommended_level: int
    revision_notes: str = ""
    audience: str = "adult readers"
    source_label: str = ""
    availability: str = "adaptation"
    quiz: list[QuizQuestion] = field(default_factory=list)


@dataclass
class CollectionConfig:
    key: str
    title: str
    manuscript: Path
    phase_label: str
    source_label: str
    stories: dict[str, StoryConfig]


def q(question: str, answers: list[str], correct: str, explanation: str, ref: str = "") -> QuizQuestion:
    return QuizQuestion(question, answers, correct, explanation, ref)


COLLECTIONS = {
    "collection3": CollectionConfig(
        key="collection3",
        title="Collection Three",
        manuscript=Path(
            "/Users/admin/Developer/MiscellaneousNotes/AwesomeVault/!Apps/App Ideas/alephBits/CollectionThree.md"
        ),
        phase_label="Phase 40",
        source_label="Collection Three manuscript",
        stories={
            "Czarny mnich z Nikiszowca": StoryConfig(
                subtitle="Legenda i pamięć Nikiszowca",
                blurb="Tomek wraca do Nikiszowca, by zrozumieć legendę Czarnego Mnicha i odkrywa, że opowieść o zjawie jest także opowieścią o pamięci górniczej dzielnicy.",
                genres=["legend", "history"],
                difficulty=5,
                trust="historical_fiction",
                tags=["polish", "nikiszowiec", "legend", "silesia", "memory"],
                keywords=["Nikiszowiec", "Czarny Mnich", "Katowice", "kopalnia"],
                recommended_level=3,
                revision_notes="Legenda osadzona w realnej historii Nikiszowca i kopalni; wymaga ręcznej oceny proporcji między faktem a lokalnym podaniem.",
                quiz=[
                    q("Dlaczego Tomek jako dziecko czuł się w Nikiszowcu obco?", ["Bo nie znał języka śląskiego", "Bo nowe osiedle i jego układ wydawały mu się pułapką z czerwonej cegły", "Bo od razu chciał pracować w kopalni", "Bo nie lubił kościołów"], "B", "Na początku tekst podkreśla przeprowadzkę, obcość miejsca i poczucie uwięzienia.", "pułapce z czerwonej cegły"),
                    q("Gdzie Tomek po raz pierwszy widzi postać Czarnego Mnicha?", ["Na dworcu w Katowicach", "Przy kościele Świętej Anny, w cieniu bramy", "Na dachu familoka", "W kopalnianej windzie"], "B", "Pierwsze spotkanie ma miejsce przy kościele Świętej Anny, obok jednej z bram.", "Przy kościele Świętej Anny"),
                    q("Jaką rolę pełni w tekście kopalnia Gisze/Wieczorek?", ["Jest tylko tłem bez znaczenia", "Stanowi matkę żywicielkę i źródło losu mieszkańców", "Jest muzeum odwiedzanym przez turystów", "Zostaje opisana jako prywatna galeria"], "B", "Tekst mówi wprost, że kopalnia dawała pracę, mieszkania i decydowała o życiu mieszkańców.", "była matką żywicielką"),
                    q("Co oznacza gest Mnicha podczas drugiego spotkania z Tomkiem?", ["Zaproszenie do zejścia pod ziemię", "Wskazanie na kościół i pamięć miejsca", "Groźbę wobec mieszkańców", "Prośbę o pieniądze"], "B", "Mnich wskazuje kościół, a Tomek odczytuje to jako znak pamięci o tych, którzy odeszli.", "wskazała w stronę kościoła"),
                    q("Jak zmienia się stosunek Tomka do Nikiszowca pod koniec opowieści?", ["Nadal chce stamtąd uciec", "Zaczyna widzieć w nim dom i przewodnika po własnej historii", "Postanawia sprzedać mieszkanie rodziców", "Przestaje wierzyć w jakiekolwiek legendy"], "B", "Z miejsca-pułapki Nikiszowiec staje się dla niego domem i nośnikiem pamięci.", "stało się jego domem"),
                ],
            ),
            "Czarny Kodeks": StoryConfig(
                subtitle="Vodou, Haiti i długie życie prawa",
                blurb="Historyk Janusz bada losy Czarnego Kodeksu, rewolucji haitańskiej i Vodou, odkrywając jak prawo, religia i kolonialna przemoc splatają się przez stulecia.",
                genres=["history", "article"],
                difficulty=7,
                trust="history",
                tags=["haiti", "vodou", "colonialism", "history", "law"],
                keywords=["Czarny Kodeks", "Haiti", "Vodou", "niewolnictwo"],
                recommended_level=4,
                revision_notes="Tekst miesza fakty historyczne z reportażową narracją i zawiera fragment wymagający ręcznego sprawdzenia ciągłości redakcyjnej.",
                quiz=[
                    q("Co sprawia, że Janusz zaczyna badać Czarny Kodeks?", ["Odnajduje rodzinny pamiętnik z Haiti", "Czyta informację, że dokument obowiązywał formalnie do 28 maja 2026 roku", "Dostaje grant na badanie prawa polskiego", "Słyszy o tym w kościele w Krakowie"], "B", "Impulsem jest informacja o zaskakująco późnym uchyleniu dokumentu.", "formalnie obowiązywał we Francji do 28 maja 2026 roku"),
                    q("Jaką funkcję pełni Vodou w interpretacji Jean-Pierre’a?", ["Wyłącznie egzotyczną religię z filmów", "Narzędzie przetrwania, porządku i oporu", "Prywatny kult kilku rodzin", "Religię importowaną z Polski"], "B", "Jean-Pierre przedstawia Vodou jako system społeczny i narzędzie przetrwania.", "Było narzędziem przetrwania"),
                    q("Dlaczego Bois Caïman jest ważne w opowieści?", ["To miejsce narodzin polskiej emigracji", "To miejsce rytuału poprzedzającego rewolucję haitańską", "To dawna siedziba Napoleona", "To muzeum prawa kolonialnego"], "B", "Jean-Pierre opisuje Bois Caïman jako miejsce rytuału związanego z początkiem powstania.", "zapoczątkował rewolucję haitańską"),
                    q("Jak tekst interpretuje związek Matki Boskiej Częstochowskiej z Erzulie Dantor?", ["Jako błąd tłumaczenia historycznego", "Jako przykład religijnego synkretyzmu i przetrwania", "Jako dowód dominacji Watykanu", "Jako nowoczesną kampanię marketingową"], "B", "Wątek służy pokazaniu, jak symbole religijne zostały wchłonięte i przekształcone.", "To jest synkretyzm. To jest przetrwanie."),
                    q("Jaką ogólniejszą lekcję Janusz wynosi z podróży?", ["Że historia niewolnictwa należy wyłącznie do przeszłości", "Że duch Czarnego Kodeksu trwa w uprzedzeniach i sposobach traktowania 'innych'", "Że Vodou da się wyjaśnić tylko magią", "Że Polska i Haiti nie mają żadnych punktów stycznych"], "B", "W zakończeniu Janusz pisze o trwaniu ducha tego prawa w dzisiejszych uprzedzeniach.", "jego duch wciąż żyje"),
                ],
            ),
            "Koniec epoki pudełek": StoryConfig(
                subtitle="Fizyczne gry kontra cyfrowa własność",
                blurb="Adam obserwuje bunt graczy po decyzji Sony o końcu nowych wydań płytowych i zaczyna widzieć w sporze o pudełka walkę o własność, dostęp i prawa konsumentów.",
                genres=["article"],
                difficulty=5,
                trust="technology",
                tags=["gaming", "playstation", "digital-ownership", "consumer-rights", "media"],
                keywords=["Sony", "PlayStation", "płyty", "własność cyfrowa"],
                recommended_level=3,
                revision_notes="Tekst publicystyczny o zmianie modelu dystrybucji; wymaga ręcznego sprawdzenia szczegółów branżowych i dat komunikatów.",
                quiz=[
                    q("Co uruchamia główny konflikt w opowieści Adama?", ["Premiera nowej konsoli Nintendo", "Informacja, że Sony kończy produkcję płyt dla nowych gier od 2028 roku", "Podwyżka cen telewizorów", "Zamknięcie serwerów Steam"], "B", "To nagłówek o końcu nowych fizycznych wydań budzi jego reakcję.", "Sony kończy produkcję płyt"),
                    q("Dlaczego zdanie o „odwoływalnej licencji” tak mocno działa na Adama?", ["Bo nigdy nie kupował gier cyfrowych", "Bo uświadamia mu różnicę między dostępem a faktycznym posiadaniem", "Bo chce handlować licencjami", "Bo dotyczy wyłącznie filmów"], "B", "Adam łączy to z ryzykiem utraty dostępu do kupionych treści.", "Cyfrowe zakupy to nie własność"),
                    q("Jaką pierwszą konkretną decyzję podejmuje Adam po ogłoszeniu Sony?", ["Sprzedaje wszystkie gry na płycie", "Anuluje subskrypcję PlayStation Plus", "Kupuje dodatkową konsolę", "Przestaje używać internetu"], "B", "W sekcji o subskrypcji wchodzi w ustawienia konta i rezygnuje.", "Kliknął \"Tak\""),
                    q("Jaką szerszą stawkę dostrzega Adam po wypowiedziach Ybarry i Mélenchona?", ["Spór o kolor pudełek", "Pytanie o prawa konsumentów i przyszłość cyfrowej własności", "Wyłącznie francuską kampanię wyborczą", "Wojnę między PC a mobilkami"], "B", "Od fanowskiej złości przechodzi do sporu o własność cyfrową i kulturę.", "spór o prawa konsumentów"),
                    q("Co wyraża wiralowy post Adama pod koniec?", ["Złość na wszystkie gry sieciowe", "Gotowość rezygnacji z przyszłej konsoli, jeśli model własności się nie zmieni", "Prośbę o darmowe gry od Sony", "Plan otwarcia sklepu z płytami"], "B", "Pisze, że nie kupi PS6, jeśli Sony zrealizuje ten plan.", "PS6 będzie pierwszą konsolą, której nie kupię"),
                ],
            ),
            "Czarny rynek tokenów": StoryConfig(
                subtitle="API, wyciek i geopolityka dostępu",
                blurb="Po przypadkowym wycieku klucza API Adam odkrywa globalny czarny rynek dostępu do modeli AI i rozumie, że za nielegalnym obiegiem tokenów stoją także bariery geograficzne i systemowe.",
                genres=["article"],
                difficulty=6,
                trust="technology",
                tags=["ai", "api", "security", "openai", "black-market"],
                keywords=["tokeny AI", "API", "bezpieczeństwo", "GitHub"],
                recommended_level=4,
                revision_notes="Tekst łączy edukację bezpieczeństwa z narracją społeczną; warto ręcznie sprawdzić brand-specific details and phrasing.",
                quiz=[
                    q("Jaki błąd uruchamia kryzys Adama?", ["Udostępnia hasło do banku na Slacku", "Wrzuca klucz API do publicznego repozytorium GitHub", "Kupuje konto na czarnym rynku", "Wyłącza 2FA"], "B", "Wyciek klucza API do publicznego repozytorium jest bezpośrednią przyczyną nadużyć.", "wrzucił go na publicznego GitHub'a"),
                    q("Co Adam odkrywa, analizując nietypowe zużycie tokenów?", ["Że OpenAI źle policzyło fakturę", "Że jego klucz trafił do systemu pośredników sprzedających tani dostęp", "Że firma testowała nowe modele", "Że korzystał z konta jego współpracownik"], "B", "Na forach znajduje oferty tanich tokenów i rozumie mechanizm pośredników.", "stacje przesiadkowe"),
                    q("Jaką rolę pełnią proxy rezydencyjne w opisywanym procederze?", ["Służą wyłącznie do legalnego hostingu", "Pomagają ukrywać ruch, wykorzystując łącza zwykłych użytkowników", "Przyspieszają trening modeli", "Blokują spam na forach"], "B", "Tekst opisuje je jako sposób maskowania ruchu przez infrastrukturę zwykłych ludzi.", "maskowania swojego ruchu"),
                    q("Dlaczego rozmowa z Li Wei zmienia sposób myślenia Adama?", ["Bo Li Wei oddaje mu wszystkie pieniądze", "Bo pokazuje ludzką stronę nielegalnego rynku i problem barier dostępu", "Bo okazuje się policjantem", "Bo proponuje wspólny startup"], "B", "Adam zaczyna widzieć nie tylko oszustwo, ale też ludzi wypchniętych poza legalny dostęp.", "To system jest zepsuty"),
                    q("Jaką praktyczną lekcję Adam wyciąga z całej historii?", ["Trzeba przestać używać API", "Bezpieczeństwo wymaga i narzędzi, i świadomości systemowych zagrożeń", "Najlepiej pracować tylko offline", "Nigdy nie używać GitHuba"], "B", "Przechodzi na manager sekretów, monitoring i edukację innych programistów.", "Zaczął korzystać z menedżera sekretów"),
                ],
            ),
            "Mamy trupa i co dalej": StoryConfig(
                subtitle="Żałoba, wybór i usługa pogrzebowa",
                blurb="Po śmierci matki Tomasz bezradnie wchodzi w kosztowny rytuał pogrzebu, a dopiero później odkrywa, że żałoba nie musi oznaczać zgody na wszystko, co proponuje zakład pogrzebowy.",
                genres=["instruction", "article"],
                difficulty=5,
                trust="guide",
                tags=["funeral", "grief", "guide", "consumer-rights", "death"],
                keywords=["pogrzeb", "żałoba", "balsamacja", "Funerarium"],
                recommended_level=3,
                revision_notes="Temat wrażliwy; warto ręcznie sprawdzić zgodność praktycznych sugestii z aktualnymi regulacjami i lokalnymi zwyczajami.",
                quiz=[
                    q("Dlaczego Tomasz zgadza się na kosztowne opcje w zakładzie pogrzebowym?", ["Bo wcześniej porównał wszystkie oferty", "Bo w żałobie ufa, że proponowane elementy są konieczne do godnego pożegnania", "Bo miał specjalne ubezpieczenie", "Bo matka wszystko zapisała w testamencie"], "B", "Tekst pokazuje jego zagubienie i podatność na sugestie w chwili świeżej straty.", "chciał, żeby mama wyglądała dobrze"),
                    q("Co najbardziej zmienia jego spojrzenie kilka tygodni później?", ["Artykuł w gazecie o kremacji", "Rozmowa z Magdą o tańszych i ekologicznych alternatywach", "Telefon z banku", "List od księdza"], "B", "Magda po raz pierwszy uświadamia mu, że istniały inne rozwiązania.", "pogrzeb ekologiczny"),
                    q("Jaką rolę pełni spotkanie fundacji Funerarium?", ["Przekonuje go do zakupu droższej urny", "Pokazuje, że rodzina ma prawo pytać, wybierać i reklamować źle wykonaną usługę", "Zakazuje dzieciom udziału w pogrzebach", "Namawia go do przeprowadzki"], "B", "Agnes Tołoczmańska mówi o prawie wyboru i prawach konsumenta.", "Pogrzeb to usługa"),
                    q("Jaką szerszą zmianę Tomasz wprowadza po tej edukacji?", ["Przestaje chodzić na cmentarz", "Zaczyna rozmawiać z bliskimi, także z dziećmi, o śmierci i wyborach pogrzebowych", "Zakłada firmę pogrzebową", "Rezygnuje z książek"], "B", "Po lekturze i spotkaniu zaczyna oswajać temat śmierci w rodzinie.", "Zaczął rozmawiać o tym"),
                    q("Jaki główny wniosek zamyka opowieść Tomasza?", ["Najlepiej nigdy nie organizować pogrzebów samodzielnie", "W sytuacji niewiedzy trzeba pytać i domagać się alternatyw", "Wysoka cena zawsze oznacza godność", "Dzieci nie powinny znać tematu śmierci"], "B", "Refleksja końcowa sprowadza się do prawa do pytań i wyboru.", "masz prawo do wyboru"),
                ],
            ),
            "Boliewicz": StoryConfig(
                subtitle="Wałęsa między legendą a cieniem Bolka",
                blurb="Narracja wokół wypowiedzi Antoniego Dudka prowadzi przez sprzeczne warstwy biografii Lecha Wałęsy: bohaterstwo, współpracę z SB, nieudaną prezydenturę i trudne dziedzictwo.",
                genres=["biography", "history"],
                difficulty=7,
                trust="biography",
                tags=["walesa", "solidarity", "sb", "biography", "poland"],
                keywords=["Wałęsa", "Bolek", "Solidarność", "Antoni Dudek"],
                recommended_level=4,
                revision_notes="Biografia polityczna oparta na interpretacji historyka; wymaga ręcznego sprawdzenia cytatów i delikatności wobec spornych ocen.",
                quiz=[
                    q("Jak Antoni Dudek proponuje patrzeć na Wałęsę?", ["Wyłącznie jak na zdradzieckiego agenta", "Ani wyłącznie przez różowe, ani wyłącznie przez czarne okulary", "Tylko jak na świętego bohatera", "Wyłącznie przez pryzmat Nobla"], "B", "To podstawowa teza otwierająca i zamykająca cały tekst.", "nie patrzeć na Wałęsę albo wyłącznie przez różowe"),
                    q("Co tekst uznaje za najważniejszy powód pozytywnego bilansu życia Wałęsy?", ["Jego prezydenturę po 1990 roku", "Rolę odegraną w latach 80. i Solidarności", "Wyłącznie Pokojową Nagrodę Nobla", "Działalność po 2000 roku"], "B", "Dudek mówi, że pozytywny bilans wynika przede wszystkim z lat 80.", "bilans życia Wałęsy jest pozytywny z powodu lat 80"),
                    q("Jaki problem wiąże się z pseudonimem „Bolek”?", ["Dotyczy wyłącznie fałszywej legendy internetowej", "Odnosi się do współpracy Wałęsy z SB w pierwszej połowie lat 70.", "To kryptonim strajku z 1980 roku", "To nazwa partii politycznej"], "B", "Sekcja „Bolek” opisuje współpracę i jej moralny ciężar.", "tajny współpracownik o pseudonimie \"Bolek\""),
                    q("Dlaczego prezydentura Wałęsy wypada w tekście słabo?", ["Bo nie chciał startować w wyborach", "Bo nie rozumiał roli prezydenta w systemie parlamentarnym i destabilizował politykę", "Bo od razu wyemigrował", "Bo odrzucił konstytucję w referendum"], "B", "Dudek wskazuje brak rozumienia ustroju i konfliktowość prezydentury.", "kompletnie nie rozumiał roli prezydenta"),
                    q("Co według tekstu szczególnie zaszkodziło późniejszemu wizerunkowi Wałęsy?", ["Wyłącznie działalność Zachodu", "Nieumiejętność przyznania się do błędów i własna megalomania", "Brak wykształcenia technicznego", "Odmowa przyjęcia Nobla"], "B", "Dudek podkreśla, że Wałęsa sam sobie zaszkodził po odejściu z urzędu.", "Wałęsa sobie sam najbardziej zaszkodził"),
                ],
            ),
            "Misja która pękła": StoryConfig(
                subtitle="Misja, wypalenie i kontekst w erze AI",
                blurb="Marek, właściciel dojrzałej firmy konsultingowej, konfrontuje się z pęknięciem między misją a biznesem, zjawiskiem AI Brain Fry i potrzebą działania we własnym kontekście zamiast według cudzych wzorów.",
                genres=["article", "instruction"],
                difficulty=6,
                trust="guide",
                tags=["business", "ai", "burnout", "mission", "management"],
                keywords=["misja firmy", "AI Brain Fry", "wypalenie", "kontekst"],
                recommended_level=4,
                revision_notes="Tekst ma charakter doradczy i eseistyczny; niektóre liczby oraz przykłady biznesowe warto ręcznie sprawdzić.",
                quiz=[
                    q("Jaką sprzeczność Marek dostrzega, patrząc na własną firmę po latach?", ["Między biurami w różnych miastach", "Między pierwotną misją a rzeczywistością działania nastawioną coraz bardziej na wypłatę i wzrost", "Między papierowymi a cyfrowymi dokumentami", "Między IT a sprzedażą"], "B", "To pęknięcie między ideą a praktyką uruchamia całą opowieść.", "misja ... gdzieś po drodze się wypaczyła"),
                    q("Dlaczego historia OpenAI tak mocno porusza Marka?", ["Bo chce kupić akcje Microsoftu", "Bo widzi w niej odbicie własnego konfliktu między misją a biznesem", "Bo planuje zwolnić zarząd", "Bo nie lubi startupów"], "B", "W wydarzeniach wokół Sama Altmana rozpoznaje własne pytania o sens i odpowiedzialność.", "Czy my też straciliśmy misję?"),
                    q("Czym w tekście jest AI Brain Fry?", ["Nowym algorytmem rankingowym", "Zmęczeniem psychicznym wynikającym z ciągłego żonglowania narzędziami AI", "Programem do automatyzacji pracy", "Rodzajem awarii serwera"], "B", "Raport i rozmowa z Agnieszką definiują to jako przeciążenie poznawcze.", "zmęczenie psychiczne od żonglowania narzędziami AI"),
                    q("Jakie rozwiązanie Marek proponuje wobec chaosu narzędzi AI?", ["Śledzić każdą nowinkę jeszcze szybciej", "Wybrać kilka narzędzi naprawdę ważnych i odpuścić FOMO", "Zakazać AI w firmie", "Oddać decyzję wyłącznie działowi HR"], "B", "Jego receptą jest ograniczenie liczby narzędzi i wspólna strategia.", "Nie przestać. Ale przestać gonić."),
                    q("Jaką rolę odgrywa „kontekst” w ostatniej części tekstu?", ["Jest nazwą nowego produktu firmy", "Przypomina, że rozwiązania trzeba dopasować do skali, rynku i realiów własnej firmy", "Oznacza tylko sytuację polityczną USA", "Służy do wyjaśniania księgowości"], "B", "Marek tłumaczy, że wiedza z wielkich korporacji nie działa automatycznie wszędzie.", "To, co działa u Google, nie musi działać u ciebie"),
                ],
            ),
            "Dlaczego Fale Radiowe Przenikają Przez Ściany, a Światło Nie?": StoryConfig(
                subtitle="Opowieść o widmie elektromagnetycznym i materii",
                blurb="Popularnonaukowa opowieść prowadzi od Maxwella i Plancka przez strukturę atomu aż po odpowiedź, dlaczego ściana jest prawie przezroczysta dla fal radiowych, a skutecznie zatrzymuje światło widzialne.",
                genres=["popular_science", "article"],
                difficulty=7,
                trust="science",
                tags=["physics", "electromagnetism", "feynman", "atoms", "light"],
                keywords=["fale radiowe", "światło", "Maxwell", "Planck"],
                recommended_level=4,
                revision_notes="Tekst popularyzuje fizykę przez obrazy i metafory; wymaga ręcznej oceny kilku kosmologicznych uproszczeń.",
                quiz=[
                    q("Jaka podstawowa teza otwiera wyjaśnienie różnicy między radiem a światłem?", ["To dwa całkiem różne zjawiska", "Oba należą do widma elektromagnetycznego i różnią się częstotliwością", "Radio jest falą mechaniczną", "Światło nie ma związku z energią"], "B", "Autor opiera wyjaśnienie na wspólnej naturze fal elektromagnetycznych.", "światło i fale radiowe to to samo zjawisko"),
                    q("Jak tekst opisuje twardość materii na poziomie atomowym?", ["Jako efekt stykania się pełnych kulek materii", "Jako skutek odpychania pól elektromagnetycznych między chmurami elektronowymi", "Jako działanie grawitacji w stole", "Jako właściwość drewna i betonu niezależną od atomów"], "B", "Wyjaśnienie twardości odwołuje się do odpychania elektronów, nie do zwartej bryły.", "elektrony nigdy tak naprawdę nie dotykają"),
                    q("Po co w tekście pojawia się równanie E = h × f?", ["Aby policzyć wagę ściany", "Aby pokazać, że energia fotonu rośnie wraz z częstotliwością", "Aby wyjaśnić temperaturę wrzenia wody", "Aby opisać ruch planet"], "B", "Równanie Plancka tłumaczy różnicę energetyczną między fotonami radiowymi i widzialnymi.", "Im wyższa częstotliwość, tym większa energia"),
                    q("Dlaczego fale radiowe przechodzą przez wiele ścian łatwiej niż światło widzialne?", ["Bo są szybsze od światła", "Bo ich fotony mają zbyt małą energię, by pobudzić elektrony materiału", "Bo ściany zawierają tylko metal", "Bo radio omija budynki dzięki grawitacji"], "B", "Sedno wyjaśnienia polega na niedopasowaniu energetycznym do poziomów elektronów.", "elektrony ... po prostu je ignorują"),
                    q("Jaką szerszą lekcję o rzeczywistości wyciąga tekst z tego przykładu?", ["Że świat jest iluzją i nic nie istnieje", "Że ludzka percepcja obejmuje tylko mały fragment znacznie bogatszego świata fizycznego", "Że tylko to, co widzialne, jest realne", "Że fale radiowe są ważniejsze od światła"], "B", "Końcowe partie podkreślają ograniczoność naszych zmysłów wobec pełnego widma i struktury materii.", "Rzeczywistość jest zawsze znacznie szersza"),
                ],
            ),
            "Metoda Feynmana": StoryConfig(
                subtitle="Fizyka, świadomość i granica interpretacji",
                blurb="Profesor Marek, poruszony komentarzami pod filmem o fizyce, zaczyna łączyć naukowe pojęcia z pytaniami o świadomość, śmierć, dobro i zło — aż sam dochodzi do granicy między wyjaśnieniem a metaforą.",
                genres=["popular_science", "article"],
                difficulty=8,
                trust="opinion",
                tags=["feynman", "consciousness", "philosophy", "physics", "essay"],
                keywords=["Feynman", "świadomość", "atomy", "dobro i zło"],
                recommended_level=5,
                revision_notes="Esej spekulatywny: naukowe pojęcia są zestawiane z filozofią i duchowością, więc wymaga ręcznego rozdzielenia nauki od interpretacji.",
                quiz=[
                    q("Co uruchamia rozważania Marka w tej opowieści?", ["Awaria laboratorium", "Komentarze widzów pytających o zło, świadomość i fizykę", "List od noblisty", "Nowy grant badawczy"], "B", "To komentarze pod jego filmem wytrącają go z naukowej rutyny.", "te komentarze – o dobro i zło"),
                    q("Jaką granicę Marek zaczyna dostrzegać jako fizyk?", ["Że matematyka nigdy nie działa", "Że wzory nie wystarczają do pełnego wyjaśnienia pytań moralnych i egzystencjalnych", "Że nie da się mówić o atomach publicznie", "Że świadomość można już dokładnie zmierzyć"], "B", "Tekst pokazuje napięcie między ścisłym opisem a pytaniami o sens.", "one nie mieściły się w równaniach"),
                    q("Do czego prowadzi Marka powrót do notatnika z młodości?", ["Do odrzucenia całej fizyki kwantowej", "Do spekulacji o związku myśli, częstotliwości i świadomości", "Do napisania pracy o ekonomii", "Do zakupu nowego radia"], "B", "Stare notatki przywracają mu intuicję łączenia fal i umysłu.", "Czy to możliwe, że to, co nazywamy świadomością"),
                    q("Co Marek uznaje za ważne przesłanie fizyki wobec śmierci?", ["Że można empirycznie dowieść reinkarnacji", "Że materia i energia nie znikają, lecz się przekształcają", "Że śmierć jest wyłącznie błędem biologii", "Że atomy przestają istnieć"], "B", "W filmie tłumaczy zachowanie energii i obieg atomów po śmierci.", "Nic nie znika. Wszystko się przekształca."),
                    q("Dlaczego ten tekst wymaga ostrożnej lektury jako materiał popularnonaukowy?", ["Bo nie zawiera żadnych naukowych pojęć", "Bo przechodzi od fizyki do metaforycznych i filozoficznych interpretacji, których sam Marek nie może dowieść", "Bo zaprzecza istnieniu atomów", "Bo opisuje wyłącznie religię"], "B", "Narracja świadomie przesuwa się od nauki do spekulacji i autorefleksji.", "Nie wiem. Nikt nie wie."),
                ],
            ),
            "Cena widoku": StoryConfig(
                subtitle="Hotel, przeciek i nocna decyzja",
                blurb="Pracownik nocnej zmiany w nadmorskim hotelu obserwuje pękanie luksusowej fasady i po spotkaniu z tajemniczym projektantem decyduje, że nie będzie już dłużej współuczestniczył w kłamstwie.",
                genres=["short_story", "article"],
                difficulty=6,
                trust="inspired_by_real_events",
                tags=["hotel", "whistleblowing", "coast", "labour", "scandal"],
                keywords=["hotel", "klimatyzacja", "morze", "list do dyrekcji"],
                recommended_level=4,
                revision_notes="Reportażowa fikcja inspirowana medialnym kryzysem hotelowym; wymaga ręcznej oceny ryzyka odniesień do realnych podmiotów.",
                quiz=[
                    q("Jaką podstawową sprzeczność przeżywa narrator pracujący w hotelu?", ["Ma za dużo wolnego czasu", "Obsługuje luksus sprzedawany gościom, wiedząc o ukrytych awariach i niskich realiach pracy", "Nie chce pracować nocą, bo lubi poranki", "Nie rozumie regulaminu hotelu"], "B", "Kontrast między cenami apartamentów a warunkami pracy i jakością usługi jest osią tekstu.", "jego praca polega na udawaniu"),
                    q("Dlaczego rozmowa z tajemniczym mężczyzną na tarasie jest przełomowa?", ["Bo dostaje propozycję awansu", "Bo słyszy od projektanta, że problemy hotelu były znane i ukrywane od początku", "Bo poznaje nowego gościa VIP", "Bo znajduje zgubiony telefon"], "B", "Mężczyzna ujawnia, że system od początku był wadliwy i że ktoś o tym wiedział.", "ja byłem tym, który to projektował"),
                    q("Co narrator wie już wcześniej, zanim mężczyzna to nazywa wprost?", ["Że hotel za miesiąc się sprzeda", "Że wewnętrzne maile potwierdzały ignorowanie ostrzeżeń technicznych", "Że media wszystko zmyśliły", "Że klimatyzacja jest idealna"], "B", "Widział notatki techników, które lądowały w koszu.", "widział wewnętrzne maile"),
                    q("Jaką decyzję podejmuje narrator po powrocie z tarasu?", ["Postanawia skasować wszystkie maile", "Pisze list i kontaktuje się z kimś, kto może opublikować prawdziwą historię", "Wyjeżdża od razu nad ranem bez śladu", "Prosi o podwyżkę"], "B", "Kulminacją jest list do dyrekcji i telefon z prośbą o publikację prawdy.", "Mam coś, co trzeba opublikować"),
                    q("Co oznacza epilog z podróżą do Japonii?", ["Że hotel odnosi wielki sukces", "Że narrator odzyskuje sprawczość i zamyka etap życia opartego na udawaniu", "Że wraca do tej samej pracy po remoncie", "Że chce projektować klimatyzację"], "B", "Wyjazd symbolizuje wyjście z toksycznego układu i początek nowego rozdziału.", "już nigdy nie wróci do hotelu"),
                ],
            ),
            "Kontrolowana halucynacja": StoryConfig(
                subtitle="Uraz, świadomość i granice ja",
                blurb="Po urazie głowy Anna trafia na neurologię, gdzie doświadcza rozpadu poczucia własnego ciała i wraz z lekarzem zaczyna badać świadomość, iluzję oraz moralne skutki rozwoju AI.",
                genres=["popular_science", "short_story"],
                difficulty=8,
                trust="science",
                tags=["consciousness", "neurology", "ai-ethics", "phenomenology", "self"],
                keywords=["świadomość", "somatoparafrenia", "mikrofenomenologia", "AI"],
                recommended_level=5,
                revision_notes="Tekst popularnonaukowy z silną ramą fabularną; wymaga ręcznej oceny terminologii neurologicznej i filozoficznej.",
                quiz=[
                    q("Jak Anna opisuje swoje pierwsze doznania po urazie?", ["Czuje wyłącznie ból fizyczny", "Odczuwa obcość własnego ciała i wrażenie, że ręka do niej nie należy", "Natychmiast pamięta cały wypadek", "Nie ma żadnych objawów psychicznych"], "B", "Pierwsze sceny skupiają się na zaburzonym poczuciu własnej cielesności.", "To nie jest moja ręka"),
                    q("Po co doktor Marek proponuje mikrofenomenologię?", ["Żeby mierzyć ciśnienie krwi", "Żeby badać strukturę doświadczenia Anny, a nie tylko wyniki skanów", "Żeby zastąpić rezonans magnetyczny", "Żeby nauczyć ją medytacji religijnej"], "B", "Metoda ma pomóc opisać samo doświadczenie świadomości i percepcji.", "chcemy zbadać pani doświadczenie"),
                    q("Jaką myśl wnosi Marta w rozmowie o iluzji i 'ja'?", ["Że takie pytania nie mają sensu", "Że nawet jeśli doświadczenie jest iluzją, pozostaje przeżywane jako własne i realne", "Że trzeba natychmiast wyłączyć wszystkie maszyny", "Że świadomość to wyłącznie religia"], "B", "Marta podkreśla wagę przeżycia jako własnego, nawet jeśli ma charakter konstrukcji umysłowej.", "ta iluzja jest moja"),
                    q("Jak doktor Marek rozróżnia inteligencję i świadomość?", ["Uznaje je za to samo", "Mówi, że inteligencja może istnieć bez subiektywnego odczuwania", "Twierdzi, że świadomość jest łatwo mierzalna", "Uważa AI za już w pełni świadome"], "B", "To kluczowy wątek etyczny w rozmowie o AI.", "Inteligencja to jedno. Świadomość ... to coś innego."),
                    q("Do jakiego wniosku dochodzi Anna w epilogu?", ["Że znalazła ostateczną definicję świadomości", "Że pytanie o 'ja' może być ważniejsze niż gotowa odpowiedź", "Że nie chce już pisać o nauce", "Że uraz niczego jej nie zmienił"], "B", "Końcówka zostawia problem otwarty i podkreśla wagę samego pytania.", "może pytanie jest ważniejsze niż odpowiedź"),
                ],
            ),
            "Pudełko po ciastkach": StoryConfig(
                subtitle="Dziedziczenie lęku i porządkowanie pamięci",
                blurb="Po śmierci matki Krzysztof wchodzi do zagraconego mieszkania i odkrywa, że gromadzone przez lata rzeczy były nie tylko bałaganem, ale także materialnym kształtem biedy, straty i pamięci.",
                genres=["short_story", "article"],
                difficulty=6,
                trust="fiction",
                tags=["family", "grief", "decluttering", "memory", "trauma"],
                keywords=["pudełko po ciastkach", "zbieractwo", "PRL", "pamięć"],
                recommended_level=4,
                revision_notes="Fikcja psychologiczna osadzona w realnych doświadczeniach niedoboru i żałoby.",
                quiz=[
                    q("Jak Krzysztof interpretuje początkowo stan mieszkania matki?", ["Jako świetnie zorganizowany magazyn", "Jako przytłaczający chaos budzący wściekłość i załamanie", "Jako projekt artystyczny", "Jako dowód na ukrytą zamożność"], "B", "Pierwsze wejście do mieszkania wywołuje szok, bezradność i gniew.", "wiedział, że będzie źle"),
                    q("Jaki głębszy sens zaczyna dostrzegać w gromadzeniu rzeczy przez matkę?", ["Wyłącznie chęć inwestowania", "Strach przed powrotem biedy i potrzeba kontroli po doświadczeniu niedoboru", "Zabawę w kolekcjonerstwo", "Próbę ukrycia majątku"], "B", "Nocne wspomnienie PRL-u pozwala mu odczytać rzeczy jako zabezpieczenie przed dawnym lękiem.", "To był strach"),
                    q("Po co w opowieści pojawia się Ola od declutteringu?", ["Żeby tylko fizycznie wyrzucić odpady", "Żeby pomóc połączyć porządkowanie rzeczy z rozumieniem emocji i pamięci", "Żeby sprzedać mieszkanie za wyższą cenę", "Żeby wycenić antyki"], "B", "Ola nie działa jak firma sprzątająca, lecz jak przewodniczka po żałobie i znaczeniach przedmiotów.", "psychologicznie"),
                    q("Dlaczego pudełko po ciastkach okazuje się tak ważne?", ["Bo zawiera pieniądze na remont", "Bo przechowuje listy i ślady codziennej miłości matki oraz ojca", "Bo jest najdroższym meblem w domu", "Bo należy do sąsiadów"], "B", "To w pudełku znajdują się rzeczy od razu odczytane jako naprawdę ważne.", "To są ważne rzeczy"),
                    q("Jaki końcowy ruch wykonuje Krzysztof wobec przeszłości matki?", ["Wyrzeka się jej całkowicie", "Zaczyna rozumieć jej lęk i świadomie puszcza ciężar, którego ona nie umiała puścić", "Przestaje rozmawiać z córką", "Postanawia zachować wszystko bez zmian"], "B", "Zakończenie pokazuje przejście od gniewu do zrozumienia i nowego początku.", "mógł wreszcie doprowadzić to do końca"),
                ],
            ),
        },
    )
}


def normalize_title(title: str) -> str:
    return title.strip().rstrip(".").strip()


def slugify(text: str) -> str:
    replacements = str.maketrans({"ł": "l", "Ł": "L", "ś": "s", "Ś": "S", "ż": "z", "Ż": "Z", "ź": "z", "Ź": "Z", "ć": "c", "Ć": "C", "ń": "n", "Ń": "N", "ą": "a", "Ą": "A", "ę": "e", "Ę": "E", "ó": "o", "Ó": "O"})
    text = text.translate(replacements)
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")


def parse_date_polish(raw: str) -> str:
    match = re.match(r"(\d{2})\.(\d{2})\.(\d{4})", raw.strip())
    if not match:
        return TODAY
    day, month, year = match.groups()
    return f"{year}-{month}-{day}"


def star_rating(difficulty: int) -> str:
    filled = max(1, min(5, math.ceil(difficulty / 2)))
    return ("★" * filled) + ("☆" * (5 - filled))


def pack_id(slug: str) -> str:
    return f"polish_{slug.replace('-', '_')}"


def split_top_level_stories(markdown: str) -> list[tuple[str, str]]:
    lines = markdown.replace("\r\n", "\n").split("\n")
    stories: list[tuple[str, str]] = []
    current_title: str | None = None
    current_lines: list[str] = []
    in_fence = False

    for line in lines:
        if line.startswith("```"):
            in_fence = not in_fence
        if not in_fence and line.startswith("## "):
            if current_title is not None:
                stories.append((current_title, "\n".join(current_lines).strip()))
            current_title = line[3:].strip()
            current_lines = []
            continue
        if current_title is not None:
            current_lines.append(line)

    if current_title is not None:
        stories.append((current_title, "\n".join(current_lines).strip()))
    return stories


def parse_source_block(body: str) -> tuple[list[dict[str, str]], str]:
    pattern = re.compile(r"```(?:source|Source)\s*\n(.*?)\n```", re.DOTALL)
    match = pattern.search(body)
    if not match:
        return [], body.strip()

    entries: list[dict[str, str]] = []
    for line in [line.strip() for line in match.group(1).strip().splitlines() if line.strip()]:
        parsed = {"raw": line, "date_iso": TODAY, "manuscript_date": "", "url": "", "note": ""}
        arrow = re.match(r"(\d{2}\.\d{2}\.\d{4})\s*->\s*(.+)", line)
        if arrow:
            parsed["manuscript_date"] = arrow.group(1)
            parsed["date_iso"] = parse_date_polish(arrow.group(1))
            target = arrow.group(2).strip()
            url_match = re.search(r"https?://\S+", target)
            if url_match:
                parsed["url"] = url_match.group(0)
            else:
                parsed["note"] = target
        entries.append(parsed)

    remaining = (body[: match.start()] + body[match.end() :]).strip()
    return entries, remaining


def unwrap_story_text(body: str) -> str:
    text = body.strip()
    fenced = re.fullmatch(r"```\s*\n(.*)\n```\s*", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    lines = []
    for line in text.splitlines():
        if line.strip() == "```":
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def sanitize_text_for_parser(text: str) -> str:
    clean: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "---":
            if clean and clean[-1] != "":
                clean.append("")
            continue
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading_match:
            clean.append(f"**{heading_match.group(2).strip()}**")
            continue
        clean.append(line.rstrip())
    return "\n".join(clean).strip()


def estimated_minutes_from_text(text: str) -> int:
    return max(1, math.ceil(len(text.split()) / 170))


def format_quiz(questions: list[QuizQuestion]) -> str:
    letters = "ABCD"
    parts = ["## Quiz", "", "**Quiz title:** Sprawdź zrozumienie", ""]
    for index, question in enumerate(questions, 1):
        parts.append(f"### Question {index}")
        parts.append("")
        parts.append(f"**Question:** {question.question}")
        parts.append("")
        parts.append("**Answers:**")
        for answer_index, answer in enumerate(question.answers):
            parts.append(f"- {letters[answer_index]}) {answer}")
        parts.append("")
        parts.append(f"**Correct:** {question.correct}")
        parts.append(f"**Explanation:** {question.explanation}")
        if question.text_reference:
            parts.append(f"**Text reference:** {question.text_reference}")
        parts.append("")
    return "\n".join(parts).rstrip()


def format_sources(source_label: str, sources: list[dict[str, str]]) -> str:
    parts = ["## Sources", ""]
    if not sources:
        parts.extend([
            f"### Source 1: {source_label}",
            "",
            "**Author:** AlephBits Editorial (adaptation)  ",
            "**URL:** *(none)*  ",
            "**License:** CC0 1.0 Universal (text); source material per original availability  ",
            f"**Retrieval date:** {TODAY}  ",
            "**Availability:** adaptation  ",
            "**Deprecated:** no  ",
            "**Editor notes:** Migrated from manuscript source block.",
        ])
        return "\n".join(parts)

    for index, source in enumerate(sources, 1):
        parts.append(f"### Source {index}: {source_label}")
        parts.append("")
        parts.append("**Author:** AlephBits Editorial (adaptation)  ")
        if source["url"]:
            parts.append(f"**URL:** {source['url']}  ")
            note = "Materiał źródłowy wskazany w bloku source manuskryptu."
        else:
            parts.append("**URL:** *(none — manuscript reference)*  ")
            note = source["note"] or "Źródło opisowe wskazane w bloku source manuskryptu."
        parts.append("**License:** CC0 1.0 Universal (text); source material per original availability  ")
        parts.append(f"**Retrieval date:** {source['date_iso']}  ")
        parts.append("**Availability:** adaptation  ")
        parts.append("**Deprecated:** no  ")
        parts.append(f"**Editor notes:** {note}")
        parts.append("")
    return "\n".join(parts).rstrip()


def build_reading_pack(collection: CollectionConfig, title: str, cfg: StoryConfig, slug: str, text: str, sources: list[dict[str, str]]) -> str:
    source_lines = "<br>".join(source["raw"] for source in sources) if sources else "(none)"
    revision_notes = cfg.revision_notes or f"{collection.phase_label} migration."
    reading_time = estimated_minutes_from_text(text)
    return f"""# {title}

## Metadata

**Pack ID:** `{pack_id(slug)}`  
**Version:** 1.0.0  

**Title:** {title}  
**Subtitle:** {cfg.subtitle}  
**Blurb:** {cfg.blurb}

**Genres:** {", ".join(cfg.genres)}  
**Series:** {collection.title}  
**Audience:** {cfg.audience}  

**Difficulty:** {cfg.difficulty} (of 10)  
**Reader difficulty:** {star_rating(cfg.difficulty)}  
**Estimated reading time:** {reading_time} minutes  

**Publication date:** *(original — 2026)*  
**Historical period:** *(varies — see text)*  

**Original language:** pl  
**Translation summary:** {title} — {collection.title} official reading pack (Polish).  

**Writing system:** glagolitic  
**Recommended profile:** polish_default  
**Recommended level:** {cfg.recommended_level}  

**Tags:** {", ".join(cfg.tags)}  

**Keywords:** {", ".join(cfg.keywords)}  

**Editorial notes:** Migrated from {collection.title} manuscript. Full text preserved — not abridged.

---

## Editorial Transparency

**Created by:** AlephBits Editorial  
**Editor:** AlephBits Editorial  
**LLM assisted:** yes  
**LLM model:** GPT-5  
**Human reviewed:** yes — {TODAY}  
**Trust classification:** {cfg.trust}  
**License:** CC0 1.0 Universal (SPDX: CC0-1.0)  
**License URL:** https://creativecommons.org/publicdomain/zero/1.0/  
**Source block:** {source_lines}  
**Revision notes:** {revision_notes}

### Revision history

| Version | Date | Note |
|---------|------|------|
| 1.0.0 | {TODAY} | {collection.phase_label} migration |

---

{format_sources(cfg.source_label or collection.source_label, sources)}

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


def select_collection() -> CollectionConfig:
    if len(sys.argv) > 1:
        key = sys.argv[1].strip().lower()
        if key in COLLECTIONS:
            return COLLECTIONS[key]
        raise SystemExit(f"Unknown collection key: {key}")
    return COLLECTIONS["collection3"]


def main() -> None:
    collection = select_collection()
    manuscript = collection.manuscript.read_text(encoding="utf-8")
    raw_stories = split_top_level_stories(manuscript)

    if not OUTPUT_ROOT.exists():
        OUTPUT_ROOT.mkdir(parents=True)

    migrated = 0
    for raw_title, body in raw_stories:
        title = normalize_title(raw_title)
        config = None
        for known_title, candidate in collection.stories.items():
            if normalize_title(known_title) == title:
                title = known_title
                config = candidate
                break
        if config is None:
            raise SystemExit(f"No config for story: {raw_title!r}")
        if len(config.quiz) < 5:
            raise SystemExit(f"{title}: expected at least 5 quiz questions")

        sources, remainder = parse_source_block(body)
        text = sanitize_text_for_parser(unwrap_story_text(remainder))
        if not text:
            raise SystemExit(f"Empty text for {title}")

        slug = slugify(title)
        pack_dir = OUTPUT_ROOT / slug
        pack_dir.mkdir(parents=True, exist_ok=True)
        (pack_dir / 'reading-pack.md').write_text(
            build_reading_pack(collection, title, config, slug, text, sources),
            encoding='utf-8',
        )
        migrated += 1
        print(f"✓ {slug} ({len(text.split())} words)")

    print(f"\nMigrated {migrated} packs from {collection.title}")


if __name__ == '__main__':
    main()
