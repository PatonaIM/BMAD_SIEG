# Quick Start Guide

## 🚀 Setting Up Your Development Environment

### Option 1: Cross-Platform (Recommended)
```bash
python3 template-setup/setup.py
```

### Option 2: Platform-Specific
```bash
# macOS
./template-setup/setup-macos.sh

# Linux
./template-setup/setup-linux.sh

# Windows (PowerShell)
.\template-setup\setup-windows.ps1
```

### Option 3: Using npm scripts
```bash
# Cross-platform
npm run setup

# Platform-specific
npm run setup:macos
npm run setup:linux
npm run setup:windows
```

## 📋 What Gets Installed

- **Git** with team-standard configuration
- **Visual Studio Code** with 10 essential extensions
- **Docker Desktop** for containerization
- **Node.js/npm** with Yarn and pnpm
- **Python 3.11** with pip, virtualenv, pipenv
- **Playwright** for end-to-end testing
- **Postman** for API development
- **Code Quality Tools**: ESLint, Prettier, Pylint, Black

## ⚙️ Configuration

The setup scripts will prompt you for:
- Git user name and email
- Whether to skip Docker or VS Code installation

## 🔧 Customization

Edit `template-setup/config/setup-config.json` to customize:
- Tool versions
- VS Code extensions
- Git configuration
- Package manager preferences

## 📚 Full Documentation

See [template-setup/README.md](template-setup/README.md) for complete setup instructions and troubleshooting.

---

**Need help?** Check the troubleshooting section in the full README or create an issue in the repository.
