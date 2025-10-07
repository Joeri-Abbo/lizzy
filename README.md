# Groot CLI Tool

Groot is a command-line tool for managing AWS Systems Manager (SSM) patch operations across different environments and patch groups.

## Features

- Display Baby Groot ASCII art on startup
- `hello`: Print "Hello, World!"
- `scan`: Run patch scans for selected resource groups
- `install`: Run patch installations for selected resource groups  
- `patch`: Run complete patch workflow (scan → install → reboot → scan)
- `reboot`: Reboot instances in selected resource groups
- `compliance`: Check patch compliance status for machines in specific accounts
- Configuration management for different environments and patch groups

## Installation

### Prerequisites

- Python 3.6 or higher
- `pip` (Python package manager)

### Steps

1. Clone the repository (if not already cloned):

   ```bash
   git clone https://gitlab.com/your-username/groot-cli.git
   cd groot-cli
   ```

2. Install the CLI tool:
   ```bash
   pip install -e .
   ```

### Alternative Installation (Directly from GitLab)

```bash
pip install git+https://gitlab.com/your-username/groot-cli.git
```

## Usage

Run the following commands after installation:

- Display help:

  ```bash
  groot --help
  ```

- Print "Hello, World!":

  ```bash
  groot hello
  ```

- Run patch scan for a resource group:

  ```bash
  groot scan
  ```

- Run patch installation for a resource group:

  ```bash
  groot install
  ```

- Run complete patch workflow:

  ```bash
  groot patch
  ```

- Reboot instances in a resource group:

  ```bash
  groot reboot
  ```

- Check patch compliance status:

  ```bash
  groot compliance
  ```

- Check patch compliance with detailed information:

  ```bash
  groot compliance --detailed
  ```

## Compliance Command

The `compliance` command allows you to check the patch compliance status of machines in your AWS accounts. It provides:

- **Overview**: Shows compliance status for all instances across patch groups
- **Instance Details**: Displays individual instance compliance with platform information
- **Summary Statistics**: Provides compliance percentages and counts
- **Detailed Mode**: Shows specific missing patches when using `--detailed` flag

Example output:

```text
🔍 Checking patch compliance for environment 'Production', resource group 'Prod-AZ1'
================================================================================

📋 Patch Group: az1-windows
----------------------------------------
Found 3 instances in patch group 'az1-windows'
  ✅ web-server-01 (i-1234567890abcdef0) - Windows
     Status: COMPLIANT | Compliant: 15 | Non-Compliant: 0
  ❌ app-server-01 (i-0987654321fedcba0) - Windows  
     Status: MEDIUM | Compliant: 12 | Non-Compliant: 3
  ✅ db-server-01 (i-abcdef1234567890) - Windows
     Status: COMPLIANT | Compliant: 18 | Non-Compliant: 0

  📊 Patch Group 'az1-windows' Summary:
     ✅ Compliant: 2
     ❌ Non-Compliant: 1
     ❓ Unknown/No Data: 0

🎯 Overall Compliance Summary for 'Prod-AZ1':
==================================================
✅ Total Compliant Instances: 2
❌ Total Non-Compliant Instances: 1  
❓ Total Unknown/No Data: 0
📈 Compliance Rate: 66.7%
⚠️  Most instances are compliant, but some need attention.
```

## Configuration

## License

This project is licensed under the MIT License.
