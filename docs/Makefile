# Minimal Makefile for Sphinx with catalog generation
SPHINXBUILD ?= sphinx-build
SOURCEDIR = .
BUILDDIR = _build

.PHONY: html

html:
	python _gen_catalog.py
	$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)"
