---
name: fill-article
description: Fill a single article stub from its PDF. Use this skill whenever the user wants to extract metadata from one journal article PDF and populate the corresponding Hugo article stub files, fill in an article description from a PDF, extract title/authors/abstract/references from a scientific PDF for the NPE journal website, or mentions an article stub that needs to be filled with content from a PDF file. Also use when the user mentions "fill article", "process PDF", "extract from PDF" in the context of a single article, or asks to populate one empty article markdown file with data from its PDF document.
---

# Fill a Single Article Stub from PDF

This skill processes **one article at a time**: extracts structured metadata from a single journal article PDF and fills one pair of Hugo stub files (Russian + English) for the NPE journal website.

The user will typically invoke this repeatedly — once per article — to process an entire issue. Each invocation is independent.

## Input

For each invocation, identify these parameters from the user's request or context:

- **PDF path** — full path to the article PDF (e.g., `/Users/user/Downloads/YaEn_2_2026/01.pdf`)
- **Issue year and number** — e.g., `2026`, `2` for issue `2026-02`
- **Article number** — e.g., `01` (zero-padded two digits)

The stub files to fill are:
- `content/article/{year}/{issue:02d}/{number}.md` (Russian)
- `content_en/article/{year}/{issue:02d}/{number}.md` (English)

## PDF Structure

The journal PDFs follow a consistent bilingual format. Each article PDF contains:

1. **First page** (Russian): UDC, DOI, rubric heading, Russian title, authors with affiliations, abstract (Реферат), keywords (Ключевые слова), citation line (Для цитирования)
2. **Middle pages** (Russian): article body, then "Литература" (references in Russian), then "Авторы" section with full names, positions, and emails
3. **Last pages** (English): UDC, English title, authors, affiliations, Abstract, Keywords, For citation, References (in English), Authors section with English names

## Extraction Procedure

### 1. Read the PDF

Use PyPDF2 to extract text from all pages. You need:
- **First page text** — contains Russian metadata
- **Middle pages** — contains Russian references ("Литература")
- **Last 3–4 pages text** — contains English metadata, English references, and author details

Run the helper script:
```bash
python3 .crush/skills/fill-article/scripts/extract_pdf.py <pdf_path>
```

Or extract manually with PyPDF2. The script outputs JSON with `first_page_text`, `last_pages_text`, `full_text`, plus pre-extracted `udc`, `rubric_ru`, `rubric_en`, `first_page`, `last_page`, `authors_ru_text`, `authors_en_text`.

### 2. Extract fields

From the **first page** extract:

| Field | How to find it |
|---|---|
| **UDC** | Line starting with `УДК`, e.g. `УДК 621.039.51` → `621.039.51` |
| **Rubric** | The bilingual heading line like `АКТУАЛЬНЫЕ ПРОБЛЕМЫ ЯДЕРНОЙ ЭНЕРГЕТИКИ / CURRENT ISSUES IN NUCLEAR ENERGY` |
| **Title (RU)** | The main Russian heading, between the rubric line and the author list |
| **Authors** | Line of initials + surnames below the title: `М.А. Калугин, А.П. Лазаренко, ...` |
| **First page number** | The number at the very top of the first page |
| **Abstract (RU)** | Text after `Реферат.` up to `Ключевые слова:` — join hyphenated line breaks into continuous text |
| **Keywords (RU)** | Comma-separated list after `Ключевые слова:` |

From the **middle pages** (Russian references section):

| Field | How to find it |
|---|---|
| **References (RU)** | The `Литература` section — numbered list of references. Clean up PDF artifacts: rejoin broken words, remove spurious hyphens from line breaks |

From the **last pages** extract:

