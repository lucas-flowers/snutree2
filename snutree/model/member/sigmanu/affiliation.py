import re
from dataclasses import dataclass
from enum import Enum
from typing import (
    Callable,
    Iterator,
    Optional,
    Sequence,
    Tuple,
    Union,
    overload,
)


@dataclass
class Token:
    name: str
    glyphs: Sequence[str]


class ChapterIdToken(Enum):
    """
    Valid letters in a chapter designation.

    Some characters in the short names may be Latin homoglyphs.
    """

    ALPHA = Token("Alpha", "ΑαA")
    BETA = Token("Beta", "ΒβB")
    GAMMA = Token("Gamma", "Γγ")
    DELTA = Token("Delta", "Δδ")
    EPSILON = Token("Epsilon", "ΕεE")
    ZETA = Token("Zeta", "ΖζZ")
    ETA = Token("Eta", "ΗηH")
    THETA = Token("Theta", "Θθ")
    IOTA = Token("Iota", "ΙιI")
    KAPPA = Token("Kappa", "ΚκK")
    LAMBDA = Token("Lambda", "Λλ")
    MU = Token("Mu", "ΜμM")
    NU = Token("Nu", "ΝνN")
    XI = Token("Xi", "Ξξ")
    OMICRON = Token("Omicron", "ΟοO")
    PI = Token("Pi", "Ππ")
    RHO = Token("Rho", "ΡρP")
    SIGMA = Token("Sigma", "Σσς")
    TAU = Token("Tau", "ΤτT")
    UPSILON = Token("Upsilon", "ΥυY")
    PHI = Token("Phi", "Φφ")
    CHI = Token("Chi", "ΧχX")
    PSI = Token("Psi", "Ψψ")
    OMEGA = Token("Omega", "Ωω")

    # Because of Eta Mu (A) and (B) Chapters
    A = Token("(A)", ("(A)", "(a)"))
    B = Token("(B)", ("(B)", "(b)"))


class ChapterId(Tuple[ChapterIdToken, ...]):  # https://github.com/python/mypy/issues/9522
    """
    Identifies a single chapter.
    """

    GLYPH_TO_TOKEN = {glyph: token for token in ChapterIdToken for glyph in token.value.glyphs}

    UPPER_NAME_TO_TOKEN = {token.value.name.upper(): token for token in ChapterIdToken}

    TOKEN_NAME = r"(?i:{})".format("|".join(re.escape(token.value.name) for token in ChapterIdToken))

    TOKEN_GLYPH = "|".join(re.escape(glyph) for token in ChapterIdToken for glyph in token.value.glyphs)

    CHAPTER_NAME = fr"({TOKEN_NAME})(\s+({TOKEN_NAME}))*"

    CHAPTER_CODE = fr"({TOKEN_GLYPH})+"

    CHAPTER_ID = fr"(?P<chapter_name>{CHAPTER_NAME})|(?P<chapter_code>{CHAPTER_CODE})"

    PATTERN_CHAPTER_ID = re.compile(f"^({CHAPTER_ID})$")
    PATTERN_TOKEN_NAME = re.compile(f"{TOKEN_NAME}")
    PATTERN_TOKEN_GLYPH = re.compile(f"{TOKEN_GLYPH}")

    @overload
    def __new__(cls, chapter_id: Tuple[ChapterIdToken, ...], /) -> "ChapterId":
        ...

    @overload
    def __new__(cls, string: str, /) -> "ChapterId":
        ...

    def __new__(cls, arg: Union[Tuple[ChapterIdToken, ...], str], /) -> "ChapterId":

        if isinstance(arg, tuple):
            return super().__new__(cls, arg)  # type: ignore[arg-type]

        if not (match := cls.PATTERN_CHAPTER_ID.match(arg)):
            raise ValueError(f"not a chapter identifier: {arg}")

        chapter_name = match.group("chapter_name")
        chapter_code = match.group("chapter_code")

        # https://github.com/python/typeshed/issues/263 # For findall
        if chapter_name:
            assert not chapter_code
            token_names: list[str] = cls.PATTERN_TOKEN_NAME.findall(chapter_name)
            tokens = tuple(cls.UPPER_NAME_TO_TOKEN[token_name.upper()] for token_name in token_names)
        else:
            assert chapter_code
            glyphs: list[str] = cls.PATTERN_TOKEN_GLYPH.findall(chapter_code)
            tokens = tuple(cls.GLYPH_TO_TOKEN[glyph] for glyph in glyphs)

        return cls(tokens)

    @classmethod
    def __get_validators__(cls) -> Iterator[Callable[[object], "ChapterId"]]:
        yield cls.validate

    @classmethod
    def validate(cls, value: object) -> "ChapterId":
        if isinstance(value, ChapterId):
            return value
        elif isinstance(value, str):
            return cls(value)
        else:
            raise TypeError("string or ChapterId required")

    def __str__(self) -> str:
        return "".join(token.value.glyphs[0] for token in self)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({str(self)!r})"


@dataclass(order=True, init=False)
class Affiliation:

    chapter_id: ChapterId
    member_id: int

    CHAPTER_IDENTIFIER = r"(?P<chapter_identifier>.*)"

    MEMBER_ID = "0*(?P<member_id>[0-9]+)"  # Not exactly, but there's only two exceptions in all Sigma Nu

    AFFILIATION = fr"\s*({CHAPTER_IDENTIFIER})\s+({MEMBER_ID})\s*"

    PATTERN_AFFILIATION = re.compile(f"^{AFFILIATION}$")

    @overload
    def __init__(self, chapter_id: ChapterId, member_id: int, /) -> None:
        ...

    @overload
    def __init__(self, string: str, /) -> None:
        ...

    def __init__(self, arg1: Union[ChapterId, str], arg2: Optional[int] = None, /) -> None:

        if isinstance(arg1, tuple) and isinstance(arg2, int):
            self.chapter_id = arg1
            self.member_id = arg2
            return

        assert isinstance(arg1, str) and arg2 is None

        string = arg1

        if not (match := self.PATTERN_AFFILIATION.match(string)):
            raise ValueError(f"not a chapter affiliation: {string}")

        self.__init__(ChapterId(match.group("chapter_identifier")), int(match.group("member_id")))  # type: ignore[misc] # pylint: disable=non-parent-init-called

    def __str__(self) -> str:
        return f"{self.chapter_id}\N{NO-BREAK SPACE}{self.member_id}"
