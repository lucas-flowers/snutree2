from contextlib import nullcontext
from dataclasses import dataclass
from typing import ContextManager, Optional

import pytest

from snutree.model.member.sigmanu.affiliation import Affiliation
from tests.conftest import TestCase


@dataclass
class AffiliationTestCase(TestCase):
    string: str
    expected: Optional[str]


@pytest.mark.parametrize(
    "case",
    [
        # Basic abbreviated form
        AffiliationTestCase(
            id="basic-abbreviated",
            string="Α 3",
            expected="Α 3",
        ),
        AffiliationTestCase(
            id="basic-abbreviated",
            string="Π 5",
            expected="Π 5",
        ),
        AffiliationTestCase(
            id="basic-abbreviated",
            string="ΔA 132",
            expected="ΔΑ 132",
        ),
        AffiliationTestCase(
            id="basic-abbreviated",
            string="ABK 43925",
            expected="ΑΒΚ 43925",
        ),
        AffiliationTestCase(
            id="synonym-characters",
            string="Σςσ 5",
            expected="ΣΣΣ 5",
        ),
        AffiliationTestCase(
            id="upper-lower-and-lookalikes",
            string="αKΚ 43925",
            expected="ΑΚΚ 43925",
        ),
        AffiliationTestCase(
            id="upper-lower-and-lookalikes",
            string="AαΑ(A)(a) 5",
            expected="ΑΑΑ(A)(A) 5",
        ),
        AffiliationTestCase(
            id="greek-letters",
            string="ΗΜ 5",
            expected="ΗΜ 5",
        ),
        AffiliationTestCase(
            id="latin-letters",
            string="HM 5",
            expected="ΗΜ 5",
        ),
        AffiliationTestCase(
            id="zeros",
            string="Α 0",
            expected="Α 0",
        ),
        AffiliationTestCase(
            id="zeros",
            string="Α 000000",
            expected="Α 0",
        ),
        AffiliationTestCase(
            id="zeros",
            string="Α 0000001",
            expected="Α 1",
        ),
        AffiliationTestCase(
            id="zeros",
            string="(A)(A) 0023",
            expected="(A)(A) 23",
        ),
        AffiliationTestCase(
            id="basic-english-name",
            string="Alpha 5",
            expected="Α 5",
        ),
        AffiliationTestCase(
            id="basic-english-name",
            string="Delta Alpha 5",
            expected="ΔΑ 5",
        ),
        AffiliationTestCase(
            id="basic-english-name",
            string="(A) (B) (A) (B) 234",
            expected="(A)(B)(A)(B) 234",
        ),
        AffiliationTestCase(
            id="whitespace-in-name",
            string="        Alpha    \t    Beta\n\n\n      5    ",
            expected="ΑΒ 5",
        ),
        AffiliationTestCase(
            id="various-cases",
            string="sigma Sigma SIGMA sIgMa 5",
            expected="ΣΣΣΣ 5",
        ),
        AffiliationTestCase(
            id="invalid",
            string="alfa bravo xiii",
            expected=None,
        ),
        AffiliationTestCase(
            id="empty-string",
            string="",
            expected=None,
        ),
        AffiliationTestCase(
            id="needs-designation",
            string="6",
            expected=None,
        ),
        AffiliationTestCase(
            id="needs-designation",
            string=" 6",
            expected=None,
        ),
        AffiliationTestCase(
            id="no-number",
            string="Α",
            expected=None,
        ),
        AffiliationTestCase(
            id="no-number",
            string="A ",
            expected=None,
        ),
        AffiliationTestCase(
            id="no-positive-integer",
            string="A -5",
            expected=None,
        ),
        AffiliationTestCase(
            id="neither-a-greek-letter-nor-a-lookalike",
            string="a 5",
            expected=None,
        ),
        AffiliationTestCase(
            id="neither-a-greek-letter-nor-a-lookalike",
            string="D 5",
            expected=None,
        ),
        AffiliationTestCase(
            id="math-pi-product",
            string="∏ 6",
            expected=None,
        ),
        AffiliationTestCase(
            id="math-sigma-sum",
            string="∑ 6",
            expected=None,
        ),
        AffiliationTestCase(
            id="there-is-no-(C)",
            string="ΗΜ(C) 5",
            expected=None,
        ),
        AffiliationTestCase(
            id="there-is-no-(C)",
            string="Eta Mu (C) 5",
            expected=None,
        ),
        AffiliationTestCase(
            id="cannot-combine-word-form-and-character-form",
            string="HM (A) 5",
            expected=None,
        ),
        AffiliationTestCase(
            id="cannot-combine-word-form-and-character-form",
            string="Eta Mu(B) 5",
            expected=None,
        ),
        AffiliationTestCase(
            id="cannot-combine-word-form-and-character-form",
            string="(B)(B) (B) 5",
            expected=None,
        ),
    ],
)
def test_affiliation_from_string(case: AffiliationTestCase) -> None:

    context: ContextManager[object]
    if case.expected is None:
        context = pytest.raises(ValueError, match="not a designation")
    else:
        context = nullcontext()

    with context:
        assert str(Affiliation(case.string)) == case.expected


def test_affiliation_direct() -> None:
    assert str(Affiliation("Delta Alpha", 1000)) == "Delta Alpha 1000"