| Field | How to find it |
|---|---|
| **Title (EN)** | Heading above the `Abstract` section |
| **Abstract (EN)** | Text under `Abstract` up to `Keywords` or `Key words` |
| **Keywords (EN)** | Comma-separated list after `Keywords:` or `Key words:` |
| **References (EN)** | The `References` section — numbered list. **Note**: EN references may differ from RU references — EN versions sometimes include DOI links or different page numbers. Always extract RU and EN references independently from their respective PDF sections. |
| **Last page number** | The number at the top of the final page |
| **Author details** | The `Авторы`/`Authors` section — full names, positions, emails — needed for creating new author TOML files |

### 3. Map the rubric

Match the Russian rubric name from the PDF to the rubric key:

| Key | Russian | English |
|---|---|---|
| `currentissues` | Актуальные проблемы ядерной энергетики | Current issues in nuclear energy |
| `nuclearpowerplants` | Атомные электростанции | Nuclear power plants |
| `physicsandtechnolog` | Физика и техника ядерных реакторов | Physics and technology of nuclear reactors |
| `thermalphysics` | Теплофизика и теплогидравлика | Thermal physics and thermal hydraulics |
| `fuelcycle` | Топливный цикл и радиоактивные отходы | Fuel cycle and nuclear waste management |
| `safety` | Безопасность, надежность и диагностика ЯЭУ | Safety, reliability and diagnostics of NPI |
| `materials` | Материалы и ядерная энергетика | Nuclear materials |
| `coolants` | Химия, физика и техника теплоносителей | Chemistry, physics and technology of reactor coolants |
| `decommissioning` | Вывод из эксплуатации | Decommissioning |
| `environmentalaspects` | Экология ядерной энергетики | Environmental aspects of nuclear power |
| `directconversion` | Методы прямого преобразования ядерной энергии | Physics and methods for direct conversion of nuclear energy |
| `modeling` | Моделирование процессов в объектах ядерной энергетики | Modelling processes at nuclear facilities |
| `physics` | Физика в ядерной энергетике | Physics in nuclear power engineering |
| `medicine` | Ядерная медицина | Nuclear medicine and biology |
| `applicationofnucleartech` | Применение ядерных методов и средств | Application of nuclear tech |
| `training` | Подготовка кадров | Personnel training |
| `history` | История науки | History of science |
| `editors` | Колонка редактора | — |

Set `rubric` to the key. Set `rubric_name` to the Russian name in the RU stub, the English name in the EN stub.

### 4. Resolve authors

For each author listed in the PDF (by initials + surname):

1. Search existing author TOML files in `data/authors/*.toml` — match by the Russian `name` field (e.g., `name="Ю.А. Кузина"` matches `KuzinaJuA.toml`). This is the most reliable match because transliteration of the same Cyrillic letter can vary (e.g., `Ю` → `Yu` or `Ju`, `Я` → `Ya` or `Ja`, `Щ` → `Shch` or `Sch`).
2. If found, use that file's `term` value as the author identifier — **always use the existing term**, even if it uses a different transliteration scheme than you would pick.
3. **Update existing author files** with current data from the PDF's "Авторы"/"Authors" section: `work`, `regals`, `email`. Authors may have changed positions, affiliations, or emails since their TOML was created — the PDF reflects their current role for this specific article. **Check the affiliation** carefully: an author may have moved to a different organization (e.g., from IPPE to Proryv). Also normalize the TOML formatting to no spaces around `=` (see style guide below).
4. If not found, create new author TOML files in both `data/authors/` and `data_en/authors/`

**TOML style guide** — all author TOML files must use `key="value"` format with no spaces around `=`:
```toml
term="KamaevAA"
name="А.А. Камаев"
work="АО «ГНЦ РФ – ФЭИ»"
full_name="Камаев Алексей Альфредович"
regals="начальник департамента, к.т.н."
email="kamaev@ippe.ru"
```
When updating existing files, also fix any spacing inconsistencies (e.g., `term = "Foo"` → `term="Foo"`, `regals= "..."` → `regals="..."`).

**Term naming convention**: transliterated Surname + FirstInitial + PatronymicInitial (e.g., "Калугин Михаил Александрович" → `KaluginMA`).

