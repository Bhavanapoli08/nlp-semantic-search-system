import fitz
import pdfplumber
import re
import json
import os
from langdetect import detect
import pandas as pd
import datetime
import pdfreader


# ---------------------------------------------------
# Clean introduction text
# ---------------------------------------------------

def intro_extractor(intro_match):

    cleaned_intro = re.sub(
        r"\*Equal contribution.*?Copyright.*?\n",
        "",
        intro_match,
        flags=re.DOTALL,
    )

    cleaned_intro = re.sub(
        r"[\*\s;]*[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "",
        cleaned_intro,
    )

    cleaned_intro = re.sub(
        r"^Figure \d+[a-zA-Z]*\.\s+.*?(?=\n{2,}|\n\Z)",
        " ",
        cleaned_intro,
        flags=re.DOTALL,
    )

    cleaned_intro = re.sub(r"<.*?>", "", cleaned_intro)

    cleaned_intro = re.sub(
        r"\n\s*\d+\s*\n",
        "",
        cleaned_intro,
    )

    cleaned_intro = re.sub(
        r"arXiv:[\d\.]+v\d+.*?\n",
        "",
        cleaned_intro,
    )

    cleaned_intro = re.sub(r"\s{2,}", " ", cleaned_intro)

    return cleaned_intro


# ---------------------------------------------------
# Main PDF processing
# ---------------------------------------------------

