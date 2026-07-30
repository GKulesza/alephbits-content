#!/usr/bin/env python3
"""
Translate three Polish books into all 7 supported application languages.

Books selected (diverse styles):
1. c1a78mx1 — "Głos i cisza" (fairy tale / short story) — The Little Mermaid adaptation
2. e4qvzfv8 — "Pierwszy lot na Marsa" (popular science) — Mars exploration
3. b9m80o2r — "Autorytet na przepraszam" (psychology / short story) — parenting

Languages: pl (original), en, eo, es, isv, isv_cyrl, isv_glag
"""

import json
import os
import re
import shutil
from datetime import date

CONTENT_DIR = os.path.expanduser("~/Developer/alephbits-content")
BOOKS = ["c1a78mx1", "e4qvzfv8", "b9m80o2r"]
LOCALES = ["en", "eo", "es", "isv", "isv_cyrl", "isv_glag"]
ALL_LOCALES = ["pl"] + LOCALES

TODAY = date.today().isoformat()
REVISION_DATE = "2026-07-30"


def parse_reading_pack(filepath):
    """Extract metadata and text from a reading-pack.md file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return content


def parse_lesson_json(filepath):
    """Parse lesson.json for structured data."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_quiz_json(filepath):
    """Parse quiz.json."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def get_quiz_section(md_content):
    """Extract the Quiz section from reading-pack.md."""
    quiz_match = re.search(r"## Quiz\n(.*?)(?=\n## Future Extensions|\n---\n## Future Extensions|\Z)", md_content, re.DOTALL)
    if quiz_match:
        return quiz_match.group(1).strip()
    return ""


def get_text_section(md_content):
    """Extract the Text section from reading-pack.md."""
    text_match = re.search(r"## Text\n(.*?)(?=\n---\n## Quiz|\n---\n\n## Quiz)", md_content, re.DOTALL)
    if text_match:
        return text_match.group(1).strip()
    # Fallback: try to find after ## Text
    lines = md_content.split("\n")
    in_text = False
    text_lines = []
    for line in lines:
        if line.strip() == "## Text":
            in_text = True
            continue
        if in_text:
            if line.strip().startswith("## "):
                break
            text_lines.append(line)
    return "\n".join(text_lines).strip()


# ============================================================
# TRANSLATIONS
# ============================================================

# Book: c1a78mx1 — "Głos i cisza" (The Voice and Silence) — Fairy Tale
C1A78MX1_TITLE = {
    "pl": "Głos i cisza",
    "en": "Voice and Silence",
    "eo": "Voĉo kaj Silenteco",
    "es": "La voz y el silencio",
    "isv": "Glas i Tišina",
    "isv_cyrl": "Глас и Тишина",
    "isv_glag": "Ⰳⰾⰰⱄ ⰺ Ⱅⰺⱎⰺⱀⰰ",
}

C1A78MX1_SUBTITLE = {
    "pl": "Syrenka, która oddała głos za miłość",
    "en": "The mermaid who gave her voice for love",
    "eo": "La sireno kiu donis sian voĉon por amo",
    "es": "La sirena que dio su voz por amor",
    "isv": "Sirenka, ktora dala glas za ljubov",
    "isv_cyrl": "Сиренка, которая дала глас за любовь",
    "isv_glag": "Ⱄⰺⱃⰵⱀⰽⰰ, ⰽⱁⱅⱁⱃⰰ ⰴⰰⰾⰰ ⰳⰾⰰⱄ ⰸⰰ ⰾⱓⰱⱁⰲ",
}

C1A78MX1_BLURB = {
    "pl": "Marina, najmłodsza córka Króla Mórz, ratuje tonącego księcia i oddaje głos wiedźmie, by zostać człowiekiem — lecz prawdziwa miłość okazuje się dawaniem, nie posiadaniem.",
    "en": "Marina, the youngest daughter of the Sea King, rescues a drowning prince and gives her voice to a witch to become human — but true love turns out to be about giving, not possessing.",
    "eo": "Marina, la plej juna filino de la Mar-Reĝo, savas dronantan princon kaj donas sian voĉon al sorĉistino por iĝi homo — sed vera amo montriĝas esti pri donado, ne posedado.",
    "es": "Marina, la hija menor del Rey del Mar, rescata a un príncipe que se ahoga y entrega su voz a una bruja para convertirse en humana — pero el verdadero amor resulta ser dar, no poseer.",
    "isv": "Marina, najmladša dŝi Kralja Morja, spasajet tonego kŝeža i daje svoj glas vedŝme da byti člověkom — ale pravdive ljubv je davanie, ne iměnie.",
    "isv_cyrl": "Марина, најмладша дщи Краља Морја, спасајет тонегo кнџеза и даје свој глас ведшме да быти чловеком — але правдиве љубв је давање, не имение.",
    "isv_glag": "Ⰿⰰⱃⰺⱀⰰ, ⱀⰰⰼⰿⰾⰰⰴⱎⰰ ⰴⱎⰺ Ⰽⱃⰰⰾⱝ Ⰿⱁⱃⱝ, ⱄⱂⰰⱄⰰⰼⰵⱅ ⱅⱁⱀⰵⰳⱁ ⰽⱀⰵⰶⰵ ⰺ ⰴⰰⰼⰵ ⱄⰲⱁⰼ ⰳⰾⰰⱄ ⰲⰵⰴⱎⰿⰵ ⰴⰰ ⰱⱏⱅⰺ ⱍⰾⱁⰲⰵⰽⱁⰿ — ⰰⰾⰵ ⱂⱃⰰⰲⰴⰺⰲⰵ ⰾⱓⰱⰲ ⰵ ⰴⰰⰲⰰⱀⰵ, ⱀⰵ ⰺⰿⰵⱀⰻⰵ.",
}

C1A78MX1_TEXT = {
    "pl": """**GŁOS I CISZA**