**Transliteration ambiguities**: When creating new author terms, first check if a similar author already exists (search by surname prefix) to follow the same transliteration style used in the project. Common ambiguities: `Ю` → `Ju`/`Yu`, `Я` → `Ja`/`Ya`, `Щ` → `Shch`/`Sch`, `Ж` → `Zh`/`J`, `Х` → `Kh`/`Ch`/`H`.

Author data comes from the "Авторы" / "Authors" section at the end of the PDF, which lists each author's full name, position, and email. The PDF lists two affiliations (superscript numbers 1, 2) — map these to the correct organization names shown in the affiliation block.

**Same initials, different people**: Sometimes two different people share the same initials and surname pattern (e.g., `MarkelovAN` and `MarkelovVD`, `AbramovAN`/`AbramovLV` vs `AbramovSV`). Always verify the full name from the PDF against the existing TOML's `full_name` field to confirm it's the same person.

Author TOML format (Russian, `data/authors/`):
```toml
term="SurnameFI"
name="Ф.И. Фамилия"
work="Организация"
full_name="Фамилия Имя Отчество"
regals="должность, степень"
email="email@example.com"
authorid="1234567"
```

Author TOML format (English, `data_en/authors/`):
```toml
term="SurnameFI"
name="F.I. Surname"
work="Organization"
full_name="Surname FirstName Patronymic"
regals="position, degree"
email="email@example.com"
authorid="1234567"
```

The `authorid` and `email` fields are optional — only set them if the PDF provides this data. The `authorid` is the eLibrary AuthorID number shown in the PDF's "Авторы"/"Authors" section. Do not embed AuthorID into the `regals` field — keep it as a separate `authorid` field.

### 5. Write the filled stub files

Read the existing stub first to preserve the `date` field. Then overwrite with filled content.

#### Russian stub (`content/article/{year}/{issue:02d}/{number}.md`)

```toml
+++

categories="article"
date="{existing_date_from_stub}"
issue="{year}-{issue:02d}"
issue_name="{year} - №{issue:02d}"
number="{number}"
file="https://static.nuclear-power-engineering.ru/articles/{year}/{issue:02d}/{number}.pdf"
doi="https://doi.org/10.26583/npe.{year}.{issue_int}.{number_int}"
udc="{udc_value}"
first_page="{first_page}"
last_page="{last_page}"
rubric="{rubric_key}"
rubric_name="{rubric_name_ru}"
title="{title_ru}"
authors=["Term1", "Term2"]
tags=["tag1", "tag2"]

+++

{abstract_ru}

### Ссылки

{references_ru}
```

#### English stub (`content_en/article/{year}/{issue:02d}/{number}.md`)

```toml
+++

categories="article"
outputs=["HTML", "DOI"]
date="{existing_date_from_stub}"
issue="{year}-{issue:02d}"
issue_name="{year} - #{issue:02d}"
issue_id="{issue_number}"
number="{number}"
file="https://static.nuclear-power-engineering.ru/articles/{year}/{issue:02d}/{number}.pdf"
doi="https://doi.org/10.26583/npe.{year}.{issue_int}.{number_int}"
udc="{udc_value}"
first_page="{first_page}"
last_page="{last_page}"
rubric="{rubric_key}"
rubric_name="{rubric_name_en}"
title="{title_en}"
original_title="{title_ru}"
authors=["Term1", "Term2"]
tags=["tag1", "tag2"]

+++

{abstract_en}

### References

{references_en}
```

### 6. Special case: Article 00 (Editorial)

Article `00` is the editor's column:
- **Russian only** — do not create or modify an English stub
- No `doi`, `udc`, `first_page`, `last_page`, `authors`, `tags`, `number` fields
- `rubric="editors"`, `rubric_name="Колонка редактора"`, `title="Колонка редактора"`
- Body contains the editorial text extracted from the PDF (not abstract/references format)
- The editorial PDF is not named `00.pdf` — look for files like `0_03_Col_red_corr.pdf` in the issue directory
- The stub generated by `new-articles.py` will have extra empty fields (`doi`, `udc`, etc.) — remove them when writing the editorial

