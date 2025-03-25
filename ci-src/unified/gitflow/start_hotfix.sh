#!/bin/sh

HOTFIX_VERSION=`echo $(cat version.txt) | awk -v FS=.  -v NF=3 '{$3=$3+1}3'| sed 's/ /./g'`
HOTFIX_MESSAGE="Set hotfix version to ${HOTFIX_VERSION}"
git fetch origin hotfix/${HOTFIX_VERSION} 2> /dev/null || true

if [ $(git branch -rl "origin/hotfix/${HOTFIX_VERSION}") ]; then
    echo "[ERROR] Hotfix hotfix/${HOTFIX_VERSION} branch already exists"
    exit 1
else
    git checkout -b hotfix/${HOTFIX_VERSION}
    echo "${HOTFIX_VERSION}" > version.txt
    git add version.txt
    git commit -m"${HOTFIX_MESSAGE}"
    git push api-origin hotfix/${HOTFIX_VERSION}
fi