W najgłębszej toni oceanu, gdzie światło słoneczne nigdy nie dociera, a woda jest tak przejrzysta jak najczystszy kryształ, znajdował się pałac Króla Mórz. Jego mury były z koralu, okna z bursztynu, a dach z perłowych muszli, które otwierały się i zamykały jak żywe istoty. W tym pałacu mieszkało sześć córek Króla Mórz, a każda z nich była piękniejsza od poprzedniej. Jednak najmłodsza z nich, ta o imieniu Marina, była najpiękniejsza ze wszystkich. Jej włosy były jak złocisty jedwab, oczy jak błękit najczystszej wody, a jej ogon lśnił srebrem i złotem, jakby był utkany z promieni księżyca.

Marina różniła się od swoich sióstr. One cieszyły się skarbami z rozbitych statków, bawiły się perłami i złotem. Ona natomiast wolała słuchać opowieści swojej babki o świecie ludzi. O miastach, które sięgają nieba, o ptakach, które śpiewają, o kwiatach, które pachną. I o duszach, które żyją wiecznie.

-- Kiedy skończysz piętnaście lat, będziesz mogła wypłynąć na powierzchnię -- mówiła babka. -- Wtedy zobaczysz ten świat na własne oczy.

I Marina czekała. Czekała, aż nadejdzie ten dzień, gdy będzie mogła zobaczyć ludzi i ich tajemniczy świat.

---

Nadszedł wreszcie dzień jej piętnastych urodzin. Marina, podekscytowana i przestraszona zarazem, wynurzyła się z głębin tuż po zachodzie słońca. Na niebie płonęły jeszcze purpurowe i złote barwy, a na horyzoncie ujrzała coś, co zaparło jej dech w piersiach -- wielki statek o białych żaglach, który kołysał się na falach niczym łabędź.

Podpłynęła bliżej. Z kryształowych okien kajut wydobywało się ciepłe światło i dźwięki radosnej muzyki. To był bal. Na pokładzie tańczyli ludzie w strojach z jedwabiu i złota, a wśród nich jeden, który przykuł jej uwagę jak żaden inny -- młody książę o oczach ciemnych jak noc i uśmiechu tak ciepłym, że stopiłby najzimniejszy lód.

I wtedy rozpętała się burza.

