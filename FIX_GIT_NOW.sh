#!/bin/bash
# Quick fix script to reinitialize git in the correct directory

cd /mnt/c/Users/PC/MamaCare

echo "Current directory: $(pwd)"
echo "Checking for .git in parent directory..."

if [ -d "../.git" ]; then
    echo "WARNING: .git found in parent directory!"
    echo "This will remove the parent .git folder. Continue? (y/n)"
    read -r response
    if [ "$response" = "y" ]; then
        rm -rf ../.git
        echo "Removed parent .git folder"
    else
        echo "Aborted. Please fix manually."
        exit 1
    fi
fi

# Initialize git in current directory
if [ ! -d ".git" ]; then
    echo "Initializing git in MamaCare directory..."
    git init
fi

# Add all files
echo "Adding files..."
git add .

# Show status
echo "Git status:"
git status --short | head -20

echo ""
echo "Ready to commit! Run:"
echo "  git commit -m 'Initial commit - MamaCare project'"

