import re
from dataclasses import dataclass
from typing import Optional, overload


@dataclass(order=True, init=False)
class Affiliation:

    designation: str
    badge: int

    @overload
    def __init__(self, designation: str, badge: int, /) -> None:
        ...

    @overload
    def __init__(self, string: str, /) -> None:
        ...

    def __init__(self, arg1: str, arg2: Optional[int] = None, /) -> None:

        if arg2 is not None:
            self.designation = arg1
            self.badge = arg2
            return

        else:

            string = arg1

            if not (match := self.PATTERN_AFFILIATION.match(string)):
                raise ValueError(f"not a designation: {string}")

            chapter_name = match.group("chapter_name")
            chapter_code = match.group("chapter_code")

            # https://github.com/python/typeshed/issues/263 # For findall
            if chapter_name:
                assert not chapter_code
                words: list[str] = self.PATTERN_WORD.findall(chapter_name)
            else:
                assert chapter_code
                characters: list[str] = self.PATTERN_CHARACTER.findall(chapter_code)
                words = [self.CHARACTER_TO_WORD[character] for character in characters]

            chapter_code = "".join(self.WORD_TO_CHARACTERS[word.title()][0] for word in words)

            self.designation = chapter_code
            self.badge = int(match.group("badge"))

    # Map of titlecase designation names to a sequence of possible,
    # capitalized, abbreviations. The first abbreviation is the primary one.
    # Note that some possible abbreviations are Latin lookalikes.
    WORD_TO_CHARACTERS = {
        "Alpha": "ΑαA",
        "Beta": "ΒβB",
        "Gamma": "Γγ",
        "Delta": "Δδ",
        "Epsilon": "ΕεE",
        "Zeta": "ΖζZ",
        "Eta": "ΗηH",
        "Theta": "Θθ",
        "Iota": "ΙιI",
        "Kappa": "ΚκK",
        "Lambda": "Λλ",
        "Mu": "ΜμM",
        "Nu": "ΝνN",
        "Xi": "Ξξ",
        "Omicron": "ΟοO",
        "Pi": "Ππ",
        "Rho": "ΡρP",
        "Sigma": "Σσς",
        "Tau": "ΤτT",
        "Upsilon": "ΥυY",
        "Phi": "Φφ",
        "Chi": "ΧχX",
        "Psi": "Ψψ",
        "Omega": "Ωω",
        # Because of Eta Mu (A) and (B) Chapters
        "(A)": ["(A)", "(a)"],
        "(B)": ["(B)", "(b)"],
    }

    CHARACTER_TO_WORD = {character: word for word, characters in WORD_TO_CHARACTERS.items() for character in characters}

    WORD = r"(?i:{})".format("|".join(re.escape(word) for word in WORD_TO_CHARACTERS.keys()))

    CHARACTER = "|".join(re.escape(character) for characters in WORD_TO_CHARACTERS.values() for character in characters)

    CHAPTER_NAME = fr"({WORD})(\s+({WORD}))*"

    CHAPTER_CODE = fr"({CHARACTER})+"

    DESIGNATION = fr"(?P<chapter_name>{CHAPTER_NAME})|(?P<chapter_code>{CHAPTER_CODE})"

    BADGE = "0*(?P<badge>[0-9]+)"  # Not exactly, but there's only two exceptions in all Sigma Nu

    AFFILIATION = fr"\s*({DESIGNATION})\s+({BADGE})\s*"

    PATTERN_AFFILIATION = re.compile(AFFILIATION)
    PATTERN_WORD = re.compile(WORD)
    PATTERN_CHARACTER = re.compile(CHARACTER)

    def __str__(self) -> str:
        return f"{self.designation}\N{NO-BREAK SPACE}{self.badge}"
