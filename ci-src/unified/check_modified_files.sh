#!/bin/sh

# Check modified files
MODIFIED_FILES=$(git diff --name-only HEAD^ HEAD)
EXPECTED_FILES="version.txt"
SORTED_MODIFIED_FILES=$(echo "${MODIFIED_FILES}" | tr ' ' '\n' | sort | tr '\n' ' ')
SORTED_EXPECTED_FILES=$(echo "${EXPECTED_FILES}" | tr ' ' '\n' | sort | tr '\n' ' ')

if [ "${SORTED_MODIFIED_FILES}" = "${SORTED_EXPECTED_FILES}" ]; then
    echo "[ERROR] Only version.txt has been modified"
    exit 1
fi
