# Devtools

This folder provides conda environment definitions and a conda-build recipe.

## Create conda environments

Development:

```bash
conda env create -f devtools/conda-envs/development_env.yaml -n smonitor-dev
```

Tests:

```bash
conda env create -f devtools/conda-envs/test_env.yaml -n smonitor-test
```

QA:

```bash
conda env create -f devtools/conda-envs/qa_env.yaml -n smonitor-qa
```

Docs:

```bash
conda env create -f devtools/conda-envs/docs_env.yaml -n smonitor-docs
```

Build:

```bash
conda env create -f devtools/conda-envs/build_env.yaml -n smonitor-build
```

## Build the conda package locally

Use the build environment for packaging:
The `meta.yaml` uses `GIT_DESCRIBE_TAG` for the version. Ensure your git tags are set or
export the variable before building.


## Maintained distribution inputs

`python devtools/check_distribution_inputs.py --suite-root /path/to/pinned/molsyssuite`
reviews the committed 15-route inventory, source resource paths and actual public
Python bounds. The provider checkout must match the inventory's full commit with
unmodified tools. Runtime requirements come from `pyproject.toml`; optional pytest
bridge/collective source checks do not create required public dependencies.

With `--candidate-sha FULL_SHA --output RECEIPT`, bootstrap reviews declarations
and requires executed exact-source full-matrix/policy jobs; this is separate from
installed-file qualification. Workflow changes need renewed manual review before
updating their inventory hashes. The publisher and promoter retain their local
version/file/public guards. Original public 0.18.0 and 0.19.0 evidence remains unchanged;
future releases need their own installed and public qualification.

Owning review: uibcdf/smonitor#35. Durable guard: tests/test_distribution_inputs.py.
