# ==============================================================================
# Cloudtop Workstation Configuration Snippet
# Add this content to ~/.bashrc on your Cloudtop
# ==============================================================================

# --- Cloudtop Visual Styling (Purple Cloud Theme + Banner) ---
PS1='\[\e]0;☁️ Cloudtop: \w\a\]\[\033[01;35m\]☁️  \h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '

if [[ -z "$VIRTUAL_ENV" && -t 1 ]]; then
  echo -e "\033[1;35m┌────────────────────────────────────────────────────┐\033[0m"
  echo -e "\033[1;35m│\033[0m  \033[1;37m☁️  CONNECTED TO GOOGLE CLOUDTOP (\h)\033[0m \033[1;35m│\033[0m"
  echo -e "\033[1;35m└────────────────────────────────────────────────────┘\033[0m"
fi
