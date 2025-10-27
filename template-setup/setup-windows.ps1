# Windows Development Environment Setup Script
# Requires PowerShell 5.1+ or PowerShell Core 6+

param(
    [switch]$Force,
    [switch]$SkipDocker,
    [switch]$SkipVSCode,
    [string]$GitUserName = "Developer",
    [string]$GitUserEmail = "developer@example.com"
)

# Set execution policy for current session
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# Color functions for better output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    } else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Success { Write-ColorOutput Green $args }
function Write-Info { Write-ColorOutput Cyan $args }
function Write-Warning { Write-ColorOutput Yellow $args }
function Write-Error { Write-ColorOutput Red $args }

# Check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Install Chocolatey if not present
function Install-Chocolatey {
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        Write-Info "✅ Chocolatey is already installed"
        return
    }
    
    Write-Info "📦 Installing Chocolatey package manager..."
    try {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        Write-Success "✅ Chocolatey installed successfully"
    } catch {
        Write-Error "❌ Failed to install Chocolatey: $($_.Exception.Message)"
        exit 1
    }
}

# Install Winget if not present
function Install-Winget {
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Info "✅ Winget is already installed"
        return
    }
    
    Write-Info "📦 Installing Winget package manager..."
    try {
        # Download and install App Installer (which includes winget)
        $url = "https://aka.ms/getwinget"
        $output = "$env:TEMP\Microsoft.DesktopAppInstaller.msixbundle"
        Invoke-WebRequest -Uri $url -OutFile $output
        Add-AppxPackage -Path $output
        Write-Success "✅ Winget installed successfully"
    } catch {
        Write-Warning "⚠️ Failed to install Winget: $($_.Exception.Message)"
        Write-Info "Continuing with Chocolatey only..."
    }
}

# Install Git
function Install-Git {
    Write-Info "🔧 Installing Git..."
    try {
        if (Get-Command choco -ErrorAction SilentlyContinue) {
            choco install git -y
        } elseif (Get-Command winget -ErrorAction SilentlyContinue) {
            winget install --id Git.Git -e --source winget
        } else {
            Write-Error "❌ No package manager available for Git installation"
            exit 1
        }
        
        # Configure Git
        Write-Info "⚙️ Configuring Git..."
        git config --global user.name "$GitUserName"
        git config --global user.email "$GitUserEmail"
        git config --global init.defaultBranch main
        git config --global pull.rebase false
        git config --global core.autocrlf true
        git config --global core.safecrlf true
        
        Write-Success "✅ Git installed and configured successfully"
    } catch {
        Write-Error "❌ Failed to install Git: $($_.Exception.Message)"
        exit 1
    }
}

# Install Visual Studio Code
function Install-VSCode {
    if ($SkipVSCode) {
        Write-Info "⏭️ Skipping Visual Studio Code installation"
        return
    }
    
    Write-Info "🔧 Installing Visual Studio Code..."
    try {
        if (Get-Command choco -ErrorAction SilentlyContinue) {
            choco install vscode -y
        } elseif (Get-Command winget -ErrorAction SilentlyContinue) {
            winget install --id Microsoft.VisualStudioCode -e --source winget
        } else {
            Write-Error "❌ No package manager available for VSCode installation"
            exit 1
        }
        
        # Install extensions
        Write-Info "📦 Installing VSCode extensions..."
        $extensions = @(
            "ms-python.python",
            "ms-vscode.vscode-typescript-next",
            "esbenp.prettier-vscode",
            "dbaeumer.vscode-eslint",
            "ms-playwright.playwright",
            "ms-azuretools.vscode-docker",
            "bradlc.vscode-tailwindcss",
            "formulahendry.auto-rename-tag",
            "christian-kohler.path-intellisense",
            "mhutchie.git-graph"
        )
        
        foreach ($extension in $extensions) {
            Write-Info "Installing extension: $extension"
            code --install-extension $extension --force
        }
        
        Write-Success "✅ Visual Studio Code installed with extensions"
    } catch {
        Write-Error "❌ Failed to install Visual Studio Code: $($_.Exception.Message)"
        exit 1
    }
}

# Install Docker Desktop
function Install-Docker {
    if ($SkipDocker) {
        Write-Info "⏭️ Skipping Docker installation"
        return
    }
    
    Write-Info "🔧 Installing Docker Desktop..."
    try {
        if (Get-Command choco -ErrorAction SilentlyContinue) {
            choco install docker-desktop -y
        } elseif (Get-Command winget -ErrorAction SilentlyContinue) {
            winget install --id Docker.DockerDesktop -e --source winget
        } else {
            Write-Error "❌ No package manager available for Docker installation"
            exit 1
        }
        
        Write-Success "✅ Docker Desktop installed successfully"
        Write-Warning "⚠️ Please restart your computer and start Docker Desktop manually"
    } catch {
        Write-Error "❌ Failed to install Docker Desktop: $($_.Exception.Message)"
        exit 1
    }
}

