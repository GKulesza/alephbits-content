#!/usr/bin/env python3
"""Phase 97 — import Collection Seven stories (skip existing Nadwyżka)."""

from __future__ import annotations

import json
import math
import re
import subprocess
import unicodedata
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PACK_ROOT = REPO / "official" / "glagolitic" / "pl"
MANUSCRIPT = Path(
    "/Users/admin/Developer/MiscellaneousNotes/AwesomeVault/!Apps/App Ideas/alephBits/Books/CollectionSeven.md"
)
SKIP_SLUGS = {"nadwyzka"}
ROMAN = ("I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X")
WORDS_PER_MIN = 200


@dataclass
class QuizQ:
    question: str
    answers: tuple[str, str, str, str]
    correct: str
    explanation: str
    reference: str


@dataclass
class PackSpec:
    manuscript_title: str
    slug: str
    pack_id: str
    display_title: str
    subtitle: str
    blurb: str
    genres: str
    cover_family: str
    audience: str
    difficulty: int
    reader_stars: str
    trust: str
    tags: str
    keywords: str
    editorial_notes: str
    revision_notes: str
    philosophy_stars: int
    philosophy_note: str
    founder_notes: list[str] = field(default_factory=list)
    quiz: list[QuizQ] = field(default_factory=list)
    inspiration: str = ""
    youtube_ids: list[str] = field(default_factory=list)


def slugify(title: str) -> str:
    value = unicodedata.normalize("NFKD", title)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def pack_id_from_slug(slug: str) -> str:
    return f"polish_{slug.replace('-', '_')}"


@dataclass
class ParsedStory:
    title: str
    source_block: str
    body_raw: str
    youtube_ids: list[str]
    source_dates: list[str]


def parse_manuscript(path: Path) -> list[ParsedStory]:
    raw = path.read_text(encoding="utf-8")
    header = re.compile(
        r'^## (?:"([^"]+)"|([A-ZĄĆĘŁŃÓŚŹŻ][^\n"]+?))\s*$',
        re.MULTILINE,
    )
    matches = [m for m in header.finditer(raw) if not re.match(r"^\d", (m.group(1) or m.group(2)).strip())]
    stories: list[ParsedStory] = []

    for i, match in enumerate(matches):
        title = (match.group(1) or match.group(2)).strip()
        chunk = raw[match.end() : matches[i + 1].start() if i + 1 < len(matches) else len(raw)]

        source_block = ""
        src = re.search(r"```source\n(.*?)```", chunk, re.DOTALL)
        if src:
            source_block = src.group(1).strip()

        body = ""
        body_match = re.search(
            r"```source\n.*?```\s*\n+```\n(.*?)```",
            chunk,
            re.DOTALL,
        )
        if body_match:
            body = body_match.group(1).strip()
        else:
            blocks = re.findall(r"```[^\n]*\n(.*?)```", chunk, re.DOTALL)
            for block in blocks:
                if re.search(r"(?i)OPOWIADANIE|##\s+\d+\.\s+", block):
                    body = block.strip()
                    break
            if not body and blocks:
                body = blocks[-1].strip()
            if not source_block:
                for block in blocks:
                    if block is body or re.search(r"(?i)OPOWIADANIE|##\s+\d+\.\s+", block):
                        continue
                    if re.search(
                        r"youtube\.com|^\d{2}\.\d{2}\.\d{4}\s*->",
                        block,
                        re.M,
                    ):
                        source_block = block.strip()
                        break

        youtube_ids = re.findall(r"[?&]v=([A-Za-z0-9_-]{11})", source_block)
        youtube_ids += re.findall(r"->\s*([A-Za-z0-9_-]{11})\s*$", source_block, re.M)
        youtube_ids += re.findall(r"[?&]v=([A-Za-z0-9_-]{11})", body)
        dates = re.findall(r"(\d{2})\.(\d{2})\.(\d{4})", source_block or body)

        stories.append(
            ParsedStory(
                title=title,
                source_block=source_block,
                body_raw=body,
                youtube_ids=list(dict.fromkeys(youtube_ids)),
                source_dates=[f"{y}-{m}-{d}" for d, m, y in dates],
            )
        )
    return stories


