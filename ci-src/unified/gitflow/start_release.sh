#!/bin/sh

RELEASE_VERSION=`echo $(cut -f1 -d'-' version.txt)`
RELEASE_MESSAGE="Set release version to ${RELEASE_VERSION}"
git fetch origin release/${RELEASE_VERSION} 2> /dev/null || true

if [ $(git branch -rl "origin/release/${RELEASE_VERSION}") ]; then
    echo "[ERROR] Release release/${RELEASE_VERSION} branch already exists"
    exit 1
else
    git checkout -b release/${RELEASE_VERSION}
    echo "${RELEASE_VERSION}" > version.txt
    git add version.txt
    git commit -m"${RELEASE_MESSAGE}"
    git push api-origin release/${RELEASE_VERSION}
fi
