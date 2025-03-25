#!/bin/sh

REMOTE_BRANCHES=$(git branch -rl)
LOCAL_BRANCHES=$(git branch)

if echo "${REMOTE_BRANCHES}" | grep -q "origin/master\|origin/main" || echo "${LOCAL_BRANCHES}" | grep -q "master\|main"; then
    docker image rm ${DOCKER_REGISTRY}/${CI_PROJECT_NAMESPACE}/${CI_PROJECT_NAME}:phys-${CI_COMMIT_REF_NAME}
    docker image rm ${DOCKER_REGISTRY}/${CI_PROJECT_NAMESPACE}/${CI_PROJECT_NAME}:virt-${CI_COMMIT_REF_NAME}
    docker image rm ${DOCKER_REGISTRY}/${CI_PROJECT_NAMESPACE}/${CI_PROJECT_NAME}:rom-${CI_COMMIT_REF_NAME}
    echo "[INFO] Docker image delete succeeded for ${DOCKER_REGISTRY}/${CI_PROJECT_NAMESPACE}/${CI_PROJECT_NAME}:${CI_COMMIT_REF_NAME}"
fi