def convert_body(body: str, display_title: str) -> str:
    text = body
    text = re.sub(r"^# OPOWIADANIE:.*?\n+", "", text, flags=re.I)
    text = re.sub(r"^---\s*\n+", "", text)

    def section_repl(m: re.Match[str]) -> str:
        num = int(m.group(1))
        name = m.group(2).strip()
        label = ROMAN[num - 1] if 0 < num <= len(ROMAN) else str(num)
        return f"\n## {label}. {name}\n"

    text = re.sub(r"^## (\d+)\.\s*(.+)$", section_repl, text, flags=re.M)
    text = re.sub(r"\n---\n+", "\n---\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    banner = f"**{display_title.upper()}**"
    if not text.startswith("**"):
        text = f"{banner}\n\n{text}"
    if "**KONIEC**" not in text:
        text += "\n\n**KONIEC**"
    return text


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def reading_minutes(text: str) -> int:
    return max(1, math.ceil(word_count(text) / WORDS_PER_MIN))


def render_quiz(questions: list[QuizQ]) -> str:
    lines = ["## Quiz", "", "**Quiz title:** Sprawdź zrozumienie", ""]
    for i, q in enumerate(questions, 1):
        lines.extend(
            [
                f"### Question {i}",
                "",
                f"**Question:** {q.question}",
                "",
                "**Answers:**",
                f"- A) {q.answers[0]}",
                f"- B) {q.answers[1]}",
                f"- C) {q.answers[2]}",
                f"- D) {q.answers[3]}",
                "",
                f"**Correct:** {q.correct}",
                f"**Explanation:** {q.explanation}",
                f"**Text reference:** {q.reference}",
                "",
            ]
        )
    return "\n".join(lines)


def render_reading_pack(spec: PackSpec, story: ParsedStory, text_body: str) -> str:
    est = reading_minutes(text_body)
    yt = story.youtube_ids[0] if story.youtube_ids else ""
    src_date = story.source_dates[0] if story.source_dates else "2026-07-12"
    source_url = f"https://www.youtube.com/watch?v={yt}" if yt else "*(none — manuscript)*"

    lines = [
        f"# {spec.display_title}",
        "",
        "## Metadata",
        "",
        f"**Pack ID:** `{spec.pack_id}`  ",
        "**Version:** 1.0.0  ",
        "**Edition version:** 1.0.0  ",
        "",
        f"**Title:** {spec.display_title}  ",
        f"**Subtitle:** {spec.subtitle}  ",
        f"**Blurb:** {spec.blurb}",
        "",
        f"**Genres:** {spec.genres}  ",
        "**Series:** Collection Seven  ",
        f"**Audience:** {spec.audience}",
        "",
        f"**Difficulty:** {spec.difficulty} (of 8)  ",
        f"**Reader difficulty:** {spec.reader_stars}  ",
        f"**Estimated reading time:** {est} minutes",
        "",
        "**Publication date:** *(original — 2026)*  ",
        "**Historical period:** contemporary  ",
        "",
        "**Original language:** pl  ",
        f"**Translation summary:** {spec.display_title} — Collection Seven official reading pack (Polish).  ",
        "",
        "**Writing system:** glagolitic  ",
        "**Recommended profile:** polish_default  ",
        f"**Recommended level:** {max(2, spec.difficulty - 2)}  ",
        "",
        f"**Tags:** {spec.tags}  ",
        "",
        f"**Keywords:** {spec.keywords}  ",
        "",
        f"**Cover family:** {spec.cover_family}",
        "",
        f"**Editorial notes:** {spec.editorial_notes}",
        "",
        "**Inspiration:** " + (spec.inspiration or "Collection Seven manuscript — editorial adaptation."),
        "",
        "---",
        "",
        "## Editorial Transparency",
        "",
        "**Created by:** AlephBits Editorial  ",
        "**Editor:** AlephBits Editorial  ",
        "**LLM assisted:** yes  ",
        "**LLM model:** Claude  ",
        "**Human reviewed:** yes — 2026-07-12  ",
        f"**Trust classification:** {spec.trust}  ",
        "**License:** CC0 1.0 Universal (SPDX: CC0-1.0)  ",
        "**License URL:** https://creativecommons.org/publicdomain/zero/1.0/  ",
        f"**Source block:** {story.source_block.replace(chr(10), ' / ') if story.source_block else '*(manuscript)*'}  ",
        f"**Revision notes:** {spec.revision_notes}",
        "",
        "### Revision history",
        "",
        "| Version | Date | Note |",
        "|---------|------|------|",
        "| 1.0.0 | 2026-07-12 | Collection Seven editorial import (Phase 97) |",
        "",
        "### Editorial history",
        "",
        "| Date | Editor | Note |",
        "|------|--------|------|",
        f"| 2026-07-12 | AlephBits Editorial | Phase 97 import; philosophy fit {spec.philosophy_stars}/5 — {spec.philosophy_note} |",
        "",
        "---",
        "",
        "## Sources",
        "",
        "### Source 1: Collection Seven manuscript",
        "",
        "**Author:** AlephBits Editorial (adaptation)  ",
        f"**URL:** {source_url}  ",
        "**License:** CC0 1.0 Universal (text); source material per original availability  ",
        f"**Retrieval date:** {src_date}  ",
        "**Availability:** adaptation  ",
        "**Deprecated:** no  ",
        "**Editor notes:** Materiał źródłowy wskazany w bloku source manuskryptu; tekst jest adaptacją redakcyjną.",
        "",
        "---",
        "",
        "## Text",
        "",
        text_body,
        "",
        "---",
        "",
        render_quiz(spec.quiz),
        "",
        "---",
        "",
        "## Future Extensions",
        "",
        "### Images",
        "*(none)*",
        "",
        "### Illustrations",
        "*(none)*",
        "",
        "### Audio narration",
        "*(none)*",
        "",
        "### Pronunciation",
        "*(none)*",
        "",
        "### Handwriting",
        "*(none)*",
        "",
        "### Exercises",
        "*(none)*",
        "",
        "### Vocabulary",
        "*(none)*",
        "",
    ]
    return "\n".join(lines)


def write_license(pack_dir: Path, title: str) -> None:
    pack_dir.mkdir(parents=True, exist_ok=True)
    (pack_dir / "license.md").write_text(
        f"# License\n\n**{title}** is released under **CC0 1.0 Universal** (public domain dedication).\n\n"
        "- SPDX: `CC0-1.0`\n"
        "- Full text: https://creativecommons.org/publicdomain/zero/1.0/\n\n"
        "You may copy, modify, and distribute this work for any purpose without asking permission.\n",
        encoding="utf-8",
    )


def write_provenance(pack_dir: Path, spec: PackSpec, story: ParsedStory) -> None:
    sources = [{"type": "youtube", "videoId": vid} for vid in story.youtube_ids]
    data = {
        "packId": spec.pack_id,
        "bookId": spec.slug,
        "editorialStatus": "official",
        "createdAt": "2026-07-12",
        "lastReviewedAt": "2026-07-12",
        "editors": ["AlephBits Editorial"],
        "aiAssistance": {
            "used": True,
            "tools": [],
            "humanReview": spec.revision_notes,
        },
        "sources": sources,
        "revisionNotes": spec.revision_notes,
        "philosophyFit": {
            "stars": spec.philosophy_stars,
            "note": spec.philosophy_note,
        },
    }
    (pack_dir / "provenance.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


PACKS: dict[str, PackSpec] = {
    "Zielona poświata": PackSpec(
        manuscript_title="Zielona poświata",
        slug="zielona-poswiata",
        pack_id="polish_zielona_poswiata",
        display_title="Zielona poświata",
        subtitle="Audycja na granicy rozrywki i ostrzeżenia",
        blurb="Krzysztof prowadzi nocną audycję „w celach rozrywkowych”, ale coraz częściej mówi o rzeczach, które brzmią jak przepowiednie. Od żółtego proszku po eliksir młodości — opowieść o głosie, który słucha tysięcy ludzi, i o granicy między teorią spiskową a lękiem.",
        genres="article, short_story",
        cover_family="psychology",
        audience="adult",
        difficulty=6,
        reader_stars="★★★☆☆",
        trust="Fiction",
        tags="audycja, conspiracja, fikcja, Collection Seven",
        keywords="zielona poświata, audycja, teorie, eliksir młodości",
        editorial_notes="Fikcja inspirowana formatem audycji; treści geopolityczne i spiskowe są narracją postaci, nie faktami katalogu.",
        revision_notes="Phase 97 import. Founder review zalecany przed promocją — wrażliwe tematy i ton sensacyjny.",
        inspiration="Manuskrypt Collection Seven; format audycji Q&A i motyw „jednego z nich”.",
        philosophy_stars=2,
        philosophy_note="Słabe dopasowanie do nauki i ciekawości — silny ton sensacyjny; może służyć jako ćwiczenie krytycznego czytania z wyraźnym fiction framing.",
        founder_notes=[
            "Founder note: Treści geopolityczne i spiskowe wymagają wyraźnego fiction framing w UI biblioteki.",
            "Founder note: Epilog z „nadnaturalnym” źródłem wiedzy — founder powinien potwierdzić, czy to pozostaje w katalogu oficjalnym.",
        ],
        quiz=[
            QuizQ(
                "Jak Krzysztof opisuje charakter swojej audycji na początku?",
                (
                    "Wyłącznie program informacyjny",
                    "Serię rozrywkową o teoriach konspiracyjnych",
                    "Poranny serwis pogodowy",
                    "Audycję muzyczną bez słowa",
                ),
                "B",
                "Mówi o „zielonej poświacie” jako serii rozrywkowej o teoriach konspiracyjnych.",
                "rozrywkowej serii",
            ),
            QuizQ(
                "Co Krzysztof znajduje w starym wpisie w notatkach sprzed trzech lat?",
                (
                    "Przepis na kawę",
                    "Wzmiankę o preparacie cofającym starzenie o 20 lat",
                    "List od redakcji",
                    "Harmonogram podróży",
                ),
                "B",
                "Przewija do wpisu o preparacie przedłużającym młodość o dokładnie 20 lat.",
                "cofając starzenie o 20 lat",
            ),
            QuizQ(
                "Co sugeruje anonimowy list po audycji o żółtym proszku?",
                (
                    "Że preparat nie istnieje i nigdy nie powstanie",
                    "Że preparat istnieje, ale ma ukryty warunek i dalsze konsekwencje",
                    "Że audycja zostanie nagrodzona",
                    "Że Krzysztof ma odejść z radia natychmiast",
                ),
                "B",
                "List mówi o preparacie działającym, lecz z warunkiem i przepowiednią degradacji.",
                "Preparat istnieje",
            ),
            QuizQ(
                "Jak kończy się pierwsza linia ostrzeżenia w drugim liście?",
                (
                    "Proszę więcej nagrywać",
                    "Powiedział pan za dużo — proszę przestać",
                    "Zapraszamy na konferencję",
                    "Prosimy o wywiad w TV",
                ),
                "B",
                "Drugi list wzywa do zaprzestania nagrań ze względu na bezpieczeństwo.",
                "Powiedział pan za dużo",
            ),
            QuizQ(
                "Co sugeruje ukryte nagranie w epilogu o „jednym z nich”?",
                (
                    "Że to zwykły słuchacz radia",
                    "Że to coś spoza ludzkiego, podpowiadające przez ludzi",
                    "Że to żart studia",
                    "Że to reklama suplementu",
                ),
                "B",
                "Nagranie mówi, że „jeden z nich” to coś przybysza, które zna przyszłość.",
                "to nie człowiek",
            ),
        ],
    ),
    "Czarna płachta": PackSpec(
        manuscript_title="Czarna płachta",
        slug="czarna-plachta",
        pack_id="polish_czarna_plachta",
        display_title="Czarna płachta",
        subtitle="Pełnia, audycja i przepowiednia",
        blurb="Krzysztof przy pełni księżyca prowadzi „Dzień po dniu” — audycję, w której mówi o tym, co „przypływa” do niego w ciszy. Iran, fronty pogodowe, trzęsienia ziemi: opowieść o człowieku, który czyta świat jak znak, i o małżeństwie, które nie wierzy w proroctwa, ale zostaje.",
        genres="article, short_story",
        cover_family="psychology",
        audience="adult",
        difficulty=5,
        reader_stars="★★★☆☆",
        trust="Fiction",
        tags="pełnia, audycja, przepowiednia, Collection Seven",
        keywords="czarna płachta, Iran, pełnia księżyca, audycja",
        editorial_notes="Fikcja o postaci-proroku; wydarzenia geopolityczne są narracją, nie prognozą katalogu.",
        revision_notes="Phase 97 import. Ten sam prowadzący co w „Zielonej poświacie” — founder decyduje o relacji serii.",
        inspiration="Manuskrypt Collection Seven; motyw pełni i audycji „Dzień po dniu”.",
        philosophy_stars=2,
        philosophy_note="Słabe dopasowanie naukowe; ciekawość tylko pośrednio — raczej fikcja o intuicji niż materiał edukacyjny.",
        founder_notes=[
            "Founder note: Postać Krzysztofa pojawia się też w „Zielonej poświacie” — rozważyć oznaczenie serii redakcyjnej.",
            "Founder note: Przepowiednie geopolityczne wymagają disclaimera fiction przy publikacji.",
        ],
        quiz=[
            QuizQ(
                "Dlaczego Krzysztof prowadzi audycję inaczej w noc pełni?",
                (
                    "Bo ma wtedy najwięcej słuchaczy w radiu",
                    "Bo przy pełni „przypływają” do niego poczucia o przyszłości",
                    "Bo wtedy nagrywa reklamy",
                    "Bo pełnia wyłącza internet",
                ),
                "B",
                "Mówi, że przy pełni ma luźne poczucia na przyszłość i szkoda ich nie wykorzystać.",
                "przy pełni",
            ),
            QuizQ(
                "Kim jest Anna w opowieści?",
                (
                    "Producentką radia",
                    "Żoną Krzysztofa, lekarką i racjonalistką",
                    "Słuchaczką z Iranu",
                    "Studentką astrologii",
                ),
                "B",
                "Anna wchodzi w szlafrok, jest lekarką i kwestionuje wpływ księżyca.",
                "żona Krzysztofa",
            ),
            QuizQ(
                "Co Krzysztof mówi o Iranie w rozwinięciu audycji?",
                (
                    "Że Iran całkowicie podda się bez walki",
                    "Że w czerwcu zaczną się okazjonalne ataki i „czarna płachta” opada na Iran",
                    "Że Iran zniknie z mapy w tydzień",
                    "Że Iran przejmie Unię Europejską",
                ),
                "B",
                "Przewiduje okazjonalne ataki w czerwcu i metaforę czarnej płachty nad Iranem.",
                "czarna płachta opada na Iran",
            ),
            QuizQ(
                "Co wydarza się w Europie w epilogu zgodnie z narracją?",
                (
                    "Całkowity brak upałów",
                    "Upały, ognisko Ebola we Włoszech, droższa żywność i nowy podatek UE",
                    "Zniknięcie wszystkich podatków",
                    "Koniec audycji Krzysztofa na zawsze",
                ),
                "B",
                "Epilog wymienia upały, ognisko we Włoszech, drożyznę i podatek infrastrukturalny.",
                "podatek infrastrukturalny",
            ),
            QuizQ(
                "Co pisze anonimowy list w styczniu 2027?",
                (
                    "Że audycja została zakazana prawnie",
                    "Że dzięki ostrzeżeniom zdążył wyjechać z Iranu i żyje",
                    "Że Krzysztof ma wygrać nagrodę Nobel",
                    "Że pełnia księżyca jest mitem",
                ),
                "B",
                "List dziękuje za ostrzeżenia i ucieczkę z Iranu przed katastrofą.",
                "zdążyłem wyjechać z Iranu",
            ),
        ],
    ),
    "Obserwator": PackSpec(
        manuscript_title="Obserwator",
        slug="obserwator",
        pack_id="polish_obserwator",
        display_title="Obserwator",
        subtitle="Rynek, mit i powrót Saturna",
        blurb="Michał traci oszczędności na kryptowalutach i sięga po książkę o mitologii. Spotkanie z astrolożką Ewą zmienia pytanie z „jak wygrać z rynkiem?” na „jak czytać cykle?” — opowieść o stracie kontroli i o powrocie do obserwacji zamiast walki.",
        genres="everyday_live, short_story",
        cover_family="everyday_live",
        audience="adult",
        difficulty=4,
        reader_stars="★★☆☆☆",
        trust="Fiction",
        tags="krypto, astrologia, cykle, Collection Seven",
        keywords="obserwator, trading, astrologia, Dumuzi, Bałtyk",
        editorial_notes="Fikcja metaforiczna; astrologia jest narzędziem narracyjnym postaci, nie nauką katalogu.",
        revision_notes="Phase 97 import. Blisko „Synchroniczności” — founder decyduje o obu na półce.",
        inspiration="Mitologia Dumuzi/Tammuz, Frazer „Złota Gałąź”, motyw powrotu Saturna.",
        philosophy_stars=3,
        philosophy_note="Akceptowalne jako metafora o cyklach i pokorze wobec niepewności; słaba strona — astrologia prezentowana niemal autentycznie.",
        founder_notes=[
            "Founder note: Near-duplicate struktury z „Synchronicznością” (krypto + astrolożka + Castaneda/Frazer).",
        ],
        quiz=[
            QuizQ(
                "Ile Michał traci na początku opowieści?",
                (
                    "Osiem tysięcy złotych",
                    "Dwadzieścia trzy tysiące złotych",
                    "Sto złotych",
                    "Milion złotych",
                ),
                "B",
                "Tekst mówi o stracie dwudziestu trzech tysięcy złotych.",
                "dwadzieścia trzy tysiące",
            ),
            QuizQ(
                "Jaką książkę kupuje w antykwariacie?",
                (
                    "Złotą Gałąź Jamesa George'a Frazera",
                    "Władcę Pierścieni",
                    "Encyklopedię kryptowalut",
                    "Horoskop roczny",
                ),
                "A",
                "Kupuje „Złotą Gałąź” Frazera.",
                "Złota Gałąź",
            ),
            QuizQ(
                "Co Ewa radzi Michałowi zamiast kontrolować rynek?",
                (
                    "Pożyczyć więcej kapitału",
                    "Obserwować cykle i uczyć się na nich surfować",
                    "Zrezygnować z pracy",
                    "Kupić tylko akcje banków",
                ),
                "B",
                "Ewa mówi o zrozumieniu rytmu i surfowaniu zamiast kontroli.",
                "surfować",
            ),
            QuizQ(
                "Ile zarabia Michał po pierwszej symbolicznej transakcji?",
                (
                    "Siedem złotych zysku",
                    "Dwadzieścia trzy tysiące zysku",
                    "Strata kolejnych ośmiu tysięcy",
                    "Nic — nie handluje",
                ),
                "A",
                "Zamyka pozycję z zyskiem siedmiu złotych.",
                "siedmiu złotych",
            ),
            QuizQ(
                "Gdzie kończy opowieść Michał patrząc na morze?",
                (
                    "Na plaży w Gdańsku",
                    "Na Wawelu",
                    "W laboratorium w Gdyni",
                    "W antykwariacie",
                ),
                "A",
                "Sześć miesięcy później stoi na plaży w Gdańsku.",
                "plaży w Gdańsku",
            ),
        ],
    ),
    "Synchroniczność": PackSpec(
        manuscript_title="Synchroniczność",
        slug="synchronicznosc",
        pack_id="polish_synchronicznosc",
        display_title="Synchroniczność",
        subtitle="Fale rynku i lekcja matematyki",
        blurb="Sebastian, nauczyciel matematyki, traci oszczędności na kryptowalutach. Uczeń Lena porównuje życie do równania z ujemną deltą, a psycholog Maria mówi o powrocie Saturna — opowieść o tym, że motywacja przychodzi po działaniu, nie przed nim.",
        genres="everyday_live, short_story",
        cover_family="everyday_live",
        audience="adult",
        difficulty=4,
        reader_stars="★★☆☆☆",
        trust="Fiction",
        tags="krypto, nauka, astrologia, Collection Seven",
        keywords="synchroniczność, delta, Castaneda, nauczyciel",
        editorial_notes="Fikcja o pokorze wobec rynku; astrologia jako metafora, nie porada inwestycyjna.",
        revision_notes="Phase 97 import. Near-duplicate z „Obserwatorem”.",
        inspiration="Castaneda, motyw fali/surfingu, lekcja o funkcji kwadratowej.",
        philosophy_stars=3,
        philosophy_note="Dobra metafora edukacyjna (delta, odpowiedzialność); słabsze — powtórzenie szablonu krypto+astro z „Obserwatorem”.",
        founder_notes=[
            "Founder note: Obserwator i Synchroniczność dzielą schemat — founder decyduje, czy oba mają być w katalogu.",
        ],
        quiz=[
            QuizQ(
                "Kim zawodowo jest Sebastian?",
                (
                    "Traderem z Wall Street",
                    "Nauczycielem matematyki w liceum",
                    "Astrolożką",
                    "Lekarzem",
                ),
                "B",
                "Jest nauczycielem matematyki w warszawskim liceum.",
                "nauczycielem matematyki",
            ),
            QuizQ(
                "Co Lena porównuje do życia Sebastiana?",
                (
                    "Funkcję z ujemną deltą — brak rozwiązania w szukanym miejscu",
                    "Pole trójkąta",
                    "Logarytm naturalny",
                    "Ciąg Fibonacciego",
                ),
                "A",
                "Mówi o funkcji kwadratowej bez rozwiązań rzeczywistych przy ujemnej delcie.",
                "ujemną deltą",
            ),
            QuizQ(
                "Ile Sebastian traci na początku?",
                (
                    "Osiem tysięcy złotych",
                    "Cztery tysiące złotych",
                    "Dwadzieścia trzy tysiące złotych",
                    "Nic",
                ),
                "A",
                "W jeden dzień traci osiem tysięcy złotych.",
                "osiem tysięcy",
            ),
            QuizQ(
                "Jaką kwotą otwiera pierwszą świadomą pozycję po przerwie?",
                (
                    "Sto złotych",
                    "Osiem tysięcy złotych",
                    "Czterdzieści tysięcy złotych",
                    "Jedno złote",
                ),
                "A",
                "Otwiera symboliczną pozycję za sto złotych.",
                "sto złotych",
            ),
            QuizQ(
                "Co Sebastian pisze do Marii po pierwszym miesiącu na plusie?",
                (
                    "Że to ona zarobiła za niego",
                    "Że to on zaufał sobie — dziękuje",
                    "Że rezygnuje z handlu",
                    "Że przenosi się do Gdańska",
                ),
                "B",
                "Maria odpowiada: to ty, zaufałeś sobie.",
                "Zaufałeś sobie",
            ),
        ],
    ),
    "Przerwa": PackSpec(
        manuscript_title="Przerwa",
        slug="przerwa-nauka",
        pack_id="polish_przerwa_nauka",
        display_title="Przerwa — rytm nauki",
        subtitle="Rozproszenie, biblioteka i powrót",
        blurb="Zosia walczy z farmakologią i ze swoim telefonem. Metoda Pomodoro, biblioteka medyczna i piosenka YUI pomagają jej zrozumieć, że motywacja przychodzi po działaniu — opowieść o przerwie, która nie jest ucieczką, lecz powrotem.",
        genres="everyday_live, short_story",
        cover_family="everyday_live",
        audience="family",
        difficulty=3,
        reader_stars="★★☆☆☆",
        trust="Fiction",
        tags="nauka, student, Pomodoro, Collection Seven",
        keywords="przerwa, farmakologia, Pomodoro, YUI, biblioteka",
        editorial_notes="Fikcja edukacyjna o nauce; tytuł „Przerwa” już istnieje w katalogu (Collection Four) — inna historia, inny slug.",
        revision_notes="Phase 97 import jako przerwa-nauka; nie nadpisuje polish_przerwa.",
        inspiration="Motyw przerwy w nauce; audycja Krzysztofa cytowana w tekście; YUI „again”.",
        philosophy_stars=4,
        philosophy_note="Dobre dopasowanie — czytanie, cierpliwość, szacunek do czytelnika-studenta; praktyczna metafora bez sensacji.",
        founder_notes=[
            "Founder note: Tytuł „Przerwa” koliduje z istniejącym packiem (Patryk / wypalenie). Użyto slug przerwa-nauka i tytuł „Przerwa — rytm nauki”.",
        ],
        quiz=[
            QuizQ(
                "Co studiuje Zosia?",
                (
                    "Farmakologię",
                    "Prawo",
                    "Astronomię",
                    "Historię sztuki",
                ),
                "A",
                "Egzamin z farmakologii za trzy tygodnie.",
                "farmakologii",
            ),
            QuizQ(
                "Jaką technikę stosuje w bibliotece?",
                (
                    "Metodę Pomodoro — 25 minut nauki",
                    "Naukę całą noc bez przerw",
                    "Tylko nagrania wideo",
                    "Grupowe projekty online",
                ),
                "A",
                "Włącza timer na 25 minut i notuje bez telefonu.",
                "25 minut",
            ),
            QuizQ(
                "Co Krzysztof mówi w audycji o zabieraniu się do rzeczy?",
                (
                    "Że trzeba czekać na entuzjazm",
                    "Że działanie jest jak klarowane masło — bez super energii na start",
                    "Że najlepiej nie robić nic",
                    "Że tylko pełnia księżyca pomaga",
                ),
                "B",
                "Cytuje metaforę klarowanego masła — bez entuzjazmu na początku.",
                "klarowane masło",
            ),
            QuizQ(
                "Jaki wynik egzaminu dostaje Zosia?",
                (
                    "Niezdany",
                    "Zaliczony z oceną 4,5",
                    "Ocena 2,0",
                    "Brak wyniku w tekście",
                ),
                "B",
                "Epilog: Zaliczone. Ocena: 4,5.",
                "4,5",
            ),
            QuizQ(
                "Jaką piosenkę YUI słucha podczas nauki?",
                (
                    "„again”",
                    "„Rolling Star”",
                    "Obie — „again” przy przełomie i „Rolling Star” po egzaminie",
                    "Żadnej",
                ),
                "C",
                "„again” pomaga w przełomie; po egzaminie włącza „Rolling Star”.",
                "again",
            ),
        ],
    ),
}


def import_story(spec: PackSpec, story: ParsedStory) -> Path:
    pack_dir = PACK_ROOT / spec.slug
    body = convert_body(story.body_raw, spec.display_title)
    rp = render_reading_pack(spec, story, body)
    write_license(pack_dir, spec.display_title)
    write_provenance(pack_dir, spec, story)
    (pack_dir / "reading-pack.md").write_text(rp, encoding="utf-8")
    return pack_dir


def run_cmd(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def main() -> None:
    stories = parse_manuscript(MANUSCRIPT)
    imported: list[str] = []
    skipped: list[str] = []

    for story in stories:
        slug = slugify(story.title)
        if slug in SKIP_SLUGS:
            skipped.append(f"{story.title} ({slug}) — already official")
            continue
        spec = PACKS.get(story.title)
        if not spec:
            raise ValueError(f"No PackSpec for story: {story.title}")
        if spec.slug in SKIP_SLUGS:
            skipped.append(story.title)
            continue
        import_story(spec, story)
        imported.append(f"{spec.display_title} → {spec.slug}")
        print(f"✓ {spec.slug}")

    print(f"\nImported {len(imported)} pack(s), skipped {len(skipped)}")
    for s in skipped:
        print(f"  skip: {s}")

    run_cmd(["dart", "run", "tools/compile_pack.dart", "--all", "--overwrite"], REPO)
    run_cmd(["dart", "run", "tools/build_manifest.dart"], REPO)
    run_cmd(["dart", "run", "scripts/validate_pack.dart"], REPO)

    app_repo = REPO.parent / "alephbits"
    if app_repo.exists():
        run_cmd(["dart", "run", "tool/bundle_content_assets.dart"], app_repo)
        run_cmd(["flutter", "test"], app_repo)

    print("Phase 97 import complete.")


if __name__ == "__main__":
    main()
