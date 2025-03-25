#!/bin/sh

# Check if required environment variables are set
if [ -z "${DOCKER_REGISTRY_USER}" ] || [ -z "${DOCKER_REGISTRY_PASSWORD}" ] || [ -z "${DOCKER_REGISTRY}" ]; then
    echo "[ERROR] Required environment variables DOCKER_REGISTRY_USER, DOCKER_REGISTRY_PASSWORD, or DOCKER_REGISTRY are not set"
    exit 1
fi

# Docker login
echo "[INFO] Logging into Docker registry..."
DOCKER_LOGIN_RESULT=$(docker login -u "${DOCKER_REGISTRY_USER}" -p "${DOCKER_REGISTRY_PASSWORD}" "${DOCKER_REGISTRY}" 2>&1)
if echo "${DOCKER_LOGIN_RESULT}" | grep -q "Login Succeeded"; then
    echo "[INFO] Docker login succeeded"
else
    echo "[ERROR] Docker login failed"
    exit 1
fi
