# Pending proposals

Work that is not yet part of the contract: a design question, a capability
argued for, a decision recorded but not implemented.

Every entry is filed and closed under
[`../reporting_protocol.md`](../reporting_protocol.md): it carries front matter
and is tracked by a GitHub issue. A proposal closes as `resolved`, `withdrawn` or
`superseded`, and a resolved one names in `normative` the document that absorbed
its durable rules — a decision that leaves no rule anywhere has not landed.

`status: partial` is the honest state for a proposal that has been decided and
not yet implemented, and it is used here rather than described in prose.

The table below is generated from front matter by
`python devtools/devguide_index.py`. Do not edit it by hand.

<!-- generated: devguide_index -->

| entry | status | issue | summary |
| --- | --- | --- | --- |
| [`hint_ownership_on_catalog_instances.md`](hint_ownership_on_catalog_instances.md) | `partial` | [uibcdf/smonitor#5](https://github.com/uibcdf/smonitor/issues/5) | Which names the catalog base classes own, and whether hint returns. |
| [`pytest_diagnostics_bridge_and_molsyssuite_policy.md`](pytest_diagnostics_bridge_and_molsyssuite_policy.md) | `open` | [uibcdf/smonitor#6](https://github.com/uibcdf/smonitor/issues/6) | How SMonitor diagnostics participate in a pytest run, and what a policy layer owns. |

<!-- /generated -->
