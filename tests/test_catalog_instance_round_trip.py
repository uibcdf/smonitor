"""Catalog instances must survive being rebuilt from their serialized form.

Python rebuilds an exception as `type(e)(*e.args)`. `pickle` and
`copy.deepcopy` both take that route, and so does pytest-xdist when a warning
crosses from a worker to the controller. The assumption behind it is that the
first constructor argument is the message.

These classes break that assumption on purpose: they render the message from
structured data, and their subclasses name that data first — `atom_name`,
`reason`, `resource`. Rebuilding through the constructor therefore feeds the
rendered sentence back into a domain field and the template renders around its
own output, which is what these tests exist to prevent.
"""

from __future__ import annotations

import copy
import pickle

import pytest

import smonitor
from smonitor.integrations import CatalogException, CatalogWarning

CODES = {
    "T-ATOM": {
        "user_message": "Atom name '{atom_name}' is not recognized.",
        "user_hint": "Provide an explicit atom type.",
    },
    "T-FORM": {"user_message": "Form '{form}' cannot be read."},
}


class AtomWarning(CatalogWarning):
    """The shape that breaks: a domain field where the message is expected."""

    catalog_key = "AtomWarning"

    def __init__(self, atom_name):
        super().__init__(code="T-ATOM", extra={"atom_name": atom_name})


class ComputedWarning(CatalogWarning):
    """Worse: the message is derived, so no constructor call can recover it."""

    catalog_key = "ComputedWarning"

    def __init__(self, names):
        super().__init__(code="T-ATOM", extra={"atom_name": ", ".join(sorted(names))})


class FormError(CatalogException):
    catalog_key = "FormError"

    def __init__(self, form):
        super().__init__(code="T-FORM", extra={"form": form})


@pytest.fixture(autouse=True)
def _configured():
    smonitor.configure(profile="user", handlers=[], codes=CODES)


@pytest.mark.parametrize(
    "instance",
    [
        AtomWarning(atom_name="Ar"),
        ComputedWarning(names=["CB", "CA"]),
        FormError(form="file:pdb"),
    ],
    ids=["domain-field", "computed", "exception"],
)
@pytest.mark.parametrize("rebuild", [
    pytest.param(lambda obj: pickle.loads(pickle.dumps(obj)), id="pickle"),
    pytest.param(copy.deepcopy, id="deepcopy"),
])
def test_round_trip_is_exact(instance, rebuild):
    rebuilt = rebuild(instance)

    assert type(rebuilt) is type(instance)
    assert str(rebuilt) == str(instance)
    assert rebuilt.code == instance.code
    assert rebuilt.extra == instance.extra
    assert rebuilt.args == instance.args


def test_the_message_is_not_rendered_a_second_time():
    """The failure this guards against, stated as the symptom it produced."""
    original = AtomWarning(atom_name="Ar")
    assert str(original).count("is not recognized") == 1

    rebuilt = pickle.loads(pickle.dumps(original))

    assert str(rebuilt).count("is not recognized") == 1, str(rebuilt)
    assert rebuilt.extra["atom_name"] == "Ar"


def test_unserializable_extra_refuses_instead_of_lying():
    """`extra` that cannot be serialized now raises where it used to corrupt.

    Before the state was carried, only `args` — a string — was pickled, so the
    call succeeded and the damage appeared on the far side as doubled text.
    `extra` is required to be serializable anyway: it goes into JSON events and
    into exported bundles.
    """
    smonitor.configure(profile="user", handlers=[], codes=CODES)
    offender = CatalogWarning(code="T-ATOM", extra={"handle": lambda: None})

    assert str(offender)  # rendering is unaffected
    with pytest.raises((pickle.PicklingError, AttributeError, TypeError)):
        pickle.dumps(offender)
