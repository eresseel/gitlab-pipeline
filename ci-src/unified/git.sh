#!/bin/sh

git config --global user.email "${GIT_USER_EMAIL}"
git config --global user.name "${GIT_USER_NAME}"
git remote add api-origin "${CI_SERVER_PROTOCOL}://oauth2:${OAUTH2_TOKEN}@${CI_SERVER_HOST}/${CI_PROJECT_NAMESPACE}/${CI_PROJECT_NAME}.git"

echo "[INFO] Setting git configurations"
echo "[INFO] Email: $(git config --global user.email)"
echo "[INFO] User: $(git config --global user.name)"
