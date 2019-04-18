
import re
from dataclasses import dataclass, field

@dataclass(order=True)
class Affiliation:

    priority: int = field(default=1)
    designation: str
    badge: str

    # Map of titlecase designation names to a sequence of possible,
    # capitalized, abbreviations. The first abbreviation is the primary one.
    # Note that some possible abbreviations are Latin lookalikes.
    word_to_characters = {

        'Alpha': 'ΑαA',
        'Beta': 'ΒβB',
        'Gamma': 'Γγ',
        'Delta': 'Δδ',
        'Epsilon': 'ΕεE',
        'Zeta': 'ΖζZ',
        'Eta': 'ΗηH',
        'Theta': 'Θθ',
        'Iota': 'ΙιI',
        'Kappa': 'ΚκK',
        'Lambda': 'Λλ',
        'Mu': 'ΜμM',
        'Nu': 'ΝνN',
        'Xi': 'Ξξ',
        'Omicron': 'ΟοO',
        'Pi': 'Ππ',
        'Rho': 'ΡρP',
        'Sigma': 'Σσς',
        'Tau': 'ΤτT',
        'Upsilon': 'ΥυY',
        'Phi': 'Φφ',
        'Chi': 'ΧχX',
        'Psi': 'Ψψ',
        'Omega': 'Ωω',

        # Because of Eta Mu (A) and (B) Chapters
        '(A)': ['(A)', '(a)'],
        '(B)': ['(B)', '(b)'],

    }

    character_to_word = {
        character: word
        for word, characters in word_to_characters.items()
        for character in characters
    }

    word = r'(?i:{})'.format('|'.join(
        re.escape(word)
        for word in word_to_characters.keys()
    ))

    character = '|'.join(
        re.escape(character)
        for characters in word_to_characters.values()
        for character in characters
    )

    chapter_name = fr'({word})(\s+({word}))*'

    chapter_code = fr'({character})+'

    designation = fr'(?P<chapter_name>{chapter_name})|(?P<chapter_code>{chapter_code})'

    badge = '0*(?P<badge>[0-9]+)' # Not exactly, but there's only two exceptions in all Sigma Nu

    affiliation = fr'\s*({designation})\s+({badge})\s*'

    pattern_affiliation = re.compile(affiliation)
    pattern_word = re.compile(word)
    pattern_character = re.compile(character)

    @classmethod
    def from_string(cls, string, priority=1):

        match = cls.pattern_affiliation.match(string)
        chapter_name = match.group('chapter_name')
        chapter_code = match.group('chapter_code')

        if chapter_name:
            words = cls.pattern_word.findall(chapter_name)
        else: # chapter_code
            characters = cls.pattern_character.findall(chapter_code)
            words = map(cls.character_to_word.__getitem__, characters)

        chapter_code = ''.join(
            cls.word_to_characters[word.title()][0]
            for word in words
        )

        return cls(priority, chapter_code, int(str(match.group('badge'))))

    def __str__(self):
        return f'{self.designation}\N{NO-BREAK SPACE}{self.badge}'