def process_pdf(File_name, Title):

    title = Title
    published_date = ""
    authors = []

    doc = fitz.open(File_name)

    full_text = ""

    for page in doc:
        full_text += page.get_text()

    try:
        language = detect(full_text[:1000])
    except:
        language = "unknown"

    # ---------------------------------------------------
    # ABSTRACT
    # ---------------------------------------------------

    abstract_match = re.search(
        r"(?:^|\n)[\s\dIVX\.]*Abstract[\s\S]+?(?=\n[\s\dIVX\.]*(Keywords|Introduction|1\s*Introduction|I\.?\s*Introduction)\b)",
        full_text,
        re.DOTALL | re.IGNORECASE,
    )

    if abstract_match:

        abstract_text = abstract_match.group(0)

        abstract_text = re.sub(
            r"^[\s\dIVX\.]*Abstract\s*",
            "",
            abstract_text,
            flags=re.IGNORECASE,
        )

    else:

        abstract_text = "Not found"

    # ---------------------------------------------------
    # INTRODUCTION
    # ---------------------------------------------------

    intro_headers = list(
        re.finditer(
            r"(?:^|\n)[\s\dIVX\.]*Introduction\b",
            full_text,
            re.IGNORECASE,
        )
    )

    if intro_headers:
        full_text = full_text[intro_headers[-1].start():]

    full_text = re.sub(r"^(\s*\d{2,}\s*\n)+", "", full_text)

    intro_match = re.search(
        r"(?:^|\n)[\dIVX\. ]*Introduction[\s\S]+?(?=(?:\n+[\dIVX\.]+\s*(LITERATURE REVIEW|Method[s]?|Related Work|Background|Preliminaries|Experiment[s]?|Result[s]?|Discussion|Conclusion[s]?|Acknowledgement[s]?|Reference[s]?)[\:\-\s]*\b|\Z))",
        full_text,
        re.DOTALL | re.IGNORECASE,
    )

    if intro_match:

        intro_match = intro_extractor(
            intro_match.group(0).strip()
        )

        intro_match = re.sub(
            r"^[\dIVXivx\. ]*Introduction\s*",
            "",
            intro_match,
            flags=re.IGNORECASE,
        )

    else:

        intro_match = "Not found"

    # ---------------------------------------------------
    # RELATED WORK
    # ---------------------------------------------------

    related_work = re.search(
        r"(?:^|\n)[\dIVX\. ]*(?:Related Work|Literature Review)[\s\S]+?(?=\n[\dIVX\. ]*(Background|Preliminary|Method[s]?|Experiment[s]?|Result[s]?|Conclusion[s]?|Discussion)\b)",
        full_text,
        re.DOTALL | re.IGNORECASE,
    )

    if related_work:

        related_work = related_work.group(0).strip()

        related_work = re.sub(
            r"^[\dIVXivx\. ]*(Related Work|Literature Review)\s*",
            "",
            related_work,
            flags=re.IGNORECASE,
        )

    else:

        related_work = "Not found"

    # ---------------------------------------------------
    # BACKGROUND
    # ---------------------------------------------------

    background = re.search(
        r"(?:^|\n)[\dIVX\. ]*(?:Background)[\s\S]+?(?=\n[\dIVX\. ]*(Related Work|Method[s]?|Experiment[s]?|Result[s]?|Conclusion[s]?|Discussion)\b)",
        full_text,
        re.DOTALL | re.IGNORECASE,
    )

    if background:

        background = background.group(0).strip()

        background = re.sub(
            r"^[\dIVXivx\. ]*Background\s*",
            "",
            background,
            flags=re.IGNORECASE,
        )

    else:

        background = "Not found"

    # ---------------------------------------------------
    # PRELIMINARY
    # ---------------------------------------------------

    preliminary = re.search(
        r"(?:^|\n)[\dIVX\. ]*(?:Preliminary)[\s\S]+?(?=\n[\dIVX\. ]*(Method[s]?|Experiment[s]?|Result[s]?|Conclusion[s]?)\b)",
        full_text,
        re.DOTALL | re.IGNORECASE,
    )

    if preliminary:

        preliminary = preliminary.group(0).strip()

        preliminary = re.sub(
            r"^[\dIVXivx\. ]*Preliminary\s*",
            "",
            preliminary,
            flags=re.IGNORECASE,
        )

    else:

        preliminary = "Not found"

    # ---------------------------------------------------
    # METHOD
    # ---------------------------------------------------

    method = re.search(
        r"(?:^|\n)\s*[\dIVX]+[\.\)]?\s*(Method|Methods|Methodology)[\s\S]+?(?=(?:\n+[\dIVX\. ]*(Related Work|Experiment[s]?|Result[s]?|Conclusion[s]?|Discussion)\b)|\Z)",
        full_text,
        re.DOTALL | re.IGNORECASE,
    )

    if method:

        method = method.group(0).strip()

        method = re.sub(
            r"^[\dIVXivx\. ]*(Method|Methods|Methodology)\s*",
            "",
            method,
            flags=re.IGNORECASE,
        )

    else:

        method = "Not found"

    # ---------------------------------------------------
    # EXPERIMENTS
    # ---------------------------------------------------

    experiments = re.search(
        r"(?:^|\n)[\dIVX\. ]*(Experiment[s]?)[\s\S]+?(?=\n[\dIVX\. ]*(Result[s]?|Conclusion[s]?|Discussion)\b)",
        full_text,
        re.DOTALL | re.IGNORECASE,
    )

    if experiments:

        experiments = experiments.group(0).strip()

        experiments = re.sub(
            r"^[\dIVXivx\. ]*Experiment[s]?\s*",
            "",
            experiments,
            flags=re.IGNORECASE,
        )

    else:

        experiments = "Not found"

    # ---------------------------------------------------
    # RESULTS
    # ---------------------------------------------------

    results = re.search(
        r"(\n[\dIVX\. ]*(Result[s]?)\s*)[\s\S]+?(?=\n[\dIVX\. ]*(Conclusion[s]?|Discussion|Acknowledgement|Reference[s]?)\b)",
        full_text,
        re.DOTALL | re.IGNORECASE,
    )

    if results:

        results = results.group(0).strip()

        results = re.sub(
            r"^[\dIVXivx\. ]*Result[s]?\s*",
            "",
            results,
            flags=re.DOTALL | re.IGNORECASE,
        )

    else:

        results = "Not found"

    # ---------------------------------------------------
    # DISCUSSION
    # ---------------------------------------------------

    discussion = re.search(
        r"(\n[\dIVX\. ]*(Discussion)\s*)[\s\S]+?(?=\n[\dIVX\. ]*(Conclusion[s]?|Acknowledgement[s]?|Reference[s]?)\b)",
        full_text,
        re.DOTALL | re.IGNORECASE,
    )

    if discussion:

        discussion = discussion.group(0).strip()

        discussion = re.sub(
            r"^[\dIVXivx\. ]*Discussion\s*",
            "",
            discussion,
            flags=re.IGNORECASE,
        )

    else:

        discussion = "Not found"

    # ---------------------------------------------------
    # CONCLUSION
    # ---------------------------------------------------

    conclusion = re.search(
        r"(\n[\dIVX\. ]*(Conclusion[s]?)\s*)[\s\S]+?(?=\n[\dIVX\. ]*(Discussion|Acknowledgement[s]?|Reference[s]?)\b)",
        full_text,
        re.DOTALL | re.IGNORECASE,
    )

    if conclusion:

        conclusion = conclusion.group(0).strip()

        conclusion = re.sub(
            r"^[\dIVXivx\. ]*Conclusion[s]?\s*",
            "",
            conclusion,
            flags=re.IGNORECASE,
        )

    else:

        conclusion = "Not found"

    # ---------------------------------------------------
    # ACKNOWLEDGEMENTS
    # ---------------------------------------------------

    acknowledgements = re.search(
        r"(?:^|\n)[\dIVX\. ]*(Acknowledgement[s]?)[\s\S]+?(?=\n[\dIVX\. ]*(Reference[s]?|APPENDIX))",
        full_text,
        re.DOTALL | re.IGNORECASE,
    )

    if acknowledgements:

        acknowledgements = acknowledgements.group(0).strip()

        acknowledgements = re.sub(
            r"^[\dIVXivx\. ]*Acknowledgement[s]?\s*",
            "",
            acknowledgements,
            flags=re.IGNORECASE,
        )

    else:

        acknowledgements = "Not found"

    # ---------------------------------------------------
    # REFERENCES
    # ---------------------------------------------------

    references = re.search(
        r"(?:^|\n)\s*(References|Bibliography|REFERENCES)\s*\n([\s\S]+?)(?=\n\s*(Appendix|APPENDIX|Acknowledgement|ACKNOWLEDGEMENT|$))",
        full_text,
        re.IGNORECASE,
    )

    if references:

        references = references.group(0).strip()

        references = re.sub(
            r"^[\dIVXivx\. ]*(References|Bibliography)\s*",
            "",
            references,
            flags=re.IGNORECASE,
        )

        references = references.strip()

        references_text = re.findall(
            r"(?:^\d+\.\s+.+?(?=^\d+\.|\Z))|(?:^\[\d+\].+?(?=^\[\d+\]|\Z))",
            references,
            flags=re.MULTILINE | re.DOTALL,
        )

        references = [
            ref.strip()
            for ref in references_text
        ]

    else:

        references = []

    # ---------------------------------------------------
    # FIGURES
    # ---------------------------------------------------

    figures = re.findall(
        r"(?im)^\s*Fig(?:ure)?\.?\s*\d+[.:]?(?:\s*[A-Za-z]\)?)?[\s\S]*?(?=\s*(?:Fig\.|equation\s+\d+\.?|[\dIVX]+\.?\s|$))",
        full_text,
    )

    figure_data = [
        {"caption": fig.strip()}
        for fig in figures
    ]

    # ---------------------------------------------------
    # TABLES
    # ---------------------------------------------------

    pattern = r"""
        (?ms)
        (?:^|\r?\n\r?\n)
        (Table\s*\d+(?:\.|\:).*?)
        (?=\.\n{1,}|[A-Z]\.\s|\s*Table\s*\d+\.|\s*[A-Za-z]+\s*[A-Z]\d\s*)
    """

    tables = re.findall(
        pattern,
        full_text,
        flags=re.VERBOSE,
    )

    table_data = [
        {
            "caption": c.replace("\n", " ").strip()
        }
        for c in tables
    ]

    # ---------------------------------------------------
    # REFERENCES TEXT
    # ---------------------------------------------------

    if isinstance(references, list):
        references_text = "\n".join(references)
    else:
        references_text = str(references)

    # ---------------------------------------------------
    # FINAL JSON
    # ---------------------------------------------------

    ld_json = {

        "name": title,

        "datePublished": published_date,

        "inLanguage": language,

        "author": [
            {
                "@type": "Person",
                "name": name
            }
            for name in authors
        ],

        "articleBody": [

            {"ABSTRACT": abstract_text},

            {"INTRODUCTION": intro_match},

            {"RELATED WORK": related_work},

            {"PRELIMINARY": preliminary},

            {"BACKGROUND": background},

            {"METHOD": method},

            {"EXPERIMENTS": experiments},

            {"RESULTS": results},

            {"DISCUSSION": discussion},

            {"CONCLUSION": conclusion},

            # IMPORTANT
            {"REFERENCES": references_text},

            {"ACKNOWLEDGEMENTS": acknowledgements},
        ],

        "citations": references,

        "figure": figure_data,

        "table": table_data,
    }

    return ld_json
