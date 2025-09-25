#!/bin/sh
# Usage: ./json2base64.sh input.json
# input.json を base64エンコードして出力

if [ $# -lt 1 ]; then
  echo "Usage: $0 input.json"
  exit 1
fi

INPUT_FILE="$1"

if [ ! -f "$INPUT_FILE" ]; then
  echo "File not found: $INPUT_FILE"
  exit 2
fi

base64 -w 0 "$INPUT_FILE" | echo "$(cat)"
