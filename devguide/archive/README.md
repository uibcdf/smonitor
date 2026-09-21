# Archive

Closed reports: `resolved`, `withdrawn` and `superseded` entries, moved here from
`../pending_bugs/` and `../pending_proposals/` when their issue closed.

**Archived documents are immutable evidence.** They record what we believed, what
we measured, and what we ruled out, on the date we did. A claim that turns out to
be false gets an appended, dated correction note; the original claim is not
edited. A measurement that has since gone stale needs nothing — it was true when
taken.

They are kept rather than deleted because deleting breaks every reference into
them, which is the argument [`../reporting_protocol.md`](../reporting_protocol.md)
makes for issue numbers over paths, applied to our own files.

The directory is flat on purpose. There are few documents, it is read by search
rather than by browsing, and splitting it later would move files that are already
referenced. If navigating it ever becomes the problem, the answer is a generated
index, not moved files.

The table below is generated from front matter by
`python devtools/devguide_index.py`. Do not edit it by hand.

<!-- generated: devguide_index -->

| entry | status | issue | summary |
| --- | --- | --- | --- |
| [`adopt_molsyssuite_python_tooling_policy.md`](adopt_molsyssuite_python_tooling_policy.md) | `resolved` | [uibcdf/smonitor#12](https://github.com/uibcdf/smonitor/issues/12) | Adopt the shared Python and Ruff development baseline. |
| [`catalog_warnings_re_rendered_under_xdist.md`](catalog_warnings_re_rendered_under_xdist.md) | `resolved` | [uibcdf/smonitor#4](https://github.com/uibcdf/smonitor/issues/4) | A catalog hint interpolating a field cannot be re-rendered from args alone. |
| [`doi_badge_cites_molsysmt.md`](doi_badge_cites_molsysmt.md) | `resolved` | [uibcdf/smonitor#13](https://github.com/uibcdf/smonitor/issues/13) | The README DOI badge cites the MolSysMT archive. |
| [`frame_time_test_has_submicrosecond_boundary.md`](frame_time_test_has_submicrosecond_boundary.md) | `resolved` | [uibcdf/smonitor#18](https://github.com/uibcdf/smonitor/issues/18) | Avoid a one-microsecond false failure in the frame-time test |
| [`hint_ownership_on_catalog_instances.md`](hint_ownership_on_catalog_instances.md) | `resolved` | [uibcdf/smonitor#5](https://github.com/uibcdf/smonitor/issues/5) | Which names the catalog base classes own, and whether hint returns. |
| [`integrations_reach_through_a_partially_initialized_package.md`](integrations_reach_through_a_partially_initialized_package.md) | `resolved` | [uibcdf/smonitor#3](https://github.com/uibcdf/smonitor/issues/3) | The integrations reach through a package that is not finished being imported. |
| [`publish_one_staged_noarch_conda_artifact.md`](publish_one_staged_noarch_conda_artifact.md) | `resolved` | [uibcdf/smonitor#16](https://github.com/uibcdf/smonitor/issues/16) | Publish one staged noarch Conda artifact instead of interpreter-platform duplicates |
| [`publish_the_014_profile_message_fallback.md`](publish_the_014_profile_message_fallback.md) | `resolved` | [uibcdf/smonitor#8](https://github.com/uibcdf/smonitor/issues/8) | Publish the 0.14 profile-message fallback for downstream CI |
| [`receptor_misclassifies_composite_conda_publication.md`](receptor_misclassifies_composite_conda_publication.md) | `resolved` | [uibcdf/smonitor#10](https://github.com/uibcdf/smonitor/issues/10) | Use the release profile for the composite Conda publication workflow |
| [`release_upload_collides_with_staged_conda_coordinate.md`](release_upload_collides_with_staged_conda_coordinate.md) | `resolved` | [uibcdf/smonitor#19](https://github.com/uibcdf/smonitor/issues/19) | Release upload collides with a staged Conda build coordinate |
| [`verify_python_3_14_support_and_noarch_release.md`](verify_python_3_14_support_and_noarch_release.md) | `resolved` | [uibcdf/smonitor#17](https://github.com/uibcdf/smonitor/issues/17) | Establish verified Python 3.14 support and publish a noarch release |

<!-- /generated -->
