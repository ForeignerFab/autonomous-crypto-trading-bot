
# WSL Setup Guide for OKX Trading Bot

This guide provides step-by-step instructions for installing and configuring Windows Subsystem for Linux (WSL) on Windows 10/11 for running your autonomous cryptocurrency trading bot 24/7.

## Prerequisites

- Windows 10 version 2004 (Build 19041) or later, OR Windows 11
- Administrator access to your Windows PC
- Hardware virtualization support enabled in BIOS/UEFI (Intel VT-x or AMD-V)
- Stable internet connection

## Step 1: Install WSL

### Easy Installation (Recommended)

1. **Open PowerShell as Administrator**
   - Press `Win + X` and select "Windows PowerShell (Admin)" or "Terminal (Admin)"
   - Alternatively, press `Win + R`, type `powershell`, then press `Ctrl + Shift + Enter`

2. **Install WSL with Ubuntu**
   ```powershell
   wsl --install
   ```
   This command will:
   - Enable required Windows features
   - Install the WSL2 kernel
   - Download and install Ubuntu (default distribution)
   - Set WSL2 as your default version

3. **Restart Your Computer**
   - Reboot when prompted
   - After restart, Ubuntu will complete its installation automatically

4. **Create Your Linux User Account**
   - Ubuntu will launch and prompt you to create a username and password
   - Choose a simple username (lowercase, no spaces)
   - Enter a secure password (you won't see characters as you type)

### Manual Installation (For Older Windows Versions)

If you're on Windows 10 version earlier than 2004:

1. **Enable WSL Feature**
   ```powershell
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   ```

2. **Enable Virtual Machine Platform**
   ```powershell
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   ```

3. **Restart Your Computer**

4. **Download and Install WSL2 Kernel Update**
   - Download from: https://aka.ms/wsl2kernel
   - Run the installer as administrator

5. **Set WSL2 as Default**
   ```powershell
   wsl --set-default-version 2
   ```

6. **Install Ubuntu**
   ```powershell
   wsl --install -d Ubuntu
   ```

## Step 2: Verify WSL Installation

1. **Check Installed Distributions**
   ```powershell
   wsl -l -v
   ```
   You should see Ubuntu listed with version 2.

2. **Launch Ubuntu**
   - Type "Ubuntu" in the Start menu and click it
   - Or run `wsl` in PowerShell/Command Prompt

## Step 3: Configure Ubuntu for Python Development

1. **Update Package Lists**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Essential Development Tools**
   ```bash
   sudo apt install -y python3 python3-pip python3-venv build-essential curl git wget unzip
   ```

3. **Install Additional Dependencies for Trading Bot**
   ```bash
   sudo apt install -y libssl-dev libffi-dev python3-dev
   ```

4. **Verify Python Installation**
   ```bash
   python3 --version
   pip3 --version
   ```

5. **Create Python Alias (Optional)**
   ```bash
   echo 'alias python=python3' >> ~/.bashrc
   echo 'alias pip=pip3' >> ~/.bashrc
   source ~/.bashrc
   ```

## Step 4: Configure WSL for 24/7 Operation

### Enable Systemd (For Service Management)

1. **Edit WSL Configuration**
   ```bash
   sudo nano /etc/wsl.conf
   ```

2. **Add the Following Content**
   ```ini
   [boot]
   systemd=true
   
   [network]
   generateHosts = false
   generateResolvConf = false
   ```

3. **Restart WSL**
   ```powershell
   # In Windows PowerShell
   wsl --shutdown
   wsl
   ```

### Configure Automatic Startup

1. **Create Startup Script**
   ```bash
   mkdir -p ~/scripts
   nano ~/scripts/startup.sh
   ```

2. **Add Startup Commands**
   ```bash
   #!/bin/bash
   # Trading bot startup script
   cd ~/okx_trading_bot
   source venv/bin/activate
   python main.py &
   ```

3. **Make Script Executable**
   ```bash
   chmod +x ~/scripts/startup.sh
   ```

## Step 5: Windows Integration Setup

### Configure Windows Terminal (Recommended)

1. **Install Windows Terminal**
   - Download from Microsoft Store
   - Or download from GitHub releases

2. **Set Ubuntu as Default Profile**
   - Open Windows Terminal
   - Press `Ctrl + ,` to open settings
   - Set Ubuntu as default profile

### File System Access

- **Access Windows files from WSL**: `/mnt/c/Users/YourUsername/`
- **Access WSL files from Windows**: `\\wsl$\Ubuntu\home\yourusername\`

## Step 6: Performance Optimization

### Allocate Resources to WSL

1. **Create WSL Configuration File**
   ```powershell
   # In Windows PowerShell, navigate to your user directory
   cd $env:USERPROFILE
   notepad .wslconfig
   ```

2. **Add Resource Limits**
   ```ini
   [wsl2]
   memory=4GB
   processors=2
   swap=2GB
   localhostForwarding=true
   ```

3. **Restart WSL**
   ```powershell
   wsl --shutdown
   ```

### Enable GPU Support (Optional)

For advanced machine learning features:
```bash
# Install NVIDIA drivers in WSL
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda
```

## Troubleshooting

### Common Issues and Solutions

**Error: "WSL 2 requires an update to its kernel component"**
- Download and install the WSL2 kernel update from Microsoft
- Restart your computer

**Error: "The requested operation could not be completed due to a virtual disk system limitation"**
- Enable virtualization in BIOS/UEFI settings
- Ensure Hyper-V is enabled in Windows Features

**Ubuntu doesn't start or crashes**
```powershell
# Reset Ubuntu installation
wsl --unregister Ubuntu
wsl --install -d Ubuntu
```

**Network connectivity issues**
```bash
# Reset network configuration
sudo rm /etc/resolv.conf
sudo bash -c 'echo "nameserver 8.8.8.8" > /etc/resolv.conf'
```

**High memory usage**
```powershell
# Compact WSL virtual disk
wsl --shutdown
diskpart
# In diskpart:
select vdisk file="C:\Users\%USERNAME%\AppData\Local\Packages\CanonicalGroupLimited.UbuntuonWindows_79rhkp1fndgsc\LocalState\ext4.vhdx"
compact vdisk
exit
```

### Performance Issues

**Slow file operations**
- Keep project files in WSL filesystem (`~/`) rather than Windows filesystem (`/mnt/c/`)
- Use WSL2 instead of WSL1

**High CPU usage**
- Limit WSL resources in `.wslconfig`
- Close unnecessary Windows applications

## Security Considerations

1. **Keep WSL Updated**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Configure Firewall**
   ```bash
   sudo ufw enable
   sudo ufw allow 22/tcp  # SSH if needed
   ```

3. **Secure SSH Access**
   ```bash
   # Generate SSH key for Git
   ssh-keygen -t ed25519 -C "your-email@example.com"
   ```

## Next Steps

After completing this WSL setup:

1. ✅ WSL2 with Ubuntu installed and configured
2. ✅ Python development environment ready
3. ✅ System optimized for 24/7 operation
4. ➡️ Continue to [Discord Integration Guide](discord_integration.md)
5. ➡️ Set up [OKX API Configuration](okx_api_config.md)

## Useful Commands Reference

```bash
# WSL Management (from Windows PowerShell)
wsl -l -v                    # List distributions and versions
wsl --shutdown              # Shutdown all WSL instances
wsl --terminate Ubuntu      # Terminate specific distribution
wsl --export Ubuntu backup.tar  # Export distribution
wsl --import Ubuntu C:\WSL backup.tar  # Import distribution

# Ubuntu Management
sudo systemctl status       # Check system status
htop                        # Monitor system resources
df -h                       # Check disk usage
free -h                     # Check memory usage
```

---

**[Screenshot: WSL installation success showing Ubuntu terminal with username@hostname prompt]**

**[Screenshot: Windows Terminal with Ubuntu profile configured and running]**

**[Screenshot: File Explorer showing \\wsl$\Ubuntu path with trading bot files]**
