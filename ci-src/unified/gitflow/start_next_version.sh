#!/bin/sh

CURRENT_VERSION=$(cat version.txt)
NEXT_VERSION=$(echo "$CURRENT_VERSION" | awk -v FS="." -v OFS="." '{ $2=$2+1; $3=0; print $1, $2, $3 }')-SNAPSHOT
NEXT_VERSION_MESSAGE="Set next development version to ${NEXT_VERSION}"

git fetch origin develop
git checkout develop
echo "${NEXT_VERSION}" > version.txt
git add version.txt
git commit -m"${NEXT_VERSION_MESSAGE}"
git push api-origin develop
