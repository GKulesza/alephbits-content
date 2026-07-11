#!/usr/bin/env python3
"""Phase 79 — replace weak pack blurbs with editorial back-cover copy."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKS = ROOT / "official" / "glagolitic" / "pl"

# Editorial blurbs: 40–90 words, Polish, no spoilers, no AI intros.
BLURBS: dict[str, str] = {
    "boliewicz": (
        "Antoni Dudek wraca do sporów wokół Lecha Wałęsy — od pseudonimu „Bolek” "
        "po lata prezydentury i późniejsze rozczarowania. Narracja nie daje gotowych "
        "werdyktów, lecz prowadzi przez sprzeczne warstwy biografii, polityki i pamięci "
        "narodowej. Czytelnik dostaje materiał do własnej oceny człowieka, który "
        "wciąż dzieli Polaków."
    ),
    "brudne-pieniadze-czysta-nauka": (
        "Anna Kowalska odkłada artykuł o sztucznych słodzikach, choć termin góruje "
        "nad biurkiem. Gdy profesor Nowak proponuje sponsorowanie badań, pokusa "
        "finansowego oddechu staje się realna. Naukowa uczciwość i presja kariery "
        "ścierają się w opowieści o tym, ile kosztuje trzymanie się zasad, gdy "
        "ktoś oferuje pomoc."
    ),
    "cel-na-ten-rok-to-nic": (
        "Ania ma tytuł dyrektorki, harmonogram pełny spotkań i wrażenie, że wszystko "
        "jest pod kontrolą. Po rozmowie z mentorką Karoliną zaczyna jednak pytać, "
        "czy jej cele naprawdę są jej własne. Spokojna opowieść o zmęczeniu "
        "ambicją i odwadze, by na chwilę nie wiedzieć, dokąd biegniesz."
    ),
    "cena-widoku": (
        "Nocna zmiana w nadmorskim hotelu. Za szklanymi ścianami goście płacą za "
        "widok, a narrator widzi też awarie ukryte przed recepcją. Gdy na tarasie "
        "pojawia się nieznajomy z trudnym pytaniem, codzienna rutyna zaczyna pękać. "
        "Opowieść o pracy, która udaje luksus, i o cenie patrzenia na cudzy "
        "komfort z drugiej strony lady."
    ),
    "cien-skrzydel-nad-oceanem": (
        "James ma trzy lata, gdy zaczyna mówić o samolocie, płomieniach i zablokowanej "
        "kabince nad oceanem. Szczegóły pasują do śmierci pilota z 1945 roku, choć "
        "nikt w rodzinie nie opowiada mu historii wojny. Rodzice szukają wyjaśnienia "
        "między racjonalnością a tym, czego dziecko nie powinno wiedzieć."
    ),
    "cisza-przed-burza": (
        "Warszawa, październik 1932. Marian Rejewski patrzy na niemiecką Enigmę jak "
        "na układankę logiczną, nie jak na magiczny szyfr. W Biurze Szyfrów rodzi się "
        "pomysł, który może zmienić bieg wojny — jeśli zdążą, zanim świat obudzi się "
        "z koszmaru. Napięcie rośnie w ciszy laboratorium, gdzie liczy się każdy "
        "błąd."
    ),
    "czarna-skrzynka": (
        "Robert budzi się o 5:47, jeździ tą samą trasą i traktuje dzień jak "
        "rozkład jazdy. Gdy życie zaczyna wymykać się spod kontroli, szuka nowej "
        "reguły, która wszystko poukłada. Opowieść o człowieku, który myli porządek "
        "ze spokojem — i o małej zmianie, która może być początkiem czegoś "
        "innego."
    ),
    "czarny-kodeks": (
        "Janusz, historyk z pasją, podąża śladem Czarnego Kodeksu — dokumentu "
        "splątanego z rewolucją haitańską, Vodou i europejską wyobraźnią. Im "
        "głębiej wchodzi w archiwa i legendy, tym trudniej odróżnić fakt od "
        "mitu. Podróż przez pamięć kolonialną, w której świętość i przemoc "
        "przeplatają się bez ostrzeżenia."
    ),
    "czarny-mnich-z-nikiszowca": (
        "Tomek dorastał w Nikiszowcu jak obcy we własnej dzielnicy. Legenda "
        "Czarnego Mnicha wraca, gdy kopalnia milknie, a kamienice opowiadają "
        "własną historię. Między wspomnieniami dzieciństwa a dorosłym spojrzeniem "
        "pojawia się pytanie: czy demon miejsca może stać się częścią tożsamości "
        "człowieka, który chce wreszcie tu zostać."
    ),
    "czarny-rynek-tokenow": (
        "Adam, inżynier systemów chmurowych, znajduje w logach ślad, którego nie "
        "powinno być. Za fasadą legalnych API kryje się rynek kluczy i tokenów "
        "sztucznej inteligencji. Im bardziej zagłębia się w proceder, tym wyraźniej "
        "widzi, że cena „taniego dostępu” dotyczy też jego własnej pracy i "
        "odpowiedzialności."
    ),
    "dlaczego-fale-radiowe-przenikaja-przez-sciany-a-swiatlo-nie": (
        "Dlaczego radio działa za ścianą, a światło już nie? Opowieść prowadzi "
        "od fal elektromagnetycznych przez budowę materii aż do pytań, które "
        "wciąż zadają fizycy. Bez suchych wykładów — z ciekawością człowieka, "
        "który chce zrozumieć świat tuż poza codziennym doświadczeniem "
        "widzenia i słyszenia."
    ),
    "dlaczego-niebo-jest-niebieskie": (
        "Niebo wydaje się oczywiste — dopóki nie zaczniesz pytać, skąd bierze się "
        "ten kolor. Od rozpraszania światła przez Homera bez słowa na błękit, "
        "po współczesną fizykę i granice naszego widzenia. Spokojna, głęboka "
        "opowieść o tym, że nawet najprostsze pytanie może otworzyć kilka "
        "warstw prawdy naraz."
    ),
    "domek": (
        "Marta wraca do mieszkania pełnego nierozpakowanych pudeł i codziennych "
        "wymówek. Sprzątanie zawsze czeka na jutro — aż pewnego wieczoru coś "
        "w niej pęka. Opowieść o chaosie, który nie dotyczy tylko rzeczy, i o "
        "odwadze, by zatrzymać się na chwilę we własnym domu, zanim ucieknie "
        "znowu."
    ),
    "domysl-sie": (
        "Magda i Grzesiek wyglądają jak para, która ma wszystko poukładane. "
        "Między pracą, codziennymi drobiazgami i milczeniem narasta jednak "
        "niewypowiedziane napięcie. Gdy oboje trafiają na spotkanie, którego "
        "nie planowali, zaczynają zauważać wzorce, których wcześniej nie chcieli "
        "nazwać — i pytanie, czy w ogóle znają swoje własne potrzeby."
    ),
    "dostrojony-dom": (
        "Po warsztatach medytacji Ewa wraca do mieszkania pełnego przedmiotów, "
        "które kiedyś miały znaczenie. Z pomocą specjalistki od przestrzeni "
        "zaczyna pytać nie tylko o rzeczy, lecz o to, jak chce żyć. Opowieść "
        "o domu jako lustro wnętrza — i o powolnym odzyskiwaniu miejsca "
        "dla siebie."
    ),
    "dylemat-szatniarza": (
        "Polityk wraca z Brukseli do Warszawy tuż przed kolejną aferą medialną. "
        "W szatni klubu, między rozmowami o wynikach sondażów a codziennym "
        "lękiem o wizerunek, musi zdecydować, komu zaufać. Opowieść o presji "
        "publicznej roli i o cenie kompromisu, gdy cały kraj patrzy na twój "
        "następny krok."
    ),
    "dziewczyna-ktora-zniknela-o-swicie": (
        "Ośmiemnastoletnia Agnieszka wychodzi z klubu o świcie i znika bez "
        "śladu. Policjantka Joanna wraca do sprawy lat później, przeglądając "
        "nagrania, raporty i błędy pierwszych godzin. Śledztwo nie daje szybkich "
        "odpowiedzi — za to pokazuje, jak łatwo stracić czas, gdy wszyscy "
        "wierzą, że „sama wróci”."
    ),
    "dziewczyna-z-jelania": (
        "Anastazja przyjeżdża z Niemiec do Warszawy, by uczyć się polskiego "
        "bez planu kariery i bez rodziny w tym kraju. Pokój na Pradze, „Lalka” "
        "w oryginale i codzienne pomyłki językowe stają się mostem do miejsca, "
        "którego nie pamięta, a które nagle brzmi jak dom."
    ),
    "glosy-z-ziemi": (
        "Emerytowany lekarz Tadeusz Jędrzejowski zbiera historie pacjentów "
        "poszkodowanych przez system, który miał ich leczyć. Im więcej "
        "dokumentów i świadectw gromadzi, tym wyraźniej widać mechanizm "
        "korupcji i obojętności. Opowieść o człowieku, który nie chce już "
        "milczeć, gdy instytucja udaje, że wszystko działa."
    ),
    "gruby-dzienniczek": (
        "Patryk ma trzydzieści lat, wypalony grafik i poczucie, że życie "
        "przesuwa się obok. Sięga po gruby zeszyt i zaczyna od jednej prostej "
        "reguły dziennika. Czy kilka linijek dziennie mogą coś zmienić? "
        "Opowieść o małym nawyku, który staje się lustrem tego, czego "
        "unikamy."
    ),
    "jak-bor-z-jasnego-nieba": (
        "W studiu podcastu rozmowa z Marcinem „Żukiem” Kowalczykiem — byłym "
        "operatorem BOR — schodzi od adrenaliny służby do granic, o których "
        "publicznie nie wolno mówić. Wywiad ma być o zawodzie, a staje się "
        "pytaniem o to, co zostaje w człowieku po latach pracy na granicy "
        "życia i śmierci."
    ),
    "jak-ugotowac-herbate": (
        "Patryk myślał, że herbata to liście i wrzątek. Turecki czajnik, japońska "
        "matcha i polski kubek z cytryną pokazują mu coś innego: każda kultura "
        "parzy nie tylko napój, lecz sposób bycia razem. Ciepła opowieść "
        "o cierpliwości, gościnności i odkrywaniu, że prosta filiżanka "
        "może otworzyć świat."
    ),
    "kamera-na-ulicy": (
        "Noworoczna noc. Tom wraca do domu i znajduje żonę nieruchomą w salonie. "
        "W jednej chwili musi zdecydować, co zrobić — a ciało nie reaguje tak, "
        "jak powinno. Kamery na ulicy nagrywają ruch miasta, lecz w tym "
        "mieszkaniu wszystko staje w miejscu. Intymna opowieść o szoku, "
        "milczeniu i chwili, gdy człowiek nie wie, jak zachować się "
        "ludzko."
    ),
    "kamien-pamieci": (
        "Marta jedzie do Berlina z listą współrzędnych i nadzieją, że odnajdzie "
        "tablicę upamiętniającą polskich żołnierzy, o której słyszała od dziadka. "
        "W obcym mieście granice pamięci rodzinnej i historii narodowej "
        "zaczynają się zcinać. Podróż o tym, co znaczy pamiętać, gdy ślady "
        "są ledwo widoczne."
    ),
    "koniec-epoki-pudelek": (
        "Adam obserwuje, jak świat gier i muzyki reaguje na koniec nowych "
        "wydań płytowych. Między nostalgią a praktycznością cyfrowej "
        "biblioteki rodzi się pytanie: co tracimy, gdy fizyczny nośnik "
        "zniknie? Opowieść o kolekcjonerach, graczach i pokoleniu, które "
        "dorastało na pudełkach z kodem."
    ),
    "kontrolowana-halucynacja": (
        "Po urazie głowy Anna trafia na oddział neurologii. Świat zaczyna "
        "działać inaczej: ciało, pamięć i obecność własnej osoby nie "
        "składają się w całość. Lekarze mówią o badaniach, ona słyszy "
        "własne pytania głośniej. Intymna opowieść o granicy między "
        "doświadczeniem a tym, co można zmierzyć."
    ),
    "kubek": (
        "Ewa, psycholożka i matka nastolatki, obserwuje innych rodziców "
        "i coraz częściej wątpi, czy sama potrafi być po prostu obecna. "
        "Między poradnikiem a codziennością szuka odpowiedzi prostszej "
        "niż teoria. Opowieść o bliskości, która nie mieści się w "
        "schemacie i zaczyna się od małych gestów."
    ),
    "legenda-o-smoku-wawelskim": (
        "Smok straszy Kraków, a król obiecuje nagrodę temu, kto ocali miasto. "
        "Na peryferiach legendy staje Skuba — szewc bez miecza, za to z "
        "głową pełną pomysłów. Opowieść o odwadze, która nie zawsze wygląda "
        "jak w baśni, i o mieście, które wciąż chętnie wraca do swojej "
        "najstarszej opowieści."
    ),
    "mamy-trupa-i-co-dalej": (
        "Po śmierci matki Tomasz staje przed biurokracją pogrzebową, fakturami "
        "i pytaniami, na które nikt go nie przygotował. Każdy etap wygląda "
        "jak obowiązek, a jednocześnie jak coś obcego. Opowieść o żałobie "
        "bez instrukcji obsługi — i o tym, jak dorosłość czasem zaczyna się "
        "od papieru, którego nie chcesz podpisywać."
    ),
    "maria-sklodowska-curie": (
        "Warszawa XIX wieku. Mała Maria Skłodowska dorasta w rodzinie, która "
        "wierzy w naukę mimo przeciwności. Droga na Sorbonę, laboratorium "
        "pełne promieniowania i Nobla w dwóch dziedzinach dopiero nadejdą — "
        "najpierw jest bieda, konspiracyjna nauka i decyzja, że świat "
        "można zmieniać własnymi rękami."
    ),
    "metoda-feynmana": (
        "Pod filmem o fizyce ktoś pyta, czy nauka wyjaśnia wszystko. Profesor "
        "Marek zaczyna odpowiadać od wzorów, a kończy przy pytaniach, których "
        "nie da się zamknąć w równaniu. Opowieść o ciekawości, która nie "
        "boi się granic wiedzy, i o tym, jak uczyć innych, nie udając "
        "pewności co do wszystkiego."
    ),
    "misja-ktora-pekla": (
        "Marek prowadzi dojrzałą firmę konsultingową i wierzy w swoją misję "
        "pomagania przedsiębiorcom. Gdy spotyka klientów z innej skali i "
        "innego rynku, schematy zaczynają pękać. Opowieść o doradztwie, "
        "ambicji i odkrywaniu, że dobra rada bez kontekstu może być "
        "gorsza niż milczenie."
    ),
    "na-dworcu": (
        "Marek jedzie pociągiem przez Polskę i po raz pierwszy od lat naprawdę "
        "patrzy na dworce. Gdańsk, wspomnienia ojca, spory o najpiękniejszą "
        "stację — wszystko składa się w podróż, która nie chodzi o peron, "
        "lecz o miejsca, gdzie zaczyna się i kończy czyjeś oczekiwanie."
    ),
    "na-targu": (
        "Adam traci pracę w Elblągu i jedzie na targ w Nowy Targ, nie wiedząc "
        "jeszcze, że wróci tam jako handlarz. Tłumy, akcenty sąsiadów, kaszmir "
        "za kilkaset złotych i hałas, który brzmi jak początek czegoś "
        "nowego. Opowieść o handlu jako spotkaniu ludzi, nie tylko towaru."
    ),
    "oczy-ktore-nie-widza": (
        "Pani Anna uczy czytać w zerówce od dwudziestu lat i widzi zmianę, "
        "której rodzice nie zawsze chcą słuchać. Dzieci patrzą na ekrany "
        "inaczej niż na stronę książki — a aplikacja, która „uczy”, nie "
        "zawsze uczy tego, co trzeba. Spokojna opowieść o obecności dorosłego "
        "przy pierwszych sylabach."
    ),
    "pierwszy-lot-na-marsa": (
        "Mały Marek ogląda pierwsze zdjęcia Marsa z Vikinga, a dorosły wraca "
        "do laboratorium, gdzie wciąż analizuje skały z Czerwonej Planety. "
        "Między dziecięcymi marzeniami a doniesieniami o Cheyava Falls "
        "pojawia się pytanie, które nie chce odejść: czy jesteśmy sami "
        "we wszechświecie?"
    ),
    "prolog-wiatru": (
        "Yumiko ma nagrać teledysk o świcie na plaży w Chiba, tuż przy "
        "granicy miasta i oceanu. Zimny wiatr, sen na jawie i piosenka, "
        "która brzmi jak obietnica nowego początku. Opowieść o chwili, "
        "gdy kariera artystki zatrzymuje się między kolejnym ujęciem a "
        "pytaniem, dokąd właściwie zmierza."
    ),
    "przerwa": (
        "Po czternastogodzinnym dniu pracy Patryk wraca do domu wyczerpany "
        "i przypadkiem otwiera stary notes. Kilka zapisanych lat temu "
        "pytań wygląda dziś jak rozmowa z kimś, kogo dawno nie słuchał. "
        "Opowieść o wypaleniu, które nie przychodzi nagle, i o przerwie, "
        "której boimy się nazwać."
    ),
    "pudelko-po-ciastkach": (
        "Po śmierci matki Krzysztof wchodzi do mieszkania, w którym każdy "
        "kąt coś skrywa. Pudełka, gazety i przedmioty „na później” tworzą "
        "labirynt, którego sensu nie zna nikt spoza rodziny. Opowieść o "
        "lęku przed rozstanie i o powolnym rozumieniu, skąd bierze się "
        "potrzeba trzymania."
    ),
    "rozmowa-z-lekarzem": (
        "Kasia ma trzydzieści dwa lata, dwójkę dzieci i nogi, które wieczorem "
        "puchną coraz bardziej. Myślała, że to tylko „pajączki”, dopóki "
        "nie zobaczyła pierwszego żylaka. W gabinecie chirurga zaczyna "
        "rozmowę, która zmienia sposób, w jaki patrzy na własne ciało "
        "i lekceważenie objawów."
    ),
    "siedem-gor-i-jeden-ocean": (
        "Marek jedzie do Korei Południowej przy kontrakcie muzealnym i "
        "wpada w wir skojarzeń: Chopin, Wiedźmin, Lewandowski, czołgi. "
        "Im dłużej zostaje, tym wyraźniej widzi, jak bardzo obraz kraju "
        "zależy od tego, kto go ogląda. Opowieść o podróży, która "
        "najpierw dotyczy architektury, a potem tożsamości."
    ),
    "spacer-po-krakowie": (
        "Spacer po znanym mieście może brzmieć prosto — dopóki czytasz go "
        "nowym pismem. Rynek, Planty, Wisła i Wawel układają się w opowieść "
        "o miejscu, które pamiętasz, i języku, którego uczysz się na "
        "nowo. Lekcja czytania dla tych, którzy lubią, gdy tekst "
        "prowadzi krok za krokiem."
    ),
    "susza": (
        "Tomek dorasta w Borach Tucholskich u boku ojca-leśniczego. Kilka lat "
        "bez deszczu wysusza nie tylko glebę — zmienia też rozmowy przy "
        "stole i sposób patrzenia na przyszłość. Opowieść o krajobrazie, "
        "który wydaje się stały, dopóki klimat przypomina, że nic nie jest "
        "dane na zawsze."
    ),
    "trzynascie-zasad": (
        "Amerykanka przyjeżdża do Polski z uśmiechem, który tu nikt nie "
        "odwzajemnia. Przyjaciel tłumaczy jej kolejne zasady: kiedy się "
        "uśmiechać, jak stać w kolejce, co znaczy „jak leci” i dlaczego "
        "geografia ma znaczenie. Ciepła, czasem zabawna opowieść o "
        "obcowaniu z obcą kulturą bez podręcznika."
    ),
    "w-kawiarni": (
        "Marek wchodzi do kawiarni z ostatnimi pieniędzmi w portfelu i "
        "potrzebą ukrycia się choć na godzinę. Baristka widzi więcej niż "
        "zamówienie — krótką rozmowę, wizytówkę, drugą szansę bez wielkich "
        "słów. Opowieść o miejscu, gdzie ciepły kubek może być "
        "początkiem czegoś nowego."
    ),
    "wiatr-nad-rzeka": (
        "Anna zatrzymuje się na bulwarze nad Wisłą, gdy miasto pędzi dalej "
        "bez niej. Starszy mężczyzna mówi o wietrze, który pamięta to, co "
        "niosła woda — i nagle zwykły spacer staje się chwilą zatrzymania. "
        "Krótka, spokojna scena o powrocie do miejsc, które czekają "
        "cierpliwie."
    ),
    "worek-z-piaskiem": (
        "Na granicy w Cieszynie młody celnik obserwuje Jana, który codziennie "
        "przewozi ten sam, zawsze ciężki worek. Wygląda to jak zwykła "
        "manipulacja, dopóki rutyna nie zaczyna mówić własnym językiem. "
        "Opowieść o człowieku, który przez lata robił coś ważnego w cieniu "
        "codziennej pracy na przejściu."
    ),
    "wyraz-ktorego-nie-ma": (
        "Kasia nie rezygnuje z nauki czytania u córki Ali, choć każda lekcja "
        "kończy się łzami. Szuka słów, które dotrą do dziecka, a nie tylko "
        "spełnią program. Opowieść o rodzicielskiej upartości, wstydzie "
        "i małych przełomach, które nie przychodzą w jeden dzień."
    ),
    "zakazana-energia": (
        "Helena przeszukuje archiwa dworców kolejowych i znajduje projekty "
        "sprzed ery elektryczności, których nie powinno być w dokumentach. "
        "Im głębiej kopie, tym bardziej historia techniki przypomina "
        "thriller. Opowieść o architektce, która nie potrafi przejść obok "
        "pytania: kto ukrył te schematy i dlaczego?"
    ),
    "zasady": (
        "Łukasz czyta mailing Pawła Kadysza i rozpoznaje własny schemat: "
        "planowanie zamiast działania, wybór zamiast kroku. Pięć prostych "
        "reguł brzmi łatwo — dopóki nie trzeba je stosować tego samego "
        "ranka. Opowieść o prokrastynacji bez moralizowania i o tym, "
        "jak trudno zacząć od małej rzeczy."
    ),
}

BAD_INTROS = re.compile(
    r"(?i)^(?:this story is about|this book tells|in this text|"
    r"opowieść o|historia .+ który|w tym tekście|książka opowiada|"
    r"ten tekst opowiada|ta opowieść)"
)


def word_count(text: str) -> int:
    return len(re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE).split())


def rate_blurb(text: str) -> str:
    words = word_count(text)
    low = text.lower()
    if words < 20 or words > 120 or BAD_INTROS.match(text.strip()):
        return "Needs improvement"
    if 40 <= words <= 90 and not low.startswith("###"):
        return "Excellent"
    if 30 <= words <= 100:
        return "Good"
    return "Needs improvement"


def apply_blurb(path: Path, blurb: str) -> bool:
    text = path.read_text(encoding="utf-8")
    pattern = r"(\*\*Blurb:\*\*\s*)(.+?)(\n\n\*\*Genres:\*\*)"
    match = re.search(pattern, text, re.S)
    if not match:
        return False
    new_text = text[: match.start(2)] + blurb + text[match.end(2) :]
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> None:
    updated = 0
    for slug, blurb in BLURBS.items():
        path = PACKS / slug / "reading-pack.md"
        if not path.exists():
            print(f"SKIP missing {slug}")
            continue
        if apply_blurb(path, blurb):
            updated += 1
            print(f"OK {slug} ({word_count(blurb)}w, {rate_blurb(blurb)})")
    print(f"\nUpdated {updated} blurbs")


if __name__ == "__main__":
    main()
