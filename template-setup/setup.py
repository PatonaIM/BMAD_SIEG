#!/usr/bin/env python3
"""
Cross-Platform Development Environment Setup Script
Supports Windows, macOS, and Linux platforms
"""

import os
import sys
import platform
import subprocess
import json
from pathlib import Path

class DevEnvironmentSetup:
    def __init__(self):
        self.platform = platform.system().lower()
        self.script_dir = Path(__file__).parent
        self.config = self.load_config()
        
    def load_config(self):
        """Load configuration from config.json"""
        config_path = self.script_dir / "config" / "setup-config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        return self.get_default_config()
    
    def get_default_config(self):
        """Default configuration for development tools"""
        return {
            "tools": {
                "git": {
                    "name": "Git",
                    "required": True,
                    "config": {
                        "user.name": "Developer",
                        "user.email": "developer@example.com",
                        "init.defaultBranch": "main",
                        "pull.rebase": "false"
                    }
                },
                "vscode": {
                    "name": "Visual Studio Code",
                    "required": True,
                    "extensions": [
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
                    ]
                },
                "docker": {
                    "name": "Docker Desktop",
                    "required": True
                },
                "nodejs": {
                    "name": "Node.js",
                    "required": True,
                    "version": "18.x"
                },
                "python": {
                    "name": "Python",
                    "required": True,
                    "version": "3.11"
                },
                "playwright": {
                    "name": "Playwright",
                    "required": True
                },
                "postman": {
                    "name": "Postman",
                    "required": False
                }
            }
        }
    
    def detect_platform(self):
        """Detect the current platform and return appropriate handler"""
        if self.platform == "windows":
            return WindowsSetup(self.config)
        elif self.platform == "darwin":
            return MacOSSetup(self.config)
        elif self.platform == "linux":
            return LinuxSetup(self.config)
        else:
            raise OSError(f"Unsupported platform: {self.platform}")
    
    def run(self):
        """Main entry point for the setup script"""
        print("🚀 Starting Development Environment Setup")
        print(f"📱 Detected platform: {self.platform.title()}")
        print("=" * 50)
        
        try:
            setup_handler = self.detect_platform()
            setup_handler.run()
            print("\n✅ Setup completed successfully!")
        except Exception as e:
            print(f"\n❌ Setup failed: {str(e)}")
            sys.exit(1)

