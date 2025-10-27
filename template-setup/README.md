# Development Environment Setup

This repository template provides a comprehensive, cross-platform development environment setup that can be quickly configured on Windows, macOS, and Linux systems.

## 🚀 Quick Start

### Prerequisites

- **Windows**: PowerShell 5.1+ or PowerShell Core 6+
- **macOS**: macOS 10.15+ with Xcode Command Line Tools
- **Linux**: Ubuntu 20.04+, CentOS 8+, or Fedora 32+

### One-Command Setup

Choose the appropriate command for your platform:

#### Windows (PowerShell)
```powershell
# Run as Administrator for best results
.\setup-windows.ps1 -GitUserName "Your Name" -GitUserEmail "your.email@example.com"
```

#### macOS (Terminal)
```bash
chmod +x setup-macos.sh
./setup-macos.sh --git-name "Your Name" --git-email "your.email@example.com"
```

#### Linux (Terminal)
```bash
chmod +x setup-linux.sh
./setup-linux.sh --git-name "Your Name" --git-email "your.email@example.com"
```

#### Cross-Platform (Python)
```bash
python3 setup.py
```

## 🛠️ Installed Tools

### Core Development Tools
- **Git** - Version control with team-standard configuration
- **Visual Studio Code** - IDE with recommended extensions
- **Docker Desktop** - Containerization platform
- **Playwright** - End-to-end testing framework

### Package Managers
- **Node.js + npm** - JavaScript runtime and package manager
- **Python + pip** - Python runtime and package manager
- **Yarn & pnpm** - Alternative Node.js package managers

### Code Quality Tools
- **ESLint + Prettier** - JavaScript linting and formatting
- **Pylint + Black** - Python linting and formatting

### Additional Tools
- **Postman** - API development and testing
- **GitHub Actions** - CI/CD workflow templates

## 📋 Platform-Specific Instructions

### Windows Setup

The Windows setup script uses PowerShell and supports both Chocolatey and Winget package managers.

**Features:**
- Automatic package manager installation (Chocolatey/Winget)
- PowerShell execution policy handling
- Administrator privilege detection
- Comprehensive error handling

**Options:**
```powershell
.\setup-windows.ps1 [OPTIONS]

Options:
  -Force                    Force reinstallation of existing tools
  -SkipDocker              Skip Docker Desktop installation
  -SkipVSCode              Skip Visual Studio Code installation
  -GitUserName "Name"      Set Git user name
  -GitUserEmail "Email"    Set Git user email
```

### macOS Setup

The macOS setup script uses Homebrew for package management and requires Xcode Command Line Tools.

**Features:**
- Automatic Homebrew installation
- Xcode Command Line Tools detection
- Apple Silicon (M1/M2) support
- Comprehensive tool configuration

**Options:**
```bash
./setup-macos.sh [OPTIONS]

Options:
  --git-name NAME          Set Git user name (default: Developer)
  --git-email EMAIL        Set Git user email (default: developer@example.com)
  --skip-docker            Skip Docker installation
  --skip-vscode            Skip Visual Studio Code installation
  --help                   Show help message
```

### Linux Setup

The Linux setup script supports multiple distributions and package managers.

**Supported Distributions:**
- Ubuntu/Debian (apt)
- CentOS/RHEL (yum)
- Fedora (dnf)
- Snap packages

**Features:**
- Automatic distribution detection
- Multi-package manager support
- Docker group configuration
- Comprehensive tool installation

**Options:**
```bash
./setup-linux.sh [OPTIONS]

Options:
  --git-name NAME          Set Git user name (default: Developer)
  --git-email EMAIL        Set Git user email (default: developer@example.com)
  --skip-docker            Skip Docker installation
  --skip-vscode            Skip Visual Studio Code installation
  --help                   Show help message
```

## ⚙️ Configuration

### Git Configuration

All scripts configure Git with the following settings:
- Default branch: `main`
- Pull strategy: `rebase false`
- Line ending handling (platform-specific)
- User name and email (configurable)

### VS Code Configuration

The setup includes:
- **Extensions**: Python, TypeScript, Prettier, ESLint, Playwright, Docker, and more
- **Settings**: Format on save, auto-save, consistent formatting
- **Workspace**: Optimized for full-stack development

### Docker Configuration

- Docker Desktop installation
- Docker group membership (Linux)
- Compose V2 enabled
- Kubernetes disabled by default

## 🔧 Customization

### Configuration File

Edit `config/setup-config.json` to customize:
- Tool versions
- VS Code extensions
- Git configuration
- Package manager preferences

### Adding New Tools

To add new tools to the setup:

1. **Update configuration** in `config/setup-config.json`
2. **Add installation functions** to platform-specific scripts
3. **Update documentation** in this README

### Platform-Specific Modifications

Each platform script can be customized:
- `setup-windows.ps1` - Windows-specific installations
- `setup-macos.sh` - macOS-specific installations  
- `setup-linux.sh` - Linux-specific installations

## 🧪 Testing

### Verification Commands

After setup, verify installations:

```bash
# Check tool versions
git --version
node --version
python3 --version
docker --version
npx playwright --version

# Check VS Code extensions
code --list-extensions

# Check Git configuration
git config --list
```

### Test Scripts

Run the included test scripts:

```bash
# Test Node.js setup
npm test

# Test Python setup
python3 -m pytest

# Test Playwright
npx playwright test
```

## 🚨 Troubleshooting

### Common Issues

#### Windows
- **PowerShell Execution Policy**: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- **Administrator Rights**: Some installations require administrator privileges
- **Antivirus Software**: May block package manager installations

#### macOS
- **Xcode Command Line Tools**: Install via `xcode-select --install`
- **Homebrew Permissions**: Ensure proper ownership with `sudo chown -R $(whoami) /opt/homebrew`
- **Apple Silicon**: May need to restart terminal after Homebrew installation

#### Linux
- **Package Manager**: Ensure your distribution's package manager is available
- **Docker Permissions**: Log out and back in after Docker installation
- **Snap Packages**: Some tools may require snap installation

### Getting Help

1. **Check logs**: Scripts provide detailed output and error messages
2. **Verify prerequisites**: Ensure your system meets the requirements
3. **Manual installation**: Some tools may need manual installation
4. **Platform documentation**: Refer to tool-specific installation guides

## 📚 Additional Resources

### Documentation
- [Git Documentation](https://git-scm.com/doc)
- [VS Code Documentation](https://code.visualstudio.com/docs)
- [Docker Documentation](https://docs.docker.com/)
- [Playwright Documentation](https://playwright.dev/docs/intro)

### Best Practices
- [Git Best Practices](https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository)
- [VS Code Best Practices](https://code.visualstudio.com/docs/getstarted/tips-and-tricks)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on multiple platforms
5. Submit a pull request

## 🆘 Support

If you encounter issues or have questions:

1. Check the [troubleshooting section](#-troubleshooting)
2. Search existing [issues](https://github.com/your-org/repo-template/issues)
3. Create a new issue with:
   - Your operating system and version
   - The command you ran
   - Complete error output
   - Steps to reproduce

---

**Happy coding! 🎉**