# Install Node.js
function Install-NodeJS {
    Write-Info "🔧 Installing Node.js..."
    try {
        if (Get-Command choco -ErrorAction SilentlyContinue) {
            choco install nodejs -y
        } elseif (Get-Command winget -ErrorAction SilentlyContinue) {
            winget install --id OpenJS.NodeJS -e --source winget
        } else {
            Write-Error "❌ No package manager available for Node.js installation"
            exit 1
        }
        
        # Install global packages
        Write-Info "📦 Installing global Node.js packages..."
        npm install -g yarn pnpm @playwright/test
        
        Write-Success "✅ Node.js installed successfully"
    } catch {
        Write-Error "❌ Failed to install Node.js: $($_.Exception.Message)"
        exit 1
    }
}

# Install Python
function Install-Python {
    Write-Info "🔧 Installing Python..."
    try {
        if (Get-Command choco -ErrorAction SilentlyContinue) {
            choco install python -y
        } elseif (Get-Command winget -ErrorAction SilentlyContinue) {
            winget install --id Python.Python.3.11 -e --source winget
        } else {
            Write-Error "❌ No package manager available for Python installation"
            exit 1
        }
        
        # Install global packages
        Write-Info "📦 Installing global Python packages..."
        pip install --upgrade pip
        pip install virtualenv pipenv black pylint
        
        Write-Success "✅ Python installed successfully"
    } catch {
        Write-Error "❌ Failed to install Python: $($_.Exception.Message)"
        exit 1
    }
}

# Install Playwright browsers
function Install-Playwright {
    Write-Info "🔧 Installing Playwright browsers..."
    try {
        npx playwright install
        Write-Success "✅ Playwright browsers installed successfully"
    } catch {
        Write-Error "❌ Failed to install Playwright browsers: $($_.Exception.Message)"
        exit 1
    }
}

# Install Postman
function Install-Postman {
    Write-Info "🔧 Installing Postman..."
    try {
        if (Get-Command choco -ErrorAction SilentlyContinue) {
            choco install postman -y
        } elseif (Get-Command winget -ErrorAction SilentlyContinue) {
            winget install --id Postman.Postman -e --source winget
        } else {
            Write-Error "❌ No package manager available for Postman installation"
            exit 1
        }
        
        Write-Success "✅ Postman installed successfully"
    } catch {
        Write-Error "❌ Failed to install Postman: $($_.Exception.Message)"
        exit 1
    }
}

# Create VS Code settings
function Set-VSCodeSettings {
    Write-Info "⚙️ Configuring VS Code settings..."
    $vscodeSettingsPath = "$env:APPDATA\Code\User\settings.json"
    $settings = @{
        "editor.formatOnSave" = $true
        "editor.codeActionsOnSave" = @{
            "source.fixAll.eslint" = $true
        }
        "editor.defaultFormatter" = "esbenp.prettier-vscode"
        "files.autoSave" = "afterDelay"
        "files.autoSaveDelay" = 1000
        "editor.tabSize" = 2
        "editor.insertSpaces" = $true
        "editor.detectIndentation" = $false
    }
    
    $settings | ConvertTo-Json -Depth 3 | Set-Content $vscodeSettingsPath
    Write-Success "✅ VS Code settings configured"
}

# Main execution
function Main {
    Write-Info "🚀 Starting Windows Development Environment Setup"
    Write-Info "=" * 50
    
    # Check if running as administrator
    if (-not (Test-Administrator)) {
        Write-Warning "⚠️ This script should be run as Administrator for best results"
        Write-Info "Some installations may require elevated privileges"
    }
    
    try {
        # Install package managers
        Install-Chocolatey
        Install-Winget
        
        # Install development tools
        Install-Git
        Install-VSCode
        Install-Docker
        Install-NodeJS
        Install-Python
        Install-Playwright
        Install-Postman
        
        # Configure VS Code
        Set-VSCodeSettings
        
        Write-Success "🎉 Development environment setup completed successfully!"
        Write-Info "📋 Next steps:"
        Write-Info "  1. Restart your computer if Docker was installed"
        Write-Info "  2. Start Docker Desktop"
        Write-Info "  3. Open Visual Studio Code and verify extensions are installed"
        Write-Info "  4. Run 'git --version' to verify Git installation"
        Write-Info "  5. Run 'node --version' to verify Node.js installation"
        Write-Info "  6. Run 'python --version' to verify Python installation"
        
    } catch {
        Write-Error "❌ Setup failed: $($_.Exception.Message)"
        exit 1
    }
}

# Run main function
Main
