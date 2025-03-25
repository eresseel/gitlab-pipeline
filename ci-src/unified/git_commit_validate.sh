#!/bin/sh

GIT_SHOW_OUTPUT=$(git show "${CI_COMMIT_REF_NAME}")
LAST_COMMIT_EMAIL=$(echo "${GIT_SHOW_OUTPUT}" | grep '^Tagger:\|^Author:' | sed 's/.*<\(.*\)>/\1/' | head -n 1)

if [ "${LAST_COMMIT_EMAIL}" != "${GIT_USER_EMAIL}" ]; then
    echo "[ERROR] The commit email does not match with another email address"
    exit 1
else
    echo "[INFO] The commit email does match"
fi

LAST_COMMIT_TAG=$(git log -1 --pretty="%D")
TAG_REGEX="tag: [0-9]+\.[0-9]+\.[0-9]+"
if echo "${LAST_COMMIT_TAG}" | grep -qE "${TAG_REGEX}"; then
    echo "[INFO] Tag type is valid and found"
else
    echo "[ERROR] Tag type is invalid"
    exit 1
fi

if echo "${GIT_SHOW_OUTPUT}" | grep -qE "into '?(master|main)'?"; then
    echo "[INFO] Commit is on master or main branch"
else
    echo "[ERROR] Commit is not on master branch"
    exit 1
fi
