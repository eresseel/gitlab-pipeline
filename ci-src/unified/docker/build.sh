#!/bin/sh

TAG=$(cat version.txt)

if [ "${CI_COMMIT_REF_NAME}" = "${TAG}" ]; then
    echo "[INFO] Starting Docker build..."
    docker build \
        --build-arg VER="${CI_COMMIT_REF_NAME}" \
        --build-arg BUILT="$(date +"%Y-%m-%d %H:%M:%S")" \
        --build-arg CI_SERVER_HOST="${CI_SERVER_HOST}" \
        --build-arg CI_JOB_TOKEN="${CI_JOB_TOKEN}" \
        --build-arg CI_PROJECT_NAMESPACE="${CI_PROJECT_NAMESPACE}" \
        -t "${DOCKER_REGISTRY}/${CI_PROJECT_NAMESPACE}/${CI_PROJECT_NAME}:${CI_COMMIT_REF_NAME}" .

    if [ $? -eq 0 ]; then
        echo "[INFO] Docker build succeeded for ${DOCKER_REGISTRY}/${CI_PROJECT_NAMESPACE}/${CI_PROJECT_NAME}:${CI_COMMIT_REF_NAME}"
    else
        echo "[ERROR] Docker build failed"
        exit 1
    fi

    echo "[INFO] Starting Docker push..."
    docker push "${DOCKER_REGISTRY}/${CI_PROJECT_NAMESPACE}/${CI_PROJECT_NAME}:${CI_COMMIT_REF_NAME}"

    if [ $? -eq 0 ]; then
        echo "[INFO] Docker push succeeded for ${DOCKER_REGISTRY}/${CI_PROJECT_NAMESPACE}/${CI_PROJECT_NAME}:${CI_COMMIT_REF_NAME}"
    else
        echo "[ERROR] Docker push failed"
        exit 1
    fi
else
    echo "[ERROR] No matching conditions for Docker push"
fi
