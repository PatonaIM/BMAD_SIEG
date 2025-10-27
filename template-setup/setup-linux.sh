#!/bin/bash
# Linux Development Environment Setup Script
# Supports Ubuntu/Debian, CentOS/RHEL, and Fedora

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
DISTRO=""
PACKAGE_MANAGER=""

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

# Detect Linux distribution
detect_distro() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        DISTRO=$ID
        log_info "Detected distribution: $PRETTY_NAME"
    else
        log_error "Cannot detect Linux distribution"
        exit 1
    fi
}

# Detect package manager
detect_package_manager() {
    if command_exists apt; then
        PACKAGE_MANAGER="apt"
    elif command_exists yum; then
        PACKAGE_MANAGER="yum"
    elif command_exists dnf; then
        PACKAGE_MANAGER="dnf"
    elif command_exists snap; then
        PACKAGE_MANAGER="snap"
    else
        log_error "No supported package manager found (apt, yum, dnf, snap)"
        exit 1
    fi
    log_info "Using package manager: $PACKAGE_MANAGER"
}

# Update package lists
update_packages() {
    log_info "Updating package lists..."
    case $PACKAGE_MANAGER in
        apt)
            sudo apt update
            ;;
        yum)
            sudo yum update -y
            ;;
        dnf)
            sudo dnf update -y
            ;;
    esac
}

# Install Git
install_git() {
    log_info "Installing Git..."
    case $PACKAGE_MANAGER in
        apt)
            sudo apt install -y git
            ;;
        yum)
            sudo yum install -y git
            ;;
        dnf)
            sudo dnf install -y git
            ;;
        snap)
            sudo snap install git --classic
            ;;
    esac
    
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
    
    case $PACKAGE_MANAGER in
        apt)
            # Add Microsoft repository
            wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
            sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
            sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
            sudo apt update
            sudo apt install -y code
            ;;
        snap)
            sudo snap install --classic code
            ;;
        yum|dnf)
            # For RHEL/CentOS/Fedora, we'll use snap or manual installation
            if command_exists snap; then
                sudo snap install --classic code
            else
                log_warning "VS Code installation via snap not available. Please install manually from https://code.visualstudio.com/"
                return
            fi
            ;;
    esac
    
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

# Install Docker
install_docker() {
    if [[ "$SKIP_DOCKER" == true ]]; then
        log_info "Skipping Docker installation"
        return
    fi
    
    log_info "Installing Docker..."
    
    case $PACKAGE_MANAGER in
        apt)
            # Install Docker for Ubuntu/Debian
            sudo apt update
            sudo apt install -y ca-certificates curl gnupg lsb-release
            sudo mkdir -p /etc/apt/keyrings
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            sudo apt update
            sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            ;;
        yum)
            sudo yum install -y docker
            ;;
        dnf)
            sudo dnf install -y docker
            ;;
        snap)
            sudo snap install docker
            ;;
    esac
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    log_success "Docker installed successfully"
    log_warning "Please log out and log back in for Docker group changes to take effect"
}

# Install Node.js
install_nodejs() {
    log_info "Installing Node.js..."
    
    case $PACKAGE_MANAGER in
        apt)
            # Install Node.js 18.x for Ubuntu/Debian
            curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
            sudo apt install -y nodejs
            ;;
        yum)
            # Install Node.js 18.x for CentOS/RHEL
            curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
            sudo yum install -y nodejs
            ;;
        dnf)
            # Install Node.js 18.x for Fedora
            curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
            sudo dnf install -y nodejs
            ;;
        snap)
            sudo snap install node --classic
            ;;
    esac
    
    # Install global packages
    log_info "Installing global Node.js packages..."
    npm install -g yarn pnpm @playwright/test
    
    log_success "Node.js installed successfully"
}

# Install Python
install_python() {
    log_info "Installing Python..."
    
    case $PACKAGE_MANAGER in
        apt)
            sudo apt install -y python3.11 python3.11-pip python3.11-venv
            # Create symlinks for python and pip
            sudo ln -sf /usr/bin/python3.11 /usr/bin/python
            sudo ln -sf /usr/bin/python3.11 /usr/bin/python3
            ;;
        yum)
            sudo yum install -y python3.11 python3.11-pip
            ;;
        dnf)
            sudo dnf install -y python3.11 python3.11-pip
            ;;
        snap)
            sudo snap install python311 --classic
            ;;
    esac
    
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
    
    case $PACKAGE_MANAGER in
        snap)
            sudo snap install postman
            ;;
        *)
            # Download and install Postman manually
            log_info "Downloading Postman..."
            wget https://dl.pstmn.io/download/latest/linux64 -O postman.tar.gz
            sudo tar -xzf postman.tar.gz -C /opt
            sudo ln -sf /opt/Postman/Postman /usr/local/bin/postman
            
            # Create desktop file
            cat > ~/.local/share/applications/postman.desktop << EOF
[Desktop Entry]
Name=Postman
Comment=API Development Environment
Exec=/opt/Postman/Postman
Icon=/opt/Postman/app/resources/app/assets/icon.png
Terminal=false
Type=Application
Categories=Development;
EOF
            ;;
    esac
    
    log_success "Postman installed successfully"
}

# Configure VS Code settings
configure_vscode() {
    if [[ "$SKIP_VSCODE" == true ]]; then
        return
    fi
    
    log_info "Configuring VS Code settings..."
    local vscode_settings_dir="$HOME/.config/Code/User"
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
    "editor.detectIndentation": false
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
    log_info "🚀 Starting Linux Development Environment Setup"
    echo "=================================================="
    
    # Detect system
    detect_distro
    detect_package_manager
    
    # Update packages
    update_packages
    
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
    log_info "  1. Log out and log back in for Docker group changes to take effect"
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