class BaseSetup:
    def __init__(self, config):
        self.config = config
        self.tools = config["tools"]
    
    def log(self, message, level="INFO"):
        """Log messages with consistent formatting"""
        levels = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌"
        }
        print(f"{levels.get(level, 'ℹ️')} {message}")
    
    def check_command(self, command):
        """Check if a command exists in PATH"""
        try:
            subprocess.run([command, "--version"], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def run_command(self, command, check=True):
        """Run a command and return the result"""
        try:
            result = subprocess.run(command, shell=True, 
                                  capture_output=True, text=True, check=check)
            return result
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {command}", "ERROR")
            self.log(f"Error: {e.stderr}", "ERROR")
            raise

class WindowsSetup(BaseSetup):
    def __init__(self, config):
        super().__init__(config)
        self.package_managers = self.detect_package_managers()
    
    def detect_package_managers(self):
        """Detect available package managers on Windows"""
        managers = {}
        if self.check_command("choco"):
            managers["chocolatey"] = True
        if self.check_command("winget"):
            managers["winget"] = True
        return managers
    
    def install_package_manager(self):
        """Install a package manager if none are available"""
        if not self.package_managers:
            self.log("Installing Chocolatey package manager...", "INFO")
            # Install Chocolatey
            install_cmd = (
                "Set-ExecutionPolicy Bypass -Scope Process -Force; "
                "[System.Net.ServicePointManager]::SecurityProtocol = "
                "[System.Net.ServicePointManager]::SecurityProtocol -bor 3072; "
                "iex ((New-Object System.Net.WebClient).DownloadString("
                "'https://community.chocolatey.org/install.ps1'))"
            )
            self.run_command(f'powershell -Command "{install_cmd}"')
            self.package_managers["chocolatey"] = True
    
    def install_git(self):
        """Install and configure Git"""
        self.log("Installing Git...", "INFO")
        if "chocolatey" in self.package_managers:
            self.run_command("choco install git -y")
        elif "winget" in self.package_managers:
            self.run_command("winget install --id Git.Git -e --source winget")
        
        # Configure Git
        git_config = self.tools["git"]["config"]
        for key, value in git_config.items():
            self.run_command(f'git config --global {key} "{value}"')
        self.log("Git configured successfully", "SUCCESS")
    
    def install_vscode(self):
        """Install Visual Studio Code and extensions"""
        self.log("Installing Visual Studio Code...", "INFO")
        if "chocolatey" in self.package_managers:
            self.run_command("choco install vscode -y")
        elif "winget" in self.package_managers:
            self.run_command("winget install --id Microsoft.VisualStudioCode -e --source winget")
        
        # Install extensions
        extensions = self.tools["vscode"]["extensions"]
        for extension in extensions:
            self.log(f"Installing extension: {extension}", "INFO")
            self.run_command(f"code --install-extension {extension}")
    
    def install_docker(self):
        """Install Docker Desktop"""
        self.log("Installing Docker Desktop...", "INFO")
        if "chocolatey" in self.package_managers:
            self.run_command("choco install docker-desktop -y")
        elif "winget" in self.package_managers:
            self.run_command("winget install --id Docker.DockerDesktop -e --source winget")
    
    def install_nodejs(self):
        """Install Node.js"""
        self.log("Installing Node.js...", "INFO")
        if "chocolatey" in self.package_managers:
            self.run_command("choco install nodejs -y")
        elif "winget" in self.package_managers:
            self.run_command("winget install --id OpenJS.NodeJS -e --source winget")
    
    def install_python(self):
        """Install Python"""
        self.log("Installing Python...", "INFO")
        if "chocolatey" in self.package_managers:
            self.run_command("choco install python -y")
        elif "winget" in self.package_managers:
            self.run_command("winget install --id Python.Python.3.11 -e --source winget")
    
    def install_playwright(self):
        """Install Playwright"""
        self.log("Installing Playwright...", "INFO")
        self.run_command("npm install -g @playwright/test")
        self.run_command("npx playwright install")
    
    def install_postman(self):
        """Install Postman"""
        self.log("Installing Postman...", "INFO")
        if "chocolatey" in self.package_managers:
            self.run_command("choco install postman -y")
        elif "winget" in self.package_managers:
            self.run_command("winget install --id Postman.Postman -e --source winget")
    
    def run(self):
        """Run Windows-specific setup"""
        self.log("Starting Windows setup...", "INFO")
        
        # Install package manager if needed
        self.install_package_manager()
        
        # Install tools
        self.install_git()
        self.install_vscode()
        self.install_docker()
        self.install_nodejs()
        self.install_python()
        self.install_playwright()
        self.install_postman()
        
        self.log("Windows setup completed!", "SUCCESS")

class MacOSSetup(BaseSetup):
    def __init__(self, config):
        super().__init__(config)
        self.has_homebrew = self.check_command("brew")
    
    def install_homebrew(self):
        """Install Homebrew if not present"""
        if not self.has_homebrew:
            self.log("Installing Homebrew...", "INFO")
            install_cmd = (
                '/bin/bash -c "$(curl -fsSL '
                'https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            )
            self.run_command(install_cmd)
            self.has_homebrew = True
    
    def install_git(self):
        """Install and configure Git"""
        self.log("Installing Git...", "INFO")
        self.run_command("brew install git")
        
        # Configure Git
        git_config = self.tools["git"]["config"]
        for key, value in git_config.items():
            self.run_command(f'git config --global {key} "{value}"')
        self.log("Git configured successfully", "SUCCESS")
    
    def install_vscode(self):
        """Install Visual Studio Code and extensions"""
        self.log("Installing Visual Studio Code...", "INFO")
        self.run_command("brew install --cask visual-studio-code")
        
        # Install extensions
        extensions = self.tools["vscode"]["extensions"]
        for extension in extensions:
            self.log(f"Installing extension: {extension}", "INFO")
            self.run_command(f"code --install-extension {extension}")
    
    def install_docker(self):
        """Install Docker Desktop"""
        self.log("Installing Docker Desktop...", "INFO")
        self.run_command("brew install --cask docker")
    
    def install_nodejs(self):
        """Install Node.js"""
        self.log("Installing Node.js...", "INFO")
        self.run_command("brew install node")
    
    def install_python(self):
        """Install Python"""
        self.log("Installing Python...", "INFO")
        self.run_command("brew install python@3.11")
    
    def install_playwright(self):
        """Install Playwright"""
        self.log("Installing Playwright...", "INFO")
        self.run_command("npm install -g @playwright/test")
        self.run_command("npx playwright install")
    
    def install_postman(self):
        """Install Postman"""
        self.log("Installing Postman...", "INFO")
        self.run_command("brew install --cask postman")
    
    def run(self):
        """Run macOS-specific setup"""
        self.log("Starting macOS setup...", "INFO")
        
        # Install Homebrew if needed
        self.install_homebrew()
        
        # Install tools
        self.install_git()
        self.install_vscode()
        self.install_docker()
        self.install_nodejs()
        self.install_python()
        self.install_playwright()
        self.install_postman()
        
        self.log("macOS setup completed!", "SUCCESS")

class LinuxSetup(BaseSetup):
    def __init__(self, config):
        super().__init__(config)
        self.distro = self.detect_distro()
        self.package_manager = self.detect_package_manager()
    
    def detect_distro(self):
        """Detect Linux distribution"""
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read()
                if 'ubuntu' in content.lower() or 'debian' in content.lower():
                    return 'debian'
                elif 'centos' in content.lower() or 'rhel' in content.lower():
                    return 'rhel'
                elif 'fedora' in content.lower():
                    return 'fedora'
                else:
                    return 'unknown'
        except FileNotFoundError:
            return 'unknown'
    
    def detect_package_manager(self):
        """Detect available package manager"""
        if self.check_command("apt"):
            return "apt"
        elif self.check_command("yum"):
            return "yum"
        elif self.check_command("dnf"):
            return "dnf"
        elif self.check_command("snap"):
            return "snap"
        else:
            return "unknown"
    
    def install_git(self):
        """Install and configure Git"""
        self.log("Installing Git...", "INFO")
        if self.package_manager == "apt":
            self.run_command("sudo apt update && sudo apt install -y git")
        elif self.package_manager == "yum":
            self.run_command("sudo yum install -y git")
        elif self.package_manager == "dnf":
            self.run_command("sudo dnf install -y git")
        
        # Configure Git
        git_config = self.tools["git"]["config"]
        for key, value in git_config.items():
            self.run_command(f'git config --global {key} "{value}"')
        self.log("Git configured successfully", "SUCCESS")
    
    def install_vscode(self):
        """Install Visual Studio Code and extensions"""
        self.log("Installing Visual Studio Code...", "INFO")
        if self.package_manager == "apt":
            self.run_command("wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg")
            self.run_command("sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/")
            self.run_command("sudo sh -c 'echo \"deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main\" > /etc/apt/sources.list.d/vscode.list'")
            self.run_command("sudo apt update && sudo apt install -y code")
        elif self.package_manager == "snap":
            self.run_command("sudo snap install --classic code")
        
        # Install extensions
        extensions = self.tools["vscode"]["extensions"]
        for extension in extensions:
            self.log(f"Installing extension: {extension}", "INFO")
            self.run_command(f"code --install-extension {extension}")
    
    def install_docker(self):
        """Install Docker"""
        self.log("Installing Docker...", "INFO")
        if self.package_manager == "apt":
            self.run_command("sudo apt update")
            self.run_command("sudo apt install -y ca-certificates curl gnupg lsb-release")
            self.run_command("sudo mkdir -p /etc/apt/keyrings")
            self.run_command("curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg")
            self.run_command('echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null')
            self.run_command("sudo apt update && sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin")
        elif self.package_manager == "yum":
            self.run_command("sudo yum install -y docker")
        elif self.package_manager == "dnf":
            self.run_command("sudo dnf install -y docker")
    
    def install_nodejs(self):
        """Install Node.js"""
        self.log("Installing Node.js...", "INFO")
        if self.package_manager == "apt":
            self.run_command("curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -")
            self.run_command("sudo apt install -y nodejs")
        elif self.package_manager == "yum":
            self.run_command("curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -")
            self.run_command("sudo yum install -y nodejs")
        elif self.package_manager == "dnf":
            self.run_command("curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -")
            self.run_command("sudo dnf install -y nodejs")
    
    def install_python(self):
        """Install Python"""
        self.log("Installing Python...", "INFO")
        if self.package_manager == "apt":
            self.run_command("sudo apt install -y python3.11 python3.11-pip")
        elif self.package_manager == "yum":
            self.run_command("sudo yum install -y python3.11 python3.11-pip")
        elif self.package_manager == "dnf":
            self.run_command("sudo dnf install -y python3.11 python3.11-pip")
    
    def install_playwright(self):
        """Install Playwright"""
        self.log("Installing Playwright...", "INFO")
        self.run_command("npm install -g @playwright/test")
        self.run_command("npx playwright install")
    
    def install_postman(self):
        """Install Postman"""
        self.log("Installing Postman...", "INFO")
        if self.package_manager == "snap":
            self.run_command("sudo snap install postman")
        else:
            # Download and install Postman manually
            self.run_command("wget https://dl.pstmn.io/download/latest/linux64 -O postman.tar.gz")
            self.run_command("sudo tar -xzf postman.tar.gz -C /opt")
            self.run_command("sudo ln -s /opt/Postman/Postman /usr/local/bin/postman")
    
    def run(self):
        """Run Linux-specific setup"""
        self.log("Starting Linux setup...", "INFO")
        self.log(f"Detected distribution: {self.distro}", "INFO")
        self.log(f"Using package manager: {self.package_manager}", "INFO")
        
        # Install tools
        self.install_git()
        self.install_vscode()
        self.install_docker()
        self.install_nodejs()
        self.install_python()
        self.install_playwright()
        self.install_postman()
        
        self.log("Linux setup completed!", "SUCCESS")

if __name__ == "__main__":
    setup = DevEnvironmentSetup()
    setup.run()
