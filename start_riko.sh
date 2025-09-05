#!/bin/bash

# === 1. Setting Python 3.10 Interpreter ===
PYTHON_CMD="python3.10"
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "Python 3.10 not found, Please install Python 3.10 or run install_reqs.sh first!"
    read -p "Press any key to continue..."
    exit 1
fi

# === 2. Finding GPT-SoVITS path ===
SOVITS_SUBDIR=""
for dir in GPT-SoVITS/*/; do
    if [ -d "$dir" ]; then
        SOVITS_SUBDIR="$dir"
        break
    fi
done

if [ -z "$SOVITS_SUBDIR" ]; then
    echo "GPT-SoVITS path not found."
    read -p "Press any key to continue..."
    exit 1
fi

echo "Found GPT-SoVITS Path: $SOVITS_SUBDIR"

# === 3. Starting GPT-SoVITS API ===
cd "$SOVITS_SUBDIR"
echo "Starting go-api.sh..."
./go-api.sh &
cd - > /dev/null

# === 4. Starting Riko ===
echo "Starting Riko..."
$PYTHON_CMD server/main_chat.py

read -p "Press any key to continue..."