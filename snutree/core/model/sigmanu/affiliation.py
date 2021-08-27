import re
from dataclasses import dataclass
from typing import Optional, overload


@dataclass(order=True, init=False)
class Affiliation:

    priority: int
    designation: str
    badge: str

    @overload
    def __init__(self, designation: str, badge: str, /, priority: int) -> None:
        ...

    @overload
    def __init__(self, string: str, /, *, priority: int = ...) -> None:
        ...

    def __init__(self, arg1: str, arg2: Optional[str] = None, /, priority: int = 1) -> None:

        if isinstance(arg2, str):
            self.designation = arg1
            self.badge = arg2
            self.priority = priority
            return

        else:

            string = arg1

            if not (match := self.pattern_affiliation.match(string)):
                raise ValueError(f"not a designation: {string}")

            chapter_name = match.group("chapter_name")
            chapter_code = match.group("chapter_code")

            # https://github.com/python/typeshed/issues/263 # For findall
            if chapter_name:
                assert not chapter_code
                words: list[str] = self.pattern_word.findall(chapter_name)
            else:
                assert chapter_code
                characters: list[str] = self.pattern_character.findall(chapter_code)
                words = [self.character_to_word[character] for character in characters]

            chapter_code = "".join(self.word_to_characters[word.title()][0] for word in words)

            self.priority = priority
            self.designation = chapter_code
            self.badge = str(int(match.group("badge")))

    # Map of titlecase designation names to a sequence of possible,
    # capitalized, abbreviations. The first abbreviation is the primary one.
    # Note that some possible abbreviations are Latin lookalikes.
    word_to_characters = {
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

    character_to_word = {character: word for word, characters in word_to_characters.items() for character in characters}

    word = r"(?i:{})".format("|".join(re.escape(word) for word in word_to_characters.keys()))

    character = "|".join(re.escape(character) for characters in word_to_characters.values() for character in characters)

    chapter_name = fr"({word})(\s+({word}))*"

    chapter_code = fr"({character})+"

    designation = fr"(?P<chapter_name>{chapter_name})|(?P<chapter_code>{chapter_code})"

    badge = "0*(?P<badge>[0-9]+)"  # Not exactly, but there's only two exceptions in all Sigma Nu

    affiliation = fr"\s*({designation})\s+({badge})\s*"

    pattern_affiliation = re.compile(affiliation)
    pattern_word = re.compile(word)
    pattern_character = re.compile(character)

    def __str__(self) -> str:
        return f"{self.designation}\N{NO-BREAK SPACE}{self.badge}"
