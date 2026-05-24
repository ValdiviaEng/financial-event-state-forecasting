# Project convenience commands.
#
# This Makefile intentionally stays simple because the repository is currently a
# structural scaffold. The commands here focus on environment setup, directory
# creation, and future entry-point naming conventions rather than on executing a
# complete pipeline that does not yet exist.

PYTHON := python

.PHONY: install install-dev create-dirs lint format test

install:
	$(PYTHON) -m pip install -r requirements.txt

install-dev:
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -e .[dev]

create-dirs:
	mkdir -p data/raw/universe data/interim data/final data/embeddings data/kb data/manifests artifacts/checkpoints artifacts/figures artifacts/tables runs/logs reports notebooks .cache/huggingface/transformers .cache/torch

lint:
	$(PYTHON) -m ruff check src tests

format:
	$(PYTHON) -m black src tests

test:
	$(PYTHON) -m pytest
