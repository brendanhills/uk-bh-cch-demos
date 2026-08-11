#!/usr/bin/env bash
# ==============================================================================
# run_server.sh - Manage Project Dash server in a dedicated tmux session
# ==============================================================================
# Usage:
#   ./run_server.sh           # Start/Restart server, create session if needed, attach
#   ./run_server.sh start     # Same as default
#   ./run_server.sh restart   # Restart server in tmux session and attach
#   ./run_server.sh kill      # Stop server and kill tmux session
#   ./run_server.sh stop      # Alias for kill
#   ./run_server.sh status    # Check status of session and server
#   ./run_server.sh --no-attach # Start/restart in background without attaching
# ==============================================================================

set -e

SESSION_NAME="project-dash"
PORT=9000
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMAND="python3 server.py"

# Function to check if tmux session exists
session_exists() {
    tmux has-session -t "$SESSION_NAME" 2>/dev/null
}

# Function to check if server process is running
server_process_running() {
    if session_exists && tmux capture-pane -pt "$SESSION_NAME" -S -15 2>/dev/null | grep -q "Serving Project Dash"; then
        return 0
    elif pgrep -f "[p]ython3.*server\.py" >/dev/null 2>&1 || pgrep -f "[u]v run.*server\.py" >/dev/null 2>&1; then
        return 0
    fi
    return 1
}

# Function to check if port/server is currently active
port_in_use() {
    if server_process_running; then
        return 0
    elif command -v lsof >/dev/null 2>&1 && lsof -i :$PORT -sTCP:LISTEN >/dev/null 2>&1; then
        return 0
    elif command -v ss >/dev/null 2>&1 && ss -tuln | grep -q ":$PORT "; then
        return 0
    elif command -v netstat >/dev/null 2>&1 && netstat -tuln | grep -q ":$PORT "; then
        return 0
    fi
    return 1
}

# Function to attach to session
attach_session() {
    if [ -n "$TMUX" ]; then
        echo "💡 Currently inside another tmux session. Switching client to '$SESSION_NAME'..."
        tmux switch-client -t "$SESSION_NAME" 2>/dev/null || {
            echo "👉 To view session: tmux switch-client -t $SESSION_NAME"
        }
    else
        echo "🔗 Attaching to tmux session '$SESSION_NAME' (Press 'Ctrl+b' then 'd' to detach)..."
        exec tmux attach-session -t "$SESSION_NAME"
    fi
}

# Action: Kill / Stop
do_kill() {
    if session_exists; then
        echo "🛑 Stopping server and killing tmux session '$SESSION_NAME'..."
        tmux send-keys -t "$SESSION_NAME" C-c 2>/dev/null || true
        sleep 0.5
        tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true
        echo "✅ Tmux session '$SESSION_NAME' terminated."
    else
        echo "ℹ️  Tmux session '$SESSION_NAME' is not running."
    fi

    # Clean up any orphan process on port 9000 if remaining
    if port_in_use; then
        echo "🧹 Cleaning up lingering process on port $PORT..."
        if command -v lsof >/dev/null 2>&1; then
            lsof -ti :$PORT | xargs kill -9 2>/dev/null || true
        elif command -v fuser >/dev/null 2>&1; then
            fuser -k $PORT/tcp 2>/dev/null || true
        fi
    fi
    echo "✨ Server is completely stopped."
}

# Action: Status
do_status() {
    echo "================================================================"
    echo "📊 Project Dash Status Check"
    echo "================================================================"
    if session_exists; then
        echo "  🟢 Tmux Session:    ACTIVE ('$SESSION_NAME')"
    else
        echo "  🔴 Tmux Session:    INACTIVE"
    fi

    if port_in_use; then
        echo "  🟢 Port $PORT:        LISTENING (Server is live)"
        echo "  👉 Local URL:       http://localhost:$PORT"
        echo "  👉 Loopback URL:    http://127.0.0.1:$PORT"
    else
        echo "  🔴 Port $PORT:        NOT LISTENING (Server is stopped)"
    fi
    echo "================================================================"
}

# Action: Start / Restart
do_run() {
    local should_restart="$1"
    local no_attach="$2"

    if ! session_exists; then
        echo "🚀 Creating new tmux session '$SESSION_NAME' in $PROJECT_DIR..."
        tmux new-session -d -s "$SESSION_NAME" -c "$PROJECT_DIR" "$COMMAND"
        sleep 0.8
        echo "✅ Session created and server started."
    else
        echo "ℹ️  Tmux session '$SESSION_NAME' already exists."
        if [ "$should_restart" = "true" ] || port_in_use; then
            echo "🔄 Restarting server in session '$SESSION_NAME'..."
            tmux send-keys -t "$SESSION_NAME" C-c 2>/dev/null || true
            sleep 0.5
            tmux send-keys -t "$SESSION_NAME" "cd '$PROJECT_DIR' && $COMMAND" C-m
            sleep 0.8
            echo "✅ Server restarted."
        else
            echo "▶️  Starting server in existing session '$SESSION_NAME'..."
            tmux send-keys -t "$SESSION_NAME" "cd '$PROJECT_DIR' && $COMMAND" C-m
            sleep 0.8
            echo "✅ Server started."
        fi
    fi

    if [ "$no_attach" != "true" ]; then
        attach_session
    else
        echo "👉 Background mode: Server is running in '$SESSION_NAME'. Run '$0' or 'tmux a -t $SESSION_NAME' to attach."
    fi
}

# Parse CLI arguments
ACTION="${1:-default}"
NO_ATTACH=false

if [ "$2" = "--no-attach" ] || [ "$1" = "--no-attach" ]; then
    NO_ATTACH=true
fi

case "$ACTION" in
    kill|stop)
        do_kill
        ;;
    status)
        do_status
        ;;
    restart)
        do_run true "$NO_ATTACH"
        ;;
    start|default|"")
        do_run true "$NO_ATTACH"
        ;;
    help|-h|--help)
        echo "Usage: $0 [start|restart|kill|stop|status|--no-attach|help]"
        echo ""
        echo "Commands:"
        echo "  (no arg) / start  : Creates tmux if not existing, restarts/starts server, attaches."
        echo "  restart           : Restarts the server inside tmux and attaches."
        echo "  kill / stop       : Stops server and kills tmux session."
        echo "  status            : Shows live status of tmux session and port."
        echo "  --no-attach       : Runs command without attaching to tmux session."
        echo "  help              : Displays this usage guide."
        ;;
    *)
        echo "Unknown option: $ACTION"
        echo "Run '$0 help' for available options."
        exit 1
        ;;
esac
