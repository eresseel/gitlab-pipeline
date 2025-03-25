#!/bin/sh

lines=".ci
ci-src
.dockerignore
.gitlab-ci.yml
common-pipeline"

if [ -f .dockerignore ]; then
  echo "[INFO] The .dockerignore file exists. Appending lines to it."
else
  echo "[INFO] The .dockerignore file does not exist. Creating it"
  touch .dockerignore
fi

for line in ${lines}; do
  if ! grep -qx "${line}" .dockerignore; then
    echo "${line}" >> .dockerignore
  fi
done

echo "[INFO] The .dockerignore file has been updated"
