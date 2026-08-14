# Chromebook (Bruschetta) to Cloudtop Remote Development Setup

A battle-tested, high-reliability configuration guide and copy-paste toolkit for Google Customer Engineers working remotely from a **Chromebook (ChromeOS / Bruschetta gLinux VM)** connected to **Google Cloudtop**.

---

## 1. Why this Setup Exists

Connecting to Cloudtop from a Chromebook over Google's WebSocket proxy (`sup-ssh-relay`) often encounters common friction points:
* **Multiplexing Deadlocks (`ControlMaster`):** Shared SSH sockets break when laptops sleep or switch networks, permanently locking forwarded ports with `Address already in use`.
* **Security Key Prompt Loops:** `autossh` backgrounding before authentication causes endless Titan Security Key popup loops (5–7+ popups).
* **Identity Probing Failures:** SSH attempts to probe every FIDO2 slot and corporate key sequentially, triggering multiple key touches per connection.
* **Overloaded File Watchers:** Opening `$HOME` over VS Code Remote-SSH recursively indexes `~/.cache`, `~/.local`, and `~/.antigravity`, causing 10,000+ Git change warnings and extension host freezes.
* **Keepalive Conflicts:** `TCPKeepAlive yes` sends raw OS TCP ACK probes that fail through WebSocket relays.

This setup resolves all of these issues with **zero socket multiplexing conflicts**, **single-touch morning authentication**, and **isolated, sub-200ms terminal sessions**.

---

## 2. Directory Structure

```text
ce_chromebox_setup/
├── README.md                          # Comprehensive guide, visual diagrams, and troubleshooting
│
├── chromebook/                        # --- Files for Chromebook (Bruschetta VM) ---
│   ├── ssh_config.template            # ~/.ssh/config template (no multiplexing, IdentitiesOnly)
│   └── bashrc_additions.sh            # ~/.bashrc snippet (smart ct, tunnel daemon, codetop, green theme)
│
└── cloudtop/                          # --- Files for Cloudtop Workstation ---
    ├── bashrc_additions.sh            # ~/.bashrc snippet (purple cloud theme & login banner)
    └── tunnel-shell                   # Helper script for ChromeOS native Terminal SWA
```

---

## 3. Daily Workflow (TL;DR)

All daily commands are executed in your **Bruschetta terminal**:

```mermaid
flowchart TD
    subgraph Tab1 ["Bruschetta Tab 1 (Start of Day)"]
        CT1["1. <code>ct</code><br><i>Wakes Cloudtop & authenticates (prompts once if needed)</i>"]
    end

    subgraph Tab2 ["Bruschetta Tab 2 (Web Ports)"]
        T["2. <code>tunnel</code><br><i>Starts background autossh daemon with loop protection</i>"]
    end

    subgraph TabN ["Bruschetta Tab 3+ (Throughout Day)"]
        CTN["3. <code>ct</code><br><i>Instant (<200ms) independent Cloudtop shell</i>"]
    end

    subgraph Editor ["Bruschetta Terminal (Optional)"]
        Code["4. <code>codetop [folder]</code><br><i>Launches VS Code Desktop connected to target project</i>"]
    end

    CT1 --> T
    T --> CTN
    T --> Code
```

### The Step-by-Step Routine

| Step | Location | Command | Description |
| :--- | :--- | :--- | :--- |
| **1. Morning Connect & Auth** | Bruschetta Tab 1 | `ct` | Auto-detects credential state. Prompts once for password/security key if expired, wakes Cloudtop, and opens your primary shell. |
| **2. Start Web Ports** | Bruschetta Tab 2 | `tunnel` | Launches background `autossh` daemon with loop protection (`AUTOSSH_MAXSTART=1`). Connects silently with verified credentials. |
| **3. Open More Shell Tabs** | New Bruschetta Tabs | `ct` | Opens additional fresh, independent SSH tabs on Cloudtop in <200ms. |
| **4. Open VS Code** | Bruschetta Tab | `codetop [project]` | Launches VS Code connected to targeted project folder (avoids root `$HOME` file-watcher overload). |

