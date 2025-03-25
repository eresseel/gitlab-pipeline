#!/bin/sh

echo "[INFO] Source branch: ${CI_MERGE_REQUEST_SOURCE_BRANCH_NAME}"
echo "[INFO] Target branch: ${CI_MERGE_REQUEST_TARGET_BRANCH_NAME}"

if [[ "${CI_MERGE_REQUEST_SOURCE_BRANCH_NAME}" =~ ^feature/[a-zA-Z0-9-]+$ ]]; then
    if [[ "${CI_MERGE_REQUEST_TARGET_BRANCH_NAME}" != "develop" ]]; then
        echo "[ERROR] Feature branches can only be merged into the develop branch."
        exit 1
    fi
    echo "[INFO] Feature branch is being merged into develop. Merge request can proceed."
elif [[ "${CI_MERGE_REQUEST_SOURCE_BRANCH_NAME}" =~ ^release/[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    if [[ "${CI_MERGE_REQUEST_TARGET_BRANCH_NAME}" != "master" && "${CI_MERGE_REQUEST_TARGET_BRANCH_NAME}" != "main" ]]; then
        echo "[ERROR] Release branches can only be merged into the master or main branch."
        exit 1
    fi
    echo "[INFO] Release branch is being merged into master/main. Merge request can proceed."
elif [[ "${CI_MERGE_REQUEST_SOURCE_BRANCH_NAME}" =~ ^hotfix/[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    if [[ "${CI_MERGE_REQUEST_TARGET_BRANCH_NAME}" != "develop" && "${CI_MERGE_REQUEST_TARGET_BRANCH_NAME}" != "master" && "${CI_MERGE_REQUEST_TARGET_BRANCH_NAME}" != "main" ]]; then
        echo "[ERROR] Hotfix branches can only be merged into the develop, master, or main branch."
        exit 1
    fi
    echo "[INFO] Hotfix branch is being merged into develop/master/main. Merge request can proceed."
else
    echo "[ERROR] Invalid branch name pattern."
    exit 1
fi
