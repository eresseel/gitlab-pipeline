#!/bin/sh

# Checks if version.txt exists
if [ ! -f version.txt ]; then
  echo "[ERROR] version.txt does not exist."
  exit 1
fi

VERSION=$(cat version.txt)
echo "[INFO] Detected version: ${VERSION}"

# Determines the current branch name
BRANCH_NAME=${CI_COMMIT_REF_NAME}
echo "[INFO] Current branch: ${BRANCH_NAME}"

# Regular expressions for version formats
SEMVER_SNAPSHOT_REGEX="^[0-9]+\.[0-9]+\.[0-9]+-SNAPSHOT$"
SEMVER_RELEASE_REGEX="^[0-9]+\.[0-9]+\.[0-9]+$"

# Branch validation
if echo "${BRANCH_NAME}" | grep -Eq "^develop|feature"; then
  # For develop or feature branches, -SNAPSHOT is required
  if echo "${VERSION}" | grep -qE "${SEMVER_SNAPSHOT_REGEX}"; then
    echo "[INFO] Version is valid for ${BRANCH_NAME} branch: ${VERSION}"
  else
    echo "[ERROR] ${BRANCH_NAME} branch should have a -SNAPSHOT version (e.g., 1.0.0-SNAPSHOT)."
    exit 1
  fi
elif echo "${BRANCH_NAME}" | grep -Eq "^master|main|release|hotfix"; then
  # For master, main, release, or hotfix branches, -SNAPSHOT is not allowed
  if echo "${VERSION}" | grep -qE "${SEMVER_RELEASE_REGEX}"; then
    echo "[INFO] Version is valid for ${BRANCH_NAME} branch: ${VERSION}"
  else
    echo "[ERROR] ${BRANCH_NAME} branch should have a release version (e.g., 1.0.0)."
    exit 1
  fi
else
  echo "[ERROR] Unrecognized branch ${BRANCH_NAME}."
  exit 1
fi
