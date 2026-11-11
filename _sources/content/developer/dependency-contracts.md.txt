# Dependency contracts

SMonitor has no required Python runtime provider. Python's supported range
(`>=3.11,<3.15`) is governed separately from provider version bounds.

| Optional feature | Minimum | Consumed surface |
| --- | --- | --- |
| Rich console | `rich>=13` | Console/Theme, Text, Panel, Rule and Table rendering |
| Pytest bridge | `pytest>=8` | pytest11 entry point and configuration/unconfiguration hooks |
| Canonical pytest evidence and QA | `pytest-receptor>=1.2` | Namespaced extension producers, incomplete-evidence reporting and artifact reader |

The pytest and receptor ceilings were removed under `uibcdf/smonitor#55`:
no observed incompatibility justified excluding their next major versions.
The reader still rejects unsupported evidence schemas; permissive requirements
do not certify future releases. These providers stay optional. Real Rich and
serial/xdist receptor contract tests protect the consumed operations.

The minimum cohort (Rich 13.0.0, pytest 8.0.0, receptor 1.2.0, xdist 3.6.1)
passed focused integration checks in a disposable Python 3.12 compatibility
environment. Routine development and the full suite use Python 3.14.7 with
Rich 15.0.0, pytest 9.1.1 and the installed receptor 1.2 source generation.
This is bounded compatibility evidence, not every provider/interpreter cross-product.

CI's exact receptor 1.2.0 selection and bounded qualification/build tools remain
reproducibility inputs, not product runtime ceilings. Setuptools >=77.0.3 is
the tested SPDX metadata floor; versioningit 3.x supplies the current version
configuration/build hook. Recipe host requirements and no-build-isolation QA
environments must supply that backend floor. Keep build tools separate from
consumer runtime dependencies, and review a future tool major before changing
its reproducibility contract.