### Tunnel Management Commands (Run in Bruschetta)

| Task | Command | Expected Output |
| :--- | :--- | :--- |
| **Start Tunnel** | `tunnel` | Authenticates via `rw`, starts daemon $\rightarrow$ `✅ Background tunnel active` |
| **Check Status** | `tunnel-status` | Displays running `autossh` PID and command line. |
| **Stop Tunnel** | `tunnel-stop` | `🛑 Tunnel stopped` |
| **Restart Tunnel** | `tunnel-restart` | Stops and restarts the background daemon. |

---

## 4. Setup Walkthrough

Because remote development involves both your local client and remote workstation, setup is divided into two transparent copy-paste steps:

---

### Part 1: On your Chromebook (Inside Bruschetta VM)

#### Step 1: Configure `~/.ssh/config`
Open `~/.ssh/config` in Bruschetta:
```bash
nano ~/.ssh/config   # or your preferred editor
```
Copy and paste the template from [`chromebook/ssh_config.template`](chromebook/ssh_config.template), replacing `<CLOUDTOP_NAME>` and `<LDAP_USERNAME>` with your details:

```sshconfig
##### Primary Cloudtop Host (Clean, Independent Shell Sessions & VS Code)
Host <CLOUDTOP_NAME>.c.googlers.com <CLOUDTOP_NAME> cloudtop ct
  HostName <CLOUDTOP_NAME>.c.googlers.com
  User <LDAP_USERNAME>
  AddressFamily inet
  IdentitiesOnly yes

##### Dedicated Background Tunnel Host (Web Dev & Colab Ports)
Host cloudtop-tunnel
  HostName <CLOUDTOP_NAME>.c.googlers.com
  User <LDAP_USERNAME>
  AddressFamily inet
  ExitOnForwardFailure yes
  IdentitiesOnly yes
  LocalForward 9000 127.0.0.1:9000
  LocalForward 9090 127.0.0.1:9090
  LocalForward 9900 127.0.0.1:9900
  LocalForward 8888 127.0.0.1:8888
  LocalForward 5387 127.0.0.1:5387

##### GitHub
Host github.com
  IdentitiesOnly yes
  AddKeysToAgent yes

##### Global Defaults (No Multiplexing, Optimized WebSocket KeepAlive)
Host *
  TCPKeepAlive no
  ServerAliveInterval 15
  ServerAliveCountMax 3
  ConnectTimeout 30
  ConnectionAttempts 3
  ForwardX11 no
```

#### Step 2: Add Functions & Visual Styling to `~/.bashrc`
Append the contents of [`chromebook/bashrc_additions.sh`](chromebook/bashrc_additions.sh) to your Bruschetta `~/.bashrc`:

```bash
# --- Visual Styling (Green Laptop Theme) ---
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

# --- Background Port Tunnel Management (With Auto-Auth & Loop Protection) ---
alias tunnel='AUTOSSH_MAXSTART=1 rw --nossh_interactively --check_remaining --check_remaining_duration=8h --remote_gcertstatus_args="--check_remaining=8h" cloudtop && AUTOSSH_MAXSTART=1 autossh -M 0 -f -N cloudtop-tunnel && echo "✅ Background tunnel active (ports 9000, 9090, 9900, 8888, 5387)"'
alias tunnel-status='pgrep -fa "autossh.*cloudtop-tunnel" || echo "❌ Tunnel is not running"'
alias tunnel-stop='pkill -f "autossh.*cloudtop-tunnel" && echo "🛑 Tunnel stopped"'
alias tunnel-restart='tunnel-stop; sleep 1; tunnel'
```
Reload with `source ~/.bashrc`.

---

### Part 2: On your Cloudtop Workstation

#### Step 1: Add Visual Styling & Banner to `~/.bashrc`
Connect to Cloudtop (`ct`) and append the contents of [`cloudtop/bashrc_additions.sh`](cloudtop/bashrc_additions.sh) to `~/.bashrc`:

