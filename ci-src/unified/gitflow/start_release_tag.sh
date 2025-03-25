#!/bin/sh

RELEASE_TAG=$(cat version.txt)
RELEASE_TAG_MESSAGE="Set release tag version to ${RELEASE_TAG}"
DATA="
{
    \"name\": \"${RELEASE_TAG}\",
    \"tag_name\": \"${RELEASE_TAG}\",
    \"description\": \"${RELEASE_TAG_MESSAGE}\"
}"

if [ $(git tag -l "${RELEASE_TAG}") ]; then
    echo "[ERROR] Release tag ${RELEASE_TAG} already exists"
    exit 1
else
    git tag -a ${RELEASE_TAG} -m "${RELEASE_TAG_MESSAGE}"
    echo "[INFO] ${RELEASE_TAG_MESSAGE}"
    git push api-origin ${RELEASE_TAG}
    curl --header 'Content-Type: application/json' --header "PRIVATE-TOKEN: ${OAUTH2_TOKEN}" \
            --data "${DATA}" \
            --request POST ${CI_SERVER_PROTOCOL}://${CI_SERVER_HOST}/api/v4/projects/${CI_PROJECT_NAMESPACE}/${CI_PROJECT_NAME}/releases
fi
