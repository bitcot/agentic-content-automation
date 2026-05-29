#!/bin/bash

set -e

echo "========================================="
echo " AI Dev Environment Auto Setup"
echo "========================================="

# Detect OS
OS="$(uname -s)"

echo "Detected OS: $OS"

install_claude_mac() {
    echo "Installing Claude Code on macOS..."

    # Install Homebrew if missing
    if ! command -v brew &> /dev/null; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi

    # Install git if missing
    if ! command -v git &> /dev/null; then
        brew install git
    fi
    
    # Install Node.js (npm is required for Claude Code)
    if ! command -v npm &> /dev/null; then
        echo "Installing Node.js..."
        brew install node
    fi

    echo "Installing Claude Code via npm..."
    sudo npm install -g @anthropic-ai/claude-code

    echo "Claude installed."
}

install_claude_linux() {
    echo "Installing Claude Code on Ubuntu/Linux..."

    sudo apt update
    sudo apt install -y git curl nodejs npm

    echo "Installing Claude Code via npm..."
    sudo npm install -g @anthropic-ai/claude-code

    echo "Claude installed."
}

install_claude_windows() {
    echo "Windows detected."
    echo "Please run this in PowerShell as Administrator to install Node.js and Claude Code:"
    echo ""
    echo "winget install OpenJS.NodeJS"
    echo "npm install -g @anthropic-ai/claude-code"
    echo ""
    # We won't exit here so it can still clone the repo if git is installed
}

clone_repo() {
    echo "Cloning repository..."
    
    # Replace with the repository you want to clone
    REPO_URL="https://github.com/vercel/nextjs-subscription-payments.git"

    if [ ! -d "project-repo" ]; then
        git clone "$REPO_URL" project-repo
    else
        echo "Repo already exists."
    fi
}

install_gstack() {
    echo "Installing gstack plugin for Claude..."
    
    if ! command -v bun &> /dev/null; then
        echo "Installing bun (required for gstack)..."
        curl -fsSL https://bun.sh/install | bash
        export PATH="$HOME/.bun/bin:$PATH"
    fi
    
    if [ ! -d "$HOME/.claude/skills/gstack" ]; then
        git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
        (cd ~/.claude/skills/gstack && ./setup)
    else
        echo "gstack already installed."
    fi
}

install_speckit() {
    echo "Installing speckit plugin for Claude..."
    if ! command -v uv &> /dev/null; then
        echo "Installing uv (required for speckit)..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
    fi
    # Install specify-cli from spec-kit
    uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@main || echo "speckit install failed."
    
    # Auto-initialize specify in the newly cloned repo
    if [ -d "project-repo" ]; then
        echo "Initializing spec-kit in project-repo..."
        (cd project-repo && ~/.local/bin/specify init . --integration claude --force)
    fi
}

# Main OS Logic
case "$OS" in
    Darwin)
        install_claude_mac
        ;;
    Linux)
        install_claude_linux
        ;;
    CYGWIN*|MINGW*|MSYS*)
        install_claude_windows
        ;;
    *)
        echo "Unsupported OS: $OS"
        exit 1
        ;;
esac

# Common setup
clone_repo

install_gstack
install_speckit

echo "========================================="
echo " Setup Complete"
echo "========================================="
echo ""
echo "To initialize and use spec-kit in your project, follow these steps:"
echo ""
echo "1. Initialize spec-kit in your project:"
echo "   cd project-repo"
echo "   specify init . --integration copilot"
echo ""
echo "2. Run Claude:"
echo "   claude"
echo ""
echo "3. Establish project principles:"
echo "   Use the \$speckit-constitution command inside Claude to create principles."
echo "   Example: \$speckit-constitution Create principles focused on code quality and testing."
echo ""
echo "4. Create the spec:"
echo "   Use the \$speckit-specify command to describe what you want to build."
echo "   Example: \$speckit-specify Build an application that can help me organize my photos..."
echo ""
echo "5. Create an implementation plan & tasks:"
echo "   Use \$speckit-plan, followed by \$speckit-tasks."
echo ""
echo "6. Execute implementation:"
echo "   Use \$speckit-implement to execute tasks according to the plan."
echo ""
