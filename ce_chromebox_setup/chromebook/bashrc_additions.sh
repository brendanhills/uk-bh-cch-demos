# ==============================================================================
# Bruschetta (Chromebook gLinux VM) Configuration Snippet
# Add this content to ~/.bashrc on your Chromebook / Bruschetta VM
# ==============================================================================

# --- Visual Styling (Optional: Green Laptop Theme & Tab Title) ---
PS1='\[\e]0;💻 Bruschetta: \w\a\]\[\033[01;32m\]💻 bruschetta\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '

# --- VS Code Remote on Cloudtop (Defaults to ~/dev) ---
unalias codetop 2>/dev/null || true
codetop() {
  local target="${1:-/usr/local/google/home/$USER/dev}"
  if [[ "$target" != /* ]]; then
    target="/usr/local/google/home/$USER/dev/$target"
  fi
  code --remote ssh-remote+cloudtop "$target"
}

# --- Smart Cloudtop Connect (Auto-Auth via Roadwarrior) ---
unalias ct 2>/dev/null || true
ct() {
  if command -v gcertstatus >/dev/null 2>&1 && ! gcertstatus --check_ssh_certs >/dev/null 2>&1; then
    echo "🔑 Morning credentials expired. Authenticating via roadwarrior..."
    rw --check_remaining --check_remaining_duration=8h --remote_gcertstatus_args="--check_remaining=8h" cloudtop "$@"
  else
    ssh cloudtop "$@"
  fi
}

alias rw='rw --check_remaining --check_remaining_duration=8h --remote_gcertstatus_args="--check_remaining=8h"'

# --- Background Port Tunnel Management (With Pre-Flight Conflict Check) ---
unalias tunnel 2>/dev/null || true
tunnel() {
  local ports=(9000 9090 9900 8888 5387)
  local cleared=0

  # Check if any dev ports are hijacked by local Bruschetta processes (Python, Node, Docker)
  for p in "${ports[@]}"; do
    local pid
    pid=$(lsof -t -i :"$p" 2>/dev/null || true)
    if [[ -n "$pid" ]]; then
      local pname
      pname=$(ps -p "$pid" -o comm= 2>/dev/null || echo "PID $pid")
      if [[ "$pname" != "autossh" && "$pname" != "ssh" ]]; then
        echo -e "\033[1;33m⚠️ Port $p is held by local '$pname' (PID $pid) in Bruschetta.\033[0m"
        echo "   Releasing port to prevent localhost:$p hijack..."
        kill -9 "$pid" 2>/dev/null || sudo kill -9 "$pid" 2>/dev/null || true
        cleared=1
      fi
    fi
  done

  if [[ $cleared -eq 1 ]]; then
    sleep 0.5
  fi

  AUTOSSH_MAXSTART=1 rw --nossh_interactively --check_remaining --check_remaining_duration=8h --remote_gcertstatus_args="--check_remaining=8h" cloudtop && \
  AUTOSSH_MAXSTART=1 autossh -M 0 -f -N cloudtop-tunnel && \
  echo "✅ Background tunnel active (ports 9000, 9090, 9900, 8888, 5387)"
}

alias tunnel-status='pgrep -fa "autossh.*cloudtop-tunnel" || echo "❌ Tunnel is not running"'
alias tunnel-stop='pkill -f "autossh.*cloudtop-tunnel" && echo "🛑 Tunnel stopped"'
alias tunnel-restart='tunnel-stop; sleep 1; tunnel'