### Key details

- **Preserve the existing `date`** from the stub — don't overwrite it
- **DOI format**: `10.26583/npe.{year}.{issue_int}.{number_int}` — issue and article numbers are NOT zero-padded (e.g., `npe.2026.2.1`, not `npe.2026.02.01`); but the `number` field in front matter IS zero-padded (`"01"`)
- **Tags**: comma-separated keywords inside a TOML array
- **Citation line** in the PDF (`Для цитирования`) contains page numbers — use it to cross-check `first_page`/`last_page`
- **RU and EN references are independent** — do not copy RU references to the EN stub or vice versa. Each language has its own reference section in the PDF with potentially different formatting, DOIs, and page numbers.

### Markdown style guide

The body content (abstract and references) must follow these formatting rules:

- **Each sentence on its own line** — do not wrap sentences across multiple lines. One sentence = one line. This makes diffs readable and edits easy.
- **Valid markdown** — ensure the output renders correctly as Markdown. Use proper heading syntax (`###`), numbered lists for references, etc.
- **Empty line before paragraphs** — separate logical paragraphs with a blank line. The abstract is one paragraph; references section is another.
- **HTML tags for chemistry and isotope notation**:
  - Chemical formulas with subscripts: `UO<sub>2</sub>`, `CO<sub>2</sub>`, `H<sub>2</sub>O`, `PuO<sub>2</sub>`, `Na<sub>2</sub>O<sub>2</sub>`
  - Isotope mass numbers as superscript before the element: `<sup>235</sup>U`, `<sup>239</sup>Pu`, `<sup>137</sup>Cs`, `<sup>60</sup>Co`
  - Mathematical superscripts: `cos<sup>2</sup>`, `10<sup>-5</sup>`
  - Do NOT use plain text like `UO2` or `235U` — always use HTML tags
- **References cleanup**: PDF extraction introduces hyphenation artifacts — rejoin broken words, remove mid-word ` - ` from line wraps. Each reference should be on a single line.

### 7. RU/EN author TOML consistency checks

When creating or updating author TOML files, the RU and EN versions must be consistent. After writing both files, verify:

| Check | What to verify |
|---|---|
| **Same `term` value** | Both files must have identical `term="SurnameFI"` |
| **`work` matches** | RU `work` and EN `work` must be translations of each other (e.g., `АО «ГНЦ РФ – ФЭИ»` ↔ `JSC «SSC RF – IPPE»`) |
| **`regals` matches** | RU `regals` and EN `regals` must be translations of each other. **Never swap `work` and `regals`** — `work` is the organization, `regals` is the position/degree. A common bug is EN files having `regals` set to the organization name. |
| **`email` matches** | Both files must have the same email address |
| **`full_name` format** | RU: `"Фамилия Имя Отчество"` — EN: `"Surname FirstName Patronymic"` (surname first in both). Verify the EN transliteration matches the project's existing style for that surname (search by surname prefix). |
| **No missing fields** | If the RU file has a field (`email`, `regals`, `authorid`), the EN file should have it too, and vice versa. |

**Common inconsistencies to fix when found:**
- `work` and `regals` swapped in EN (regals contains org name instead of position)
- EN `regals` drops degree info present in RU (e.g., RU has `к.т.н.` but EN omits `Cand. Sci.`)
- EN `full_name` uses different transliteration than existing files for same surname
- Typos in EN: `(Engeneering)` → `(Engineering)`, missing closing parentheses
- Trailing commas or spaces in `regals` values

### 8. Verify

After writing, confirm:
1. Both stub files exist and have non-empty `title`, `authors`, `rubric`, `rubric_name`, `udc`, `first_page`, `last_page`
2. Each author term in `authors` matches an existing file in `data/authors/`
3. The rubric key is valid (exists in the mapping above)
4. `first_page` < `last_page`
5. The English stub has `original_title` set to the Russian title
