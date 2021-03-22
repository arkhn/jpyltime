#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

uvicorn jpyltime.app:app --host="0.0.0.0" --port=7000 --root-path=${API_ROOT_PATH}
