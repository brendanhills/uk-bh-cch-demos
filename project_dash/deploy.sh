#!/bin/bash
# Shortcut to C4A Starter deployment pipeline
exec "$(dirname "$0")/deploy/deploy.sh" "$@"
