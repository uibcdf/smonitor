# Pending bugs

Confirmed or reproducible defects in current SMonitor behaviour.

Every entry is filed and closed under
[`../reporting_protocol.md`](../reporting_protocol.md): it carries front matter,
is tracked by a GitHub issue, and closes only when it names the test that fails
if the defect returns. A resolved entry moves to [`../archive/`](../archive/) —
it is not deleted, because deleting breaks every reference into it.

A document here is the analysis: what was measured, what was refuted, and what
the residue is. The issue carries the state. When the two disagree, the document
is right and the issue is stale — except at close, where the closing comment is
the final word.

The table below is generated from front matter by
`python devtools/devguide_index.py`. Do not edit it by hand.

<!-- generated: devguide_index -->

| entry | status | issue | summary |
| --- | --- | --- | --- |
| [`catalog_warnings_re_rendered_under_xdist.md`](catalog_warnings_re_rendered_under_xdist.md) | `blocked` | [uibcdf/smonitor#4](https://github.com/uibcdf/smonitor/issues/4) | A catalog hint interpolating a field cannot be re-rendered from args alone. |

<!-- /generated -->
