#!/bin/bash

# Create the apel user if it doesn't exist
if ! getent passwd apel >/dev/null; then
    useradd -r apel
fi
