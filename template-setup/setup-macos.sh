#!/bin/bash
# macOS Development Environment Setup Script
# Requires macOS 10.15+ and Xcode Command Line Tools

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
GIT_USER_NAME="Developer"
GIT_USER_EMAIL="developer@example.com"
SKIP_DOCKER=false
SKIP_VSCODE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --git-name)
            GIT_USER_NAME="$2"
            shift 2
            ;;
        --git-email)
            GIT_USER_EMAIL="$2"
            shift 2
            ;;
        --skip-docker)
            SKIP_DOCKER=true
            shift
            ;;
        --skip-vscode)
            SKIP_VSCODE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --git-name NAME     Set Git user name (default: Developer)"
            echo "  --git-email EMAIL   Set Git user email (default: developer@example.com)"
            echo "  --skip-docker       Skip Docker installation"
            echo "  --skip-vscode       Skip Visual Studio Code installation"
            echo "  --help              Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

# Logging functions
log_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install Xcode Command Line Tools
install_xcode_tools() {
    if xcode-select -p >/dev/null 2>&1; then
        log_info "Xcode Command Line Tools already installed"
        return
    fi
    
    log_info "Installing Xcode Command Line Tools..."
    xcode-select --install
    
    # Wait for installation to complete
    log_info "Please complete the Xcode Command Line Tools installation in the popup window"
    log_info "Press any key to continue after installation is complete..."
    read -n 1 -s
}

# Install Homebrew
install_homebrew() {
    if command_exists brew; then
        log_info "Homebrew already installed"
        return
    fi
    
    log_info "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH for Apple Silicon Macs
    if [[ $(uname -m) == "arm64" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    
    log_success "Homebrew installed successfully"
}

# Install Git
install_git() {
    log_info "Installing Git..."
    brew install git
    
    # Configure Git
    log_info "Configuring Git..."
    git config --global user.name "$GIT_USER_NAME"
    git config --global user.email "$GIT_USER_EMAIL"
    git config --global init.defaultBranch main
    git config --global pull.rebase false
    git config --global core.autocrlf input
    git config --global core.safecrlf true
    
    log_success "Git installed and configured successfully"
}

# Install Visual Studio Code
install_vscode() {
    if [[ "$SKIP_VSCODE" == true ]]; then
        log_info "Skipping Visual Studio Code installation"
        return
    fi
    
    log_info "Installing Visual Studio Code..."
    brew install --cask visual-studio-code
    
    # Install extensions
    log_info "Installing VSCode extensions..."
    local extensions=(
        "ms-python.python"
        "ms-vscode.vscode-typescript-next"
        "esbenp.prettier-vscode"
        "dbaeumer.vscode-eslint"
        "ms-playwright.playwright"
        "ms-azuretools.vscode-docker"
        "bradlc.vscode-tailwindcss"
        "formulahendry.auto-rename-tag"
        "christian-kohler.path-intellisense"
        "mhutchie.git-graph"
    )
    
    for extension in "${extensions[@]}"; do
        log_info "Installing extension: $extension"
        code --install-extension "$extension" --force
    done
    
    log_success "Visual Studio Code installed with extensions"
}

# Install Docker Desktop
install_docker() {
    if [[ "$SKIP_DOCKER" == true ]]; then
        log_info "Skipping Docker installation"
        return
    fi
    
    log_info "Installing Docker Desktop..."
    brew install --cask docker
    
    log_success "Docker Desktop installed successfully"
    log_warning "Please start Docker Desktop manually from Applications"
}

# Install Node.js
install_nodejs() {
    log_info "Installing Node.js..."
    brew install node
    
    # Install global packages
    log_info "Installing global Node.js packages..."
    npm install -g yarn pnpm @playwright/test
    
    log_success "Node.js installed successfully"
}

# Install Python
install_python() {
    log_info "Installing Python..."
    brew install python@3.11
    
    # Install global packages
    log_info "Installing global Python packages..."
    pip3 install --upgrade pip
    pip3 install virtualenv pipenv black pylint
    
    log_success "Python installed successfully"
}

# Install Playwright browsers
install_playwright() {
    log_info "Installing Playwright browsers..."
    npx playwright install
    
    log_success "Playwright browsers installed successfully"
}

# Install Postman
install_postman() {
    log_info "Installing Postman..."
    brew install --cask postman
    
    log_success "Postman installed successfully"
}

# Configure VS Code settings
configure_vscode() {
    if [[ "$SKIP_VSCODE" == true ]]; then
        return
    fi
    
    log_info "Configuring VS Code settings..."
    local vscode_settings_dir="$HOME/Library/Application Support/Code/User"
    mkdir -p "$vscode_settings_dir"
    
    cat > "$vscode_settings_dir/settings.json" << EOF
{
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.fixAll.eslint": true
    },
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "files.autoSave": "afterDelay",
    "files.autoSaveDelay": 1000,
    "editor.tabSize": 2,
    "editor.insertSpaces": true,
    "editor.detectIndentation": false,
    "terminal.integrated.defaultProfile.osx": "zsh"
}
EOF
    
    log_success "VS Code settings configured"
}

# Create .gitignore template
create_gitignore() {
    log_info "Creating .gitignore template..."
    cat > .gitignore << EOF
# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/

# nyc test coverage
.nyc_output

# Dependency directories
jspm_packages/

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variables file
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Build outputs
dist/
build/
out/

# Docker
.dockerignore
Dockerfile
docker-compose.yml
EOF
    
    log_success ".gitignore template created"
}

# Main execution
main() {
    log_info "🚀 Starting macOS Development Environment Setup"
    echo "=================================================="
    
    # Check macOS version
    local macos_version=$(sw_vers -productVersion)
    log_info "macOS version: $macos_version"
    
    # Install prerequisites
    install_xcode_tools
    install_homebrew
    
    # Install development tools
    install_git
    install_vscode
    install_docker
    install_nodejs
    install_python
    install_playwright
    install_postman
    
    # Configure tools
    configure_vscode
    create_gitignore
    
    log_success "🎉 Development environment setup completed successfully!"
    echo ""
    log_info "📋 Next steps:"
    log_info "  1. Start Docker Desktop from Applications if installed"
    log_info "  2. Open Visual Studio Code and verify extensions are installed"
    log_info "  3. Run 'git --version' to verify Git installation"
    log_info "  4. Run 'node --version' to verify Node.js installation"
    log_info "  5. Run 'python3 --version' to verify Python installation"
    log_info "  6. Run 'npx playwright --version' to verify Playwright installation"
    echo ""
    log_info "🔧 Git configuration:"
    log_info "  Name: $GIT_USER_NAME"
    log_info "  Email: $GIT_USER_EMAIL"
}

# Run main function
main "$@"
