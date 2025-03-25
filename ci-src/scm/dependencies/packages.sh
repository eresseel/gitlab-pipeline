#!/bin/sh

# Check if other tools are installed
MISSING_TOOLS=""
for TOOL in git git-flow curl; do
    if ! command -v ${TOOL} >/dev/null 2>&1; then
        MISSING_TOOLS="${MISSING_TOOLS} ${TOOL}"
    fi
done

# Check if yq is installed
if ! command -v yq >/dev/null 2>&1; then
    MISSING_TOOLS="${MISSING_TOOLS} yq"
fi

if [ -z "${MISSING_TOOLS}" ]; then
    echo "[INFO] All required tools are already installed."
    exit 0
fi

if [ -f /etc/os-release ]; then
    OS=$(grep ^ID= /etc/os-release | cut -d'=' -f2 | tr -d '"')
else
    echo "[ERROR] Unable to detect the operating system."
    exit 1
fi

echo "[INFO] Detected operating system: ${OS}"

case "${OS}" in
    alpine)
        echo "[INFO] Installing missing tools on Alpine Linux..."
        apk update
        for TOOL in ${MISSING_TOOLS}; do
            if [ "${TOOL}" = "yq" ]; then
                echo "[INFO] Installing yq..."
                wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/local/bin/yq
                chmod +x /usr/local/bin/yq
            else
                echo "Installing ${TOOL}..."
                if ! apk add --no-cache ${TOOL}; then
                    echo "[ERROR] ${TOOL} installation failed."
                    exit 1
                fi
            fi
        done
        ;;
    debian|ubuntu)
        echo "[INFO] Installing missing tools on Debian/Ubuntu..."
        apt-get update -qq
        for TOOL in ${MISSING_TOOLS}; do
            if [ "${TOOL}" = "yq" ]; then
                echo "[INFO] Installing yq..."
                wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/local/bin/yq
                chmod +x /usr/local/bin/yq
            else
                echo "[INFO] Installing ${TOOL}..."
                if ! apt-get install -y -qq ${TOOL}; then
                    echo "[ERROR] ${TOOL} installation failed."
                    exit 1
                fi
            fi
        done
        ;;
    *)
        echo "[INFO] This operating system is not supported by this script."
        exit 1
        ;;
esac

# Verify installation
for TOOL in git git-flow curl yq; do
    if ! command -v ${TOOL} >/dev/null 2>&1; then
        echo "[ERROR] ${TOOL} installation failed."
        exit 1
    fi
done

echo "[INFO] All required tools installed successfully:"
echo "[INFO] Git: $(git --version)"
echo "[INFO] Git-flow: $(git-flow version 2>/dev/null || echo 'version info unavailable')"
echo "[INFO] Curl: $(curl --version | head -n 1)"
echo "[INFO] yq: $(yq --version)"