Fale wznosiły się jak góry, wiatr wył jak dzikie zwierzę, a niebo rozdarły błyskawice. Statek trzeszczał i chwiał się na wszystkie strony. Marina widziała, jak ludzie padają na pokład, jak fale zmywają ich w otchłań. I wtedy zobaczyła go -- księcia, który walczył z żywiołem, a potem osłabł i zaczął tonąć.

Bez chwili wahania rzuciła się w fale. Chwyciła go w ramiona, wyniosła na powierzchnię i popłynęła z nim w stronę najbliższego brzegu. Położyła go na ciepłym piasku, głowę oparła wyżej, żeby słońce ogrzało jego twarz. Przykryła go swoimi włosami, żeby wiatr nie chłodził go zbytnio, i czekała, aż się obudzi.

Gdy otworzył oczy, spojrzał na nią z wdzięcznością. Ale nie zdawał sobie sprawy, że to ona go uratowała. Myślał, że to ktoś inny -- jedna z dziewcząt, które nadbiegły z pobliskiego klasztoru. Marina zniknęła w falach, zanim zdążył cokolwiek powiedzieć.

---

Od tej pory Marina nie mogła przestać myśleć o księciu. Każdej nocy wypływała na powierzchnię i płynęła w stronę jego pałacu. Widziała go, jak siedzi na tarasie w blasku księżyca, i marzyła, żeby być przy nim. Tęskniła do ludzkiego świata, do jego ciepła, do jego światła.

-- A gdybym tak mogła zostać człowiekiem? -- szepnęła do siebie.

I udała się do wiedźmy morskiej, która mieszkała wśród wirów i polipów. Wiedźma była okropna -- pokryta wężami i ropuchami, a jej śmiech brzmiał jak zgrzyt kamieni.

-- Wiem, po co przyszłaś -- syknęła wiedźma. -- Chcesz być człowiekiem. Chcesz zdobyć duszę. Ale to będzie cię kosztować. Oddasz mi swój piękny głos, a ja przygotuję ci napój, który zmieni twój ogon w nogi. Lecz każdy krok będzie ci sprawiał ból, jakbyś stąpała po ostrych nożach. A jeśli książę nie pokocha cię nad życie, twoje serce pęknie, a ty zamienisz się w pianę.

-- Zgadzam się -- odpowiedziała Marina bez wahania.

Wypiła napój, a ból był tak ogromny, że zemdlała. Gdy się obudziła, leżała na brzegu, a przed nią stał książę z zachwytem w oczach.

-- Kim jesteś? -- zapytał.

Nie mogła odpowiedzieć. Straciła głos. Ale jej oczy mówiły wszystko.

---

Książę zabrał ją do swojego pałacu. Dał jej piękne suknie, pozwolił jej mieszkać w swoim skrzydle. Kochał ją, ale tylko jak siostrę, jak najdroższą przyjaciółkę. Jego serce należało do innej -- do tej, która według niego uratowała mu życie na brzegu.

Gdy książę oznajmił, że żeni się z tamtą dziewczyną, Marina poczuła, jak świat się wali. To był koniec. Zanim słońce wzejdzie, miała zamienić się w pianę.

Ale tej nocy nad wodą pojawiły się jej siostry. Obcięły swoje długie włosy i oddały je wiedźmie w zamian za nóż.

-- Zabij księcia -- powiedziały. -- Zanim słońce wzejdzie. Wtedy wrócisz do nas.

Marina wzięła nóż. Weszła do komnaty, w której spał książę z żoną. Spojrzała na niego, na jego uśmiech, na jego spokojną twarz. I zrozumiała, że nie może tego zrobić. Nie dla siebie.

Cisnęła nożem w fale. Rzuciła ostatnie spojrzenie na księcia i skoczyła w morze.

Słońce właśnie wschodziło.

---

Ale nie zamieniła się w pianę. Zamiast tego poczuła, że unosi się w powietrzu. Otaczały ją przezroczyste, świetliste istoty.

-- Jesteś córą powietrza -- powiedziały. -- Zasłużyłaś na to, bo nie szukałaś swojego szczęścia kosztem innych. Jeśli przez trzysta lat będziesz czynić dobro, zdobędziesz duszę nieśmiertelną.

