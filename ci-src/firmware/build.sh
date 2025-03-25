#!/bin/sh

# Read the tag from version.txt
TAG=$(cat version.txt)

# Build and push the Docker image
if [ "${CI_COMMIT_REF_NAME}" = "${TAG}" ]; then
    echo "[INFO] Starting Docker build..."
    docker build -t ${DOCKER_REGISTRY}/${CI_PROJECT_NAMESPACE}/${CI_PROJECT_NAME}:phys-${CI_COMMIT_REF_NAME} --target physical_disk --build-arg CI_COMMIT_REF_NAME="${CI_COMMIT_REF_NAME}" --build-arg CI_COMMIT_SHORT_SHA="${CI_COMMIT_SHORT_SHA}" --build-arg CI_COMMIT_TIMESTAMP="${CI_COMMIT_TIMESTAMP}" --build-arg CI_COMMIT_TITLE="${CI_COMMIT_TITLE}" .
    docker build -t ${DOCKER_REGISTRY}/${CI_PROJECT_NAMESPACE}/${CI_PROJECT_NAME}:virt-${CI_COMMIT_REF_NAME} --target virtual_disk --build-arg CI_COMMIT_REF_NAME="${CI_COMMIT_REF_NAME}" --build-arg CI_COMMIT_SHORT_SHA="${CI_COMMIT_SHORT_SHA}" --build-arg CI_COMMIT_TIMESTAMP="${CI_COMMIT_TIMESTAMP}" --build-arg CI_COMMIT_TITLE="${CI_COMMIT_TITLE}" .
    docker build -t ${DOCKER_REGISTRY}/${CI_PROJECT_NAMESPACE}/${CI_PROJECT_NAME}:rom-${CI_COMMIT_REF_NAME} --target rom_file --build-arg CI_COMMIT_REF_NAME="${CI_COMMIT_REF_NAME}" --build-arg CI_COMMIT_SHORT_SHA="${CI_COMMIT_SHORT_SHA}" --build-arg CI_COMMIT_TIMESTAMP="${CI_COMMIT_TIMESTAMP}" --build-arg CI_COMMIT_TITLE="${CI_COMMIT_TITLE}" .
    docker push ${DOCKER_REGISTRY}/${CI_PROJECT_NAMESPACE}/${CI_PROJECT_NAME} --all-tags

    if [ $? -eq 0 ]; then
        echo "[INFO] Docker builds succeeded"
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
