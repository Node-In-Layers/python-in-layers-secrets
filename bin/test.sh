#!/bin/bash
poetry run pytest --cov=in_layers.secrets --cov-report=term-missing -q
