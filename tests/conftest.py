import pytest

from smonitor.core import manager as manager_module
from smonitor.core.context import _context_stack
from smonitor.emitters.exceptions import disable_exceptions
from smonitor.emitters.logging import disable_logging
from smonitor.emitters.warnings import disable_warnings


@pytest.fixture(autouse=True)
def _reset_smonitor_singleton():
    disable_logging()
    disable_warnings()
    disable_exceptions()
    # The breadcrumb stack lives in a ContextVar that outlives a test if a frame
    # is ever pushed without a matching pop, so clear it alongside the manager.
    _context_stack.set(None)
    manager_module._manager_singleton = manager_module.Manager()
    yield
    disable_logging()
    disable_warnings()
    disable_exceptions()
    _context_stack.set(None)
    manager_module._manager_singleton = None
