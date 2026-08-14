#!/usr/bin/env bash
# ==============================================================================
# Bruschetta (Chromebook) Quickstart Setup Script
# Configures ~/.ssh/config and ~/.bashrc for seamless Cloudtop development
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "\033[1;36m============================================================\033[0m"
echo -e "\033[1;36m  🚀 Chromebook (Bruschetta) to Cloudtop Setup Wizard     \033[0m"
echo -e "\033[1;36m============================================================\033[0m"
echo ""

# 1. Detect / Prompt for LDAP
DEFAULT_LDAP="$USER"
read -r -p "Enter your Google LDAP username [$DEFAULT_LDAP]: " USER_LDAP
USER_LDAP="${USER_LDAP:-$DEFAULT_LDAP}"

# 2. Prompt for Cloudtop machine name
read -r -p "Enter your Cloudtop machine name (e.g. my-cloudtop): " CLOUDTOP_NAME
if [[ -z "$CLOUDTOP_NAME" ]]; then
  echo -e "\033[1;31mError: Cloudtop machine name cannot be empty.\033[0m"
  exit 1
fi
# Strip .c.googlers.com suffix if user typed full FQDN
CLOUDTOP_NAME="${CLOUDTOP_NAME%.c.googlers.com}"

echo ""
echo -e "Configuring for: \033[1;32m$USER_LDAP\033[0m @ \033[1;32m$CLOUDTOP_NAME.c.googlers.com\033[0m"
echo ""

# 3. Configure ~/.ssh/config
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"
SSH_CONFIG="$HOME/.ssh/config"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

if [[ -f "$SSH_CONFIG" ]]; then
  BACKUP_FILE="$HOME/.ssh/config.bak.$TIMESTAMP"
  echo "Backing up existing ~/.ssh/config to $BACKUP_FILE..."
  cp "$SSH_CONFIG" "$BACKUP_FILE"
fi

echo "Generating configured SSH host blocks..."
TEMP_SSH="$(mktemp)"
sed \
  -e "s/<CLOUDTOP_NAME>/$CLOUDTOP_NAME/g" \
  -e "s/<LDAP_USERNAME>/$USER_LDAP/g" \
  "$SCRIPT_DIR/chromebook/ssh_config.template" > "$TEMP_SSH"

# Check if block already exists
if grep -q "Host $CLOUDTOP_NAME" "$SSH_CONFIG" 2>/dev/null; then
  echo -e "\033[1;33mWarning: Host $CLOUDTOP_NAME is already in ~/.ssh/config. Appending new block.\033[0m"
fi

cat "$TEMP_SSH" >> "$SSH_CONFIG"
chmod 600 "$SSH_CONFIG"
rm -f "$TEMP_SSH"
echo -e "\033[1;32m✅ ~/.ssh/config updated successfully.\033[0m"

# 4. Configure ~/.bashrc
BASHRC="$HOME/.bashrc"
if [[ -f "$BASHRC" ]]; then
  cp "$BASHRC" "$HOME/.bashrc.bak.$TIMESTAMP"
fi

if grep -q "# --- Smart Cloudtop Connect" "$BASHRC" 2>/dev/null; then
  echo -e "\033[1;33m~/.bashrc already contains Cloudtop aliases. Skipping append.\033[0m"
else
  echo "" >> "$BASHRC"
  cat "$SCRIPT_DIR/chromebook/bashrc_additions.sh" >> "$BASHRC"
  echo -e "\033[1;32m✅ ~/.bashrc updated successfully.\033[0m"
fi

echo ""
echo -e "\033[1;36m============================================================\033[0m"
echo -e "\033[1;32m🎉 Setup Complete!\033[0m"
echo -e "Run \033[1;33msource ~/.bashrc\033[0m to activate your new commands."
echo -e "Daily workflow:"
echo -e "  1. \033[1;32mct\033[0m            -> Authenticates & opens your primary Cloudtop shell"
echo -e "  2. \033[1;32mtunnel\033[0m        -> Starts background port forwarder (9000, 9090, 8888, 5387)"
echo -e "  3. \033[1;32mcodetop\033[0m       -> Launches VS Code Desktop connected to ~/dev"
echo -e "\033[1;36m============================================================\033[0m"
