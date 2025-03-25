#!/bin/sh

TAG=$(cat version.txt)

if [ "${CI_COMMIT_REF_NAME}" = "${TAG}" ]; then
    docker image rm ${DOCKER_REGISTRY}/${CI_PROJECT_NAMESPACE}/${CI_PROJECT_NAME}:${CI_COMMIT_REF_NAME}
    echo "[INFO] Docker image delete succeeded for ${DOCKER_REGISTRY}/${CI_PROJECT_NAMESPACE}/${CI_PROJECT_NAME}:${CI_COMMIT_REF_NAME}"
fi