```bash
# --- Cloudtop Visual Styling (Purple Cloud Theme + Banner) ---
PS1='\[\e]0;☁️ Cloudtop: \w\a\]\[\033[01;35m\]☁️  \h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '

if [[ -z "$VIRTUAL_ENV" && -t 1 ]]; then
  echo -e "\033[1;35m┌────────────────────────────────────────────────────┐\033[0m"
  echo -e "\033[1;35m│\033[0m  \033[1;37m☁️  CONNECTED TO GOOGLE CLOUDTOP (\h)\033[0m \033[1;35m│\033[0m"
  echo -e "\033[1;35m└────────────────────────────────────────────────────┘\033[0m"
fi
```
Reload with `source ~/.bashrc`.

#### Step 2 (Optional): ChromeOS Native Terminal SWA Helper
If you use native ChromeOS Terminal links (without Bruschetta), copy [`cloudtop/tunnel-shell`](cloudtop/tunnel-shell) to `~/bin/tunnel-shell` on Cloudtop:
```bash
mkdir -p ~/bin
cp cloudtop/tunnel-shell ~/bin/tunnel-shell
chmod +x ~/bin/tunnel-shell
```

---

## 5. Port Forwarding Directory

| Port | Service | Access URL | Notes |
| :--- | :--- | :--- | :--- |
| **`9000`** | Primary Web App / Dev Server | `http://localhost:9000` | Main local debugging port. |
| **`9090`** | Secondary Web App / API | `http://localhost:9090` | Secondary dev service. |
| **`9900`** | Tertiary Web App / Worker | `http://localhost:9900` | Additional staging/test service. |
| **`8888`** | Google Colab Local Runtime / Jupyter | `http://localhost:8888` | Connects browser Colab notebook to Cloudtop execution kernel. |
| **`5387`** | Jetski Hub Server | `http://jetski/?box=<CLOUDTOP_NAME>`<br>*(or `http://localhost:5387`)* | Primary access via ÜberProxy; local port forwarded as fallback. |

---

## 6. Native ChromeOS Terminal Links (No Bruschetta VM Needed)

If you need instant terminal access directly in ChromeOS without starting the Bruschetta VM:
* **Command Box:** (ChromeOS Terminal already includes `ssh `, so do not type `ssh`):
  ```text
  <USER>@<CLOUDTOP_NAME>.c.googlers.com -L 9000:localhost:9000 -L 9090:localhost:9090 -L 9900:localhost:9900 -L 8888:localhost:8888 -o ServerAliveInterval=15 -o ServerAliveCountMax=3 -t ~/bin/tunnel-shell
  ```
* **SSH relay server options:** `--config=google`

---

## 7. Troubleshooting Runbook

### Issue 1: Multiple Security Key Popups in a Row
* **Cause:** `autossh` was launched in the background before credentials were valid, or `IdentitiesOnly yes` is missing.
* **Fix:**
  ```bash
  pkill -9 -f autossh; pkill -9 -f cloudtop-tunnel
  ```
  Ensure `IdentitiesOnly yes` is present in `~/.ssh/config` and run `ct` first to authenticate in the foreground.

### Issue 2: Port Locked (`Address in use`)
* **Cause:** A previous hung SSH process is still listening on port 9000 or 8888.
* **Fix:**
  ```bash
  sudo kill -9 $(lsof -t -i :9000 -i :8888) 2>/dev/null || true
  tunnel-restart
  ```

### Issue 3: VS Code Shows ">10,000 Changes in Git" or Slow Extension Loading
* **Cause:** An accidental `.git` folder was created in root `$HOME`.
* **Fix:** Run on Cloudtop:
  ```bash
  rm -rf ~/.git
  ```

### Issue 4: `Connection closed by UNKNOWN port 65535`
* **Cause:** SSO master cookie expired.
* **Fix:** Run `ct` to trigger roadwarrior authentication.