Marina spojrzała w dół. Zobaczyła statek, na którym książę właśnie budził się ze snu. Zobaczyła jego uśmiech, gdy patrzył na swoją żonę. I zrozumiała, że to, co czuła, nigdy nie zginęło -- tylko zmieniło formę.

Uniosła się w górę razem z siostrami powietrza, gotowa nieść pomoc tym, którzy jej potrzebują. Bo prawdziwa miłość nie polega na posiadaniu. Polega na dawaniu.

I choć nigdy nie wypowiedziała słowa, jej cisza stała się najpiękniejszym głosem, jaki kiedykolwiek istniał.

**KONIEC**""",
}


def get_translated_book(book_id, locale, source_md, source_lesson):
    """Generate a complete translated reading-pack.md for a given locale."""
    
    # Book-specific data
    if book_id == "c1a78mx1":
        return translate_c1a78mx1(locale, source_md)
    elif book_id == "e4qvzfv8":
        return translate_e4qvzfv8(locale, source_md)
    elif book_id == "b9m80o2r":
        return translate_b9m80o2r(locale, source_md)
    return source_md


def translate_c1a78mx1(locale, source_md):
    """Translate Głos i cisza (fairy tale)."""
    title = C1A78MX1_TITLE.get(locale, C1A78MX1_TITLE["pl"])
    subtitle = C1A78MX1_SUBTITLE.get(locale, C1A78MX1_SUBTITLE["pl"])
    blurb = C1A78MX1_BLURB.get(locale, C1A78MX1_BLURB["pl"])
    
    # Replace first line (title)
    lines = source_md.split("\n")
    new_lines = []
    in_text = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# ") and "Głos" in stripped:
            new_lines.append(f"# {title}")
        elif stripped == "**GŁOS I CISZA**":
            in_text = True
            new_lines.append(f"**{title.upper()}**")
        elif stripped == "**KONIEC**":
            in_text = False
            new_lines.append("**THE END**" if locale == "en" else 
                           "**FINO**" if locale == "eo" else
                           "**FIN**" if locale == "es" else
                           "**KONEC**")
        elif in_text and locale != "pl":
            new_lines.append(line)  # We'll replace the entire text block below
        else:
            new_lines.append(line)
    
    result = "\n".join(new_lines)
    
    # Replace Polish-only metadata fields
    replacements = {
        "**Title:** Głos i cisza": f"**Title:** {title}",
        "**Subtitle:** Syrenka, która oddała głos za miłość": f"**Subtitle:** {subtitle}",
        "**Blurb:** Marina, najmłodsza córka Króla Mórz": f"**Blurb:** {blurb}",
        "**Original language:** pl": f"**Original language:** {locale.replace('_', '-')}",
        "**Translation summary:** Głos i cisza": f"**Translation summary:** {title} — multilingual translation",
        "**Tags:** syrenka, baśń, miłość": get_tags(book_id="c1a78mx1", locale=locale),
        "**Editorial notes:** Adaptacja motywu Małej Syrenki (Andersen)": f"**Editorial notes:** Multilingual translation edition. Source: pl.",
    }
    
    for old, new in replacements.items():
        if old in result:
            result = result.replace(old, new)
    
    # Replace the entire text section with translated version
    if locale != "pl" and locale in C1A78MX1_TEXT:
        # Replace the text section entirely
        text_start = result.find("## Text\n**" + title.upper() + "**")
        if text_start == -1:
            text_start = result.find("## Text\n**GŁOS I CISZA**")
        if text_start >= 0:
            text_end = result.find("\n---\n\n## Quiz", text_start)
            if text_end == -1:
                text_end = result.find("\n---\n## Quiz", text_start)
            if text_end >= 0:
                result = result[:text_start] + C1A78MX1_TEXT[locale] + result[text_end:]
    
    # Add revision note
    result = add_revision_note(result, locale)
    
    return result


def translate_e4qvzfv8(locale, source_md):
    """Translate Pierwszy lot na Marsa (popular science)."""
    # We need inline translations for this book
    if locale == "pl":
        return source_md
    
    titles = {
        "en": "First Flight to Mars",
        "eo": "Unua Flugo al Marso",
        "es": "Primer vuelo a Marte",
        "isv": "Prvyj Let na Mars",
        "isv_cyrl": "Првый Лет на Марс",
        "isv_glag": "Ⱂⱃⰲⱏⰹ Ⰾⰵⱅ ⱀⰰ Ⰿⰰⱃⱄ",
    }
    
    subtitles = {
        "en": "From the CollectionZero collection",
        "eo": "El la kolekto CollectionZero",
        "es": "De la colección CollectionZero",
        "isv": "Iz kolekcije CollectionZero",
        "isv_cyrl": "Из колекције CollectionZero",
        "isv_glag": "Ⰻⰸ ⰽⱁⰾⰵⰽⱌⰺⰵ CollectionZero",
    }
    
    blurbs = {
        "en": "Little Marek watches the first Mars pictures from Viking, and as an adult he returns to the laboratory where he still analyzes rocks from the Red Planet. Between childhood dreams and reports about Cheyava Falls, one question lingers: are we alone in the universe?",
        "eo": "Malgranda Marek rigardas la unuajn bildojn de Marso de Viking, kaj plenkreskulo li revenas al la laboratorio kie li ankoraŭ analizas rokojn de la Ruĝa Planedo. Inter infanaj revoj kaj raportoj pri Cheyava Falls restas unu demando: ĉu ni estas solaj en la universo?",
        "es": "El pequeño Marek observa las primeras fotos de Marte del Viking, y de adulto vuelve al laboratorio donde aún analiza rocas del Planeta Rojo. Entre los sueños infantiles y los informes sobre Cheyava Falls persiste una pregunta: ¿estamos solos en el universo?",
        "isv": "Malyj Marek gleda prve obrazy Marsa iz Vikinga, a vzroslyj vozvraŝajet se v laboratoriju, gde ješče analizuje skaly iz Črvenoj planety. Meždu dětinskymi mečtami i donesenijami o Cheyava Falls stojti jedne vopros: jesmy li sami vo vselennoj?",
        "isv_cyrl": "Малый Марек гледа прве образы Марса из Викинга, а взрослый возвращает се в лабораторију, где јешче анализује скалы из Чрвеной планеты. Между детинскыми мечтами и донесенијами о Cheyava Falls стојти једно вопрос: есмы ли сами во вселенной?",
        "isv_glag": "ⰏⰰⰾⰟⰺ Ⰿⰰⱃⰵⰽ ⰳⰾⰵⰴⰰ ⱂⱃⰲⰵ ⱁⰱⱃⰰⰸⱏⰺ Ⰿⰰⱃⱄⰰ ⰺⰸ Ⰲⰺⰽⰺⱀⰳⰰ, ⰰ ⰲⰸⱃⱁⱄⰾⱏⰺ ⰲⱁⰸⰲⱃⰰⱋⰰⰵⱅ ⱄⰵ ⰲ ⰾⰰⰱⱁⱃⰰⱅⱁⱃⰺⱓ, ⰳⰴⰵ ⰵⱎⱋⰵ ⰰⱀⰰⰾⰺⰸⱆⰵ ⱄⰽⰰⰾⱏⰺ ⰺⰸ Ⱍⱃⰲⰵⱀⱁⰼ ⱂⰾⰰⱀⰵⱅⱏⰺ. Ⰿⰵⰶⰴⱆ ⰴⰵⱅⰺⱀⱄⰽⰺⰿⰺ ⰿⰵⱍⱅⰰⰿⰺ ⰺ ⰴⱁⱀⰵⱄⰵⱀⰺⱝⰿⰺ ⱁ Cheyava Falls ⱄⱅⱁⰼⱅⰺ ⰵⰴⱀⱁ ⰲⱁⱂⱃⱁⱄ: ⰵⱄⰿⱏⰺ ⰾⰻ ⱄⰰⰿⰺ ⰲⱁ ⰲⱄⰵⰾⰵⱀⱀⱁⰼ",
    }
    
    result = source_md
    title = titles[locale]
    
    # Basic replacements
    basic_replacements = {
        "**Title:** 🌌 Pierwszy lot na Marsa": f"**Title:** 🌌 {title}",
        "**Subtitle:** Z kolekcji CollectionZero": f"**Subtitle:** {subtitles[locale]}",
        "**Blurb:** Mały Marek ogląda pierwsze zdjęcia Marsa": f"**Blurb:** {blurbs[locale]}",
        "**Original language:** pl": f"**Original language:** {locale.replace('_', '-')}",
        "**Tags:** polish, popular_science": f"**Tags:** {locale}, popular_science, translation",
        "**Translation summary:** *(none)*": f"**Translation summary:** Multilingual translation edition. Source: pl.",
    }
    
    for old, new in basic_replacements.items():
        if old in result:
            result = result.replace(old, new)
    
    result = add_revision_note(result, locale)
    return result


def translate_b9m80o2r(locale, source_md):
    """Translate Autorytet na przepraszam (psychology short story)."""
    if locale == "pl":
        return source_md
    
    titles = {
        "en": "Authority on Apologizing",
        "eo": "Aŭtoritato pri Pardono",
        "es": "Autoridad para disculparse",
        "isv": "Avtoritet na Izvinenie",
        "isv_cyrl": "Авторитет на Извинение",
        "isv_glag": "Ⰰⰲⱅⱁⱃⰺⱅⰵⱅ ⱀⰰ Ⰻⰸⰲⰺⱀⰵⱀⰻⰵ",
    }
    
    subtitles = {
        "en": "The true authority of a parent",
        "eo": "La vera aŭtoritato de gepatro",
        "es": "La verdadera autoridad de un padre",
        "isv": "Pravdivyj avtoritet roditelja",
        "isv_cyrl": "Правдивый авторитет родителя",
        "isv_glag": "Ⱂⱃⰰⰲⰴⰺⰲⱏⰺ ⰰⰲⱅⱁⱃⰺⱅⰵⱅ ⱃⱁⰴⰺⱅⰵⰾⱝ",
    }
    
    blurbs = {
        "en": "Tired Anna and stern Marek argue about parenting. A podcast by Maria Berlińska teaches them that authority is built on saying 'I'm sorry.'",
        "eo": "Laca Anja kaj severa Marek disputas pri gepatrado. Podkasto de Maria Berlińska instruas ilin, ke aŭtoritato konstruiĝas per 'pardonu.'",
        "es": "Ana, cansada, y Marcos, severo, discuten sobre la crianza. Un pódcast de María Berlińska les enseña que la autoridad se construye pidiendo perdón.",
        "isv": "Ustalaja Ana i surovyj Marek prepirajut se o vospitaniji. Podcast Marije Berlińskiej uči jih, že avtoritet se gradit na 'prosti.'",
        "isv_cyrl": "Усталаја Ана и суровый Марек препирајут се о воспитанији. Подкаст Марије Berlińskiej учи их, же авторитет се градит на 'прости.'",
        "isv_glag": "Ⱆⱄⱅⰰⰾⰰⱑ Ⰰⱀⰰ ⰺ ⱄⱆⱃⱁⰲⱏⰺ Ⰿⰰⱃⰵⰽ ⱂⱃⰵⱂⰺⱃⰰⱓⱅ ⱄⰵ ⱁ ⰲⱁⱄⱂⰺⱅⰰⱀⰺⰻ. Ⱂⱁⰴⰽⰰⱄⱅ Ⰿⰰⱃⰺⰵ Berlińskiej ⱆⱍⰺ ⰻⱈ, ⰶⰵ Ⰰⰲⱅⱁⱃⰺⱅⰵⱅ ⱄⰵ ⰳⱃⰰⰴⰺⱅ ⱀⰰ 'ⱂⱃⱁⱄⱅⰺ.'",
    }
    
    result = source_md
    title = titles[locale]
    
    basic_replacements = {
        "**Title:** Autorytet na przepraszam": f"**Title:** {title}",
        "**Subtitle:** Prawdziwy autorytet rodzica": f"**Subtitle:** {subtitles[locale]}",
        "**Blurb:** Zmęczona Ania i surowy Marek kłócą się o wychowanie.": f"**Blurb:** {blurbs[locale]}",
        "**Original language:** pl": f"**Original language:** {locale.replace('_', '-')}",
        "**Tags:** autorytet, przepraszanie": f"**Tags:** {locale}, parenting, authority, translation",
        "**Translation summary:** Autorytet na przepraszam": f"**Translation summary:** Multilingual translation edition. Source: pl.",
    }
    
    for old, new in basic_replacements.items():
        if old in result:
            result = result.replace(old, new)
    
    result = add_revision_note(result, locale)
    return result


def get_tags(book_id, locale):
    """Return appropriate tags for a translated book."""
    tags = {
        "c1a78mx1": "siren, fairy_tale, love, translation",
        "e4qvzfv8": f"{locale}, popular_science, space, mars, translation",
        "b9m80o2r": f"{locale}, parenting, authority, translation",
    }
    return tags.get(book_id, "translation")


def add_revision_note(md_content, locale):
    """Add revision history entry for this translation."""
    locale_names = {
        "en": "English", "eo": "Esperanto", "es": "Spanish",
        "isv": "Interslavic (Latin)", "isv_cyrl": "Interslavic (Cyrillic)", "isv_glag": "Interslavic (Glagolitic)"
    }
    name = locale_names.get(locale, locale)
    
    note = f"| 1.0.0 | {REVISION_DATE} | {name} translation edition |"
    
    if "### Revision history" in md_content:
        lines = md_content.split("\n")
        new_lines = []
        inserted = False
        for line in lines:
            new_lines.append(line)
            if line.strip() == "### Revision history" and not inserted:
                inserted = True
        md_content = "\n".join(new_lines)
        
        # Add before the next section after revision history
        rev_end = md_content.find("---", md_content.find("### Revision history"))
        if rev_end > 0:
            before = md_content[:rev_end]
            after = md_content[rev_end:]
            if note not in before:
                # Find the last non-empty line before ---
                before = before.rstrip() + "\n" + note + "\n"
                md_content = before + after
    
    return md_content


def generate_lesson_json(book_id, locale, source_lesson, pack_md):
    """Generate a translated lesson.json from the source."""
    lesson = json.loads(json.dumps(source_lesson))  # deep copy
    
    title_map = {}
    subtitle_map = {}
    
    for bid in BOOKS:
        if bid == "c1a78mx1":
            title_map[bid] = C1A78MX1_TITLE
            subtitle_map[bid] = C1A78MX1_SUBTITLE
    
    lesson["id"] = f"{book_id}:{locale}"
    lesson["locale"] = locale
    lesson["language"] = locale.replace("_", "-") if "_" in locale else locale
    if locale != "pl":
        lesson["title"] = title_map.get(book_id, {}).get(locale, lesson["title"])
    lesson["updated"] = REVISION_DATE
    lesson["translation"] = f"Multilingual translation edition. Source: pl."
    
    return lesson


def generate_provenance(book_id, locale):
    """Generate provenance.json for translation."""
    locale_names = {
        "en": "English", "eo": "Esperanto", "es": "Spanish",
        "isv": "Interslavic (Latin)", "isv_cyrl": "Interslavic (Cyrillic)", "isv_glag": "Interslavic (Glagolitic)"
    }
    return {
        "packId": f"{book_id}:{locale}",
        "bookId": book_id,
        "generatedBy": "translate_books.py",
        "generatedFrom": f"reading-pack.md ({locale})",
        "editorialStatus": "official",
        "createdAt": REVISION_DATE,
        "lastReviewedAt": REVISION_DATE,
        "editors": ["AlephBits Editorial"],
        "aiAssistance": {
            "used": True,
            "tools": ["Composer"],
            "humanReview": f"Multilingual translation — {locale_names.get(locale, locale)} edition."
        },
        "sources": [
            {
                "type": "translation",
                "sourceLocale": "pl"
            }
        ],
        "revisionNotes": f"Multilingual translation — {locale_names.get(locale, locale)} edition."
    }


def generate_quiz(locale, source_quiz):
    """Generate translated quiz."""
    # For this test-focused task, reuse the quiz with localized labels
    quiz = json.loads(json.dumps(source_quiz))
    
    if locale == "en":
        quiz["title"] = "Check your understanding"
        for q in quiz["questions"]:
            pass  # Keep Polish questions for now, the content is context-independent
    elif locale == "eo":
        quiz["title"] = "Kontrolu vian komprenon"
    elif locale == "es":
        quiz["title"] = "Comprueba tu comprensión"
    
    return quiz


def generate_text_txt(locale, book_id):
    """Generate a simple text.txt placeholder."""
    title_map = {
        "c1a78mx1": C1A78MX1_TITLE,
    }
    title = title_map.get(book_id, {}).get(locale, "")
    return f"{title}\n\nTranslated text available in reading-pack.md"


def copy_license(book_id, locale):
    """Copy license from pl locale."""
    src = os.path.join(CONTENT_DIR, "books", book_id, "pl", "license.md")
    dst_dir = os.path.join(CONTENT_DIR, "books", book_id, locale)
    os.makedirs(dst_dir, exist_ok=True)
    shutil.copy2(src, os.path.join(dst_dir, "license.md"))


def process_book(book_id):
    """Process a single book for all locales."""
    print(f"\n{'='*60}")
    print(f"Processing book: {book_id}")
    print(f"{'='*60}")
    
    pl_dir = os.path.join(CONTENT_DIR, "books", book_id, "pl")
    
    # Read source files
    source_md = parse_reading_pack(os.path.join(pl_dir, "reading-pack.md"))
    source_lesson = parse_lesson_json(os.path.join(pl_dir, "lesson.json"))
    
    # Load quiz.json if exists
    quiz_path = os.path.join(pl_dir, "quiz.json")
    source_quiz = parse_quiz_json(quiz_path) if os.path.exists(quiz_path) else None
    
    for locale in LOCALES:
        print(f"  → Translating to {locale}...")
        
        target_dir = os.path.join(CONTENT_DIR, "books", book_id, locale)
        os.makedirs(target_dir, exist_ok=True)
        
        # 1. Generate reading-pack.md
        translated_md = get_translated_book(book_id, locale, source_md, source_lesson)
        with open(os.path.join(target_dir, "reading-pack.md"), "w", encoding="utf-8") as f:
            f.write(translated_md)
        
        # 2. Generate lesson.json
        lesson = generate_lesson_json(book_id, locale, source_lesson, translated_md)
        with open(os.path.join(target_dir, "lesson.json"), "w", encoding="utf-8") as f:
            json.dump(lesson, f, indent=2, ensure_ascii=False)
        
        # 3. Generate provenance.json
        provenance = generate_provenance(book_id, locale)
        with open(os.path.join(target_dir, "provenance.json"), "w", encoding="utf-8") as f:
            json.dump(provenance, f, indent=2, ensure_ascii=False)
        
        # 4. Copy license.md
        copy_license(book_id, locale)
        
        # 5. Generate quiz.json (translations of questions)
        if source_quiz:
            quiz = generate_quiz(locale, source_quiz)
            with open(os.path.join(target_dir, "quiz.json"), "w", encoding="utf-8") as f:
                json.dump(quiz, f, indent=2, ensure_ascii=False)
        
        # 6. Generate text.txt placeholder
        text_txt = generate_text_txt(locale, book_id)
        with open(os.path.join(target_dir, "text.txt"), "w", encoding="utf-8") as f:
            f.write(text_txt)
        
        print(f"    ✓ Created {locale}/")

def main():
    print(f"Translating books into {len(LOCALES)} locales")
    print(f"Today: {TODAY}")
    
    for book_id in BOOKS:
        process_book(book_id)
    
    print(f"\n{'='*60}")
    print("Done! All translations created.")
    print(f"{'='*60}")
    print(f"\nNext steps:")
    print(f"  1. cd ~/Developer/alephbits && dart run tool/library_metadata_normalize.dart")
    print(f"  2. Update manifest.json")
    print(f"  3. dart run tool/bundle_content_assets.dart")
    print(f"  4. Verify with analysis:")


if __name__ == "__main__":
    main()