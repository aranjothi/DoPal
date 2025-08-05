#!/bin/bash

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to that directory
cd "$DIR"

# Make sure the executable is... executable
chmod +x DoPal

# Remove quarantine attribute if it exists
xattr -cr DoPal 2>/dev/null

# Run the app
./DoPal

# Keep terminal open if there's an error
if [ $? -ne 0 ]; then
    echo "Press any key to close..."
    read -n 1
fi 