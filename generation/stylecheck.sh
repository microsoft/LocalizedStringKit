#!/bin/bash

pushd "${VIRTUAL_ENV}/.." > /dev/null

python -m black -l 100 localizedstringkit/*.py tests/*.py

python -m pylint --rcfile=pylintrc localizedstringkit tests
python -m mypy --ignore-missing-imports localizedstringkit/ tests/

popd > /dev/null
