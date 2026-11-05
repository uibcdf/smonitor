---
summary: Qualify SPDX license metadata and the compatible backend minimum.
issue: uibcdf/smonitor#57
status: resolved
opened: 2026-11-04
closed: 2026-11-04
verification: measured
area: [maintenance, contracts]
guard: tests/test_license_artifacts.py
normative:
blocked_by: []
supersedes: []
---

# License metadata and build-tool review

Review completed: LICENSE is MIT with its original 2026 UIBCDF/HIMFG notice;
there are no other LICENSE/NOTICE/COPYING files in this source tree. SPDX
license="MIT" and license-files=["LICENSE"] replace the legacy table and
deprecated license classifier without changing notice bytes or project license.

The Setuptools minimum is 77.0.3, deliberately tested, aligned in pyproject,
Conda host, and maintained no-build-isolation QA/development/build environments.
Versioningit remains the separately governed 3.x build hook. Python bounds and
runtime dependencies are independent. Recipe/version-freezing and public
artifact identities are unchanged; no old archive is rebuilt or replaced.

Actual wheel+sdist builds and a wheel rebuilt from each sdist passed using
Setuptools 77.0.3 and 84.0.0, Python 3.14.7, versioningit 3.3.0, build 1.6.1,
wheel 0.48.0. All notices match SHA-256
201cca3f4381a6fe589d0ee2a0f88092d8d01465744df6eda0a16ac8ec2c35fc.
Both wheel types declare License-Expression: MIT and License-File: LICENSE.
These are local dirty-source administrative artifacts, not a published release.

devtools/check_license_artifacts.py performs the real artifact/rebuild check in
QA. Its guard rejects missing SPDX metadata and altered notices. A future normal
release still requires exact-source/installed/public qualification. Owner
confirmation is delivered to uibcdf/molsyssuite#162.

## Hosted environment correction, 2026-11-04

The first QA run 41949283481 passed tests/build but rejected the new sdist
rebuild because its no-build-isolation environment lacked wheel. The declared
backend set (Setuptools, versioningit, wheel) is now explicit in QA, development
and build environments. A distribution-input guard checks that each such
environment includes all declared backend tools. This preserves the original
failed run; local success with a prepopulated tool environment was not evidence
that the hosted environment already had those tools.
