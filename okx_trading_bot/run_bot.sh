
#!/bin/bash

# OKX Trading Bot Startup Script
# This script handles the startup and monitoring of the trading bot

set -e

# Configuration
BOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$BOT_DIR/venv"
LOG_DIR="$BOT_DIR/logs"
PID_FILE="$BOT_DIR/bot.pid"
PYTHON_SCRIPT="$BOT_DIR/main.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if bot is already running
check_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0  # Running
        else
            rm -f "$PID_FILE"
            return 1  # Not running
        fi
    fi
    return 1  # Not running
}

# Start the bot
start_bot() {
    log "Starting OKX Trading Bot..."
    
    # Check if already running
    if check_running; then
        warning "Bot is already running (PID: $(cat $PID_FILE))"
        return 1
    fi
    
    # Check prerequisites
    if [ ! -f "$BOT_DIR/config.yml" ]; then
        error "Configuration file not found: $BOT_DIR/config.yml"
        error "Please copy config_template.yml to config.yml and configure your settings"
        return 1
    fi
    
    if [ ! -f "$BOT_DIR/.env" ]; then
        error "Environment file not found: $BOT_DIR/.env"
        error "Please copy .env.example to .env and add your API keys"
        return 1
    fi
    
    # Create log directory
    mkdir -p "$LOG_DIR"
    
    # Activate virtual environment
    if [ ! -d "$VENV_DIR" ]; then
        error "Virtual environment not found: $VENV_DIR"
        error "Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
        return 1
    fi
    
    source "$VENV_DIR/bin/activate"
    
    # Check Python dependencies
    if ! python -c "import ccxt, discord, pandas, numpy, talib" 2>/dev/null; then
        error "Missing Python dependencies. Please run: pip install -r requirements.txt"
        return 1
    fi
    
    # Start the bot in background
    cd "$BOT_DIR"
    nohup python "$PYTHON_SCRIPT" > "$LOG_DIR/bot_output.log" 2>&1 &
    local pid=$!
    
    # Save PID
    echo $pid > "$PID_FILE"
    
    # Wait a moment and check if it started successfully
    sleep 3
    if ps -p "$pid" > /dev/null 2>&1; then
        success "Trading bot started successfully (PID: $pid)"
        log "Logs: tail -f $LOG_DIR/trading_bot.log"
        log "Output: tail -f $LOG_DIR/bot_output.log"
        return 0
    else
        error "Failed to start trading bot"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Stop the bot
stop_bot() {
    log "Stopping OKX Trading Bot..."
    
    if ! check_running; then
        warning "Bot is not running"
        return 1
    fi
    
    local pid=$(cat "$PID_FILE")
    
    # Send SIGTERM for graceful shutdown
    kill -TERM "$pid" 2>/dev/null || true
    
    # Wait for graceful shutdown
    local count=0
    while ps -p "$pid" > /dev/null 2>&1 && [ $count -lt 30 ]; do
        sleep 1
        count=$((count + 1))
    done
    
    # Force kill if still running
    if ps -p "$pid" > /dev/null 2>&1; then
        warning "Graceful shutdown failed, forcing termination..."
        kill -KILL "$pid" 2>/dev/null || true
        sleep 2
    fi
    
    # Clean up PID file
    rm -f "$PID_FILE"
    
    if ! ps -p "$pid" > /dev/null 2>&1; then
        success "Trading bot stopped successfully"
        return 0
    else
        error "Failed to stop trading bot"
        return 1
    fi
}

# Restart the bot
restart_bot() {
    log "Restarting OKX Trading Bot..."
    stop_bot
    sleep 2
    start_bot
}

# Show bot status
status_bot() {
    if check_running; then
        local pid=$(cat "$PID_FILE")
        success "Trading bot is running (PID: $pid)"
        
        # Show process info
        ps -p "$pid" -o pid,ppid,cmd,etime,pcpu,pmem 2>/dev/null || true
        
        # Show recent logs
        if [ -f "$LOG_DIR/trading_bot.log" ]; then
            echo ""
            log "Recent log entries:"
            tail -n 5 "$LOG_DIR/trading_bot.log" 2>/dev/null || true
        fi
        
        return 0
    else
        warning "Trading bot is not running"
        return 1
    fi
}

# Show logs
show_logs() {
    local log_type=${1:-"main"}
    
    case $log_type in
        "main"|"trading")
            if [ -f "$LOG_DIR/trading_bot.log" ]; then
                tail -f "$LOG_DIR/trading_bot.log"
            else
                error "Log file not found: $LOG_DIR/trading_bot.log"
            fi
            ;;
        "error"|"errors")
            if [ -f "$LOG_DIR/errors.log" ]; then
                tail -f "$LOG_DIR/errors.log"
            else
                error "Error log file not found: $LOG_DIR/errors.log"
            fi
            ;;
        "output")
            if [ -f "$LOG_DIR/bot_output.log" ]; then
                tail -f "$LOG_DIR/bot_output.log"
            else
                error "Output log file not found: $LOG_DIR/bot_output.log"
            fi
            ;;
        *)
            error "Unknown log type: $log_type"
            echo "Available log types: main, error, output"
            ;;
    esac
}

# Setup function for first-time installation
setup_bot() {
    log "Setting up OKX Trading Bot..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_DIR" ]; then
        log "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    log "Upgrading pip..."
    pip install --upgrade pip
    
    # Install requirements
    if [ -f "$BOT_DIR/requirements.txt" ]; then
        log "Installing Python dependencies..."
        pip install -r "$BOT_DIR/requirements.txt"
    else
        error "Requirements file not found: $BOT_DIR/requirements.txt"
        return 1
    fi
    
    # Copy configuration templates if they don't exist
    if [ ! -f "$BOT_DIR/config.yml" ] && [ -f "$BOT_DIR/config_template.yml" ]; then
        log "Copying configuration template..."
        cp "$BOT_DIR/config_template.yml" "$BOT_DIR/config.yml"
        warning "Please edit config.yml with your trading parameters"
    fi
    
    if [ ! -f "$BOT_DIR/.env" ] && [ -f "$BOT_DIR/.env.example" ]; then
        log "Copying environment template..."
        cp "$BOT_DIR/.env.example" "$BOT_DIR/.env"
        warning "Please edit .env with your API keys and credentials"
    fi
    
    # Create necessary directories
    mkdir -p "$LOG_DIR"
    mkdir -p "$BOT_DIR/data"
    mkdir -p "$BOT_DIR/reports"
    mkdir -p "$BOT_DIR/reports/charts"
    
    success "Setup completed successfully!"
    echo ""
    warning "Next steps:"
    echo "1. Edit config.yml with your trading parameters"
    echo "2. Edit .env with your OKX API keys and Discord tokens"
    echo "3. Run: ./run_bot.sh start"
}

# Health check function
health_check() {
    log "Performing health check..."
    
    local issues=0
    
    # Check if bot is running
    if check_running; then
        success "✓ Bot process is running"
    else
        error "✗ Bot process is not running"
        issues=$((issues + 1))
    fi
    
    # Check configuration files
    if [ -f "$BOT_DIR/config.yml" ]; then
        success "✓ Configuration file exists"
    else
        error "✗ Configuration file missing"
        issues=$((issues + 1))
    fi
    
    if [ -f "$BOT_DIR/.env" ]; then
        success "✓ Environment file exists"
    else
        error "✗ Environment file missing"
        issues=$((issues + 1))
    fi
    
    # Check virtual environment
    if [ -d "$VENV_DIR" ]; then
        success "✓ Virtual environment exists"
    else
        error "✗ Virtual environment missing"
        issues=$((issues + 1))
    fi
    
    # Check log files
    if [ -f "$LOG_DIR/trading_bot.log" ]; then
        success "✓ Log file exists"
        local log_size=$(stat -f%z "$LOG_DIR/trading_bot.log" 2>/dev/null || stat -c%s "$LOG_DIR/trading_bot.log" 2>/dev/null || echo "0")
        if [ "$log_size" -gt 0 ]; then
            success "✓ Log file has content"
        else
            warning "⚠ Log file is empty"
        fi
    else
        warning "⚠ Log file not found (normal if bot hasn't run yet)"
    fi
    
    # Check disk space
    local disk_usage=$(df "$BOT_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$disk_usage" -lt 90 ]; then
        success "✓ Sufficient disk space ($disk_usage% used)"
    else
        warning "⚠ Low disk space ($disk_usage% used)"
    fi
    
    echo ""
    if [ $issues -eq 0 ]; then
        success "Health check passed! No issues found."
        return 0
    else
        error "Health check failed! Found $issues issue(s)."
        return 1
    fi
}

# Show help
show_help() {
    echo "OKX Trading Bot Control Script"
    echo ""
    echo "Usage: $0 {start|stop|restart|status|logs|setup|health|help}"
    echo ""
    echo "Commands:"
    echo "  start     Start the trading bot"
    echo "  stop      Stop the trading bot"
    echo "  restart   Restart the trading bot"
    echo "  status    Show bot status and recent logs"
    echo "  logs      Show live logs (main|error|output)"
    echo "  setup     Initial setup and dependency installation"
    echo "  health    Perform system health check"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start                 # Start the bot"
    echo "  $0 logs main            # Show main logs"
    echo "  $0 logs error           # Show error logs"
    echo "  $0 health               # Check system health"
    echo ""
    echo "Log files:"
    echo "  $LOG_DIR/trading_bot.log    # Main application logs"
    echo "  $LOG_DIR/errors.log         # Error logs"
    echo "  $LOG_DIR/bot_output.log     # Bot stdout/stderr"
    echo ""
}

# Main script logic
case "${1:-help}" in
    start)
        start_bot
        ;;
    stop)
        stop_bot
        ;;
    restart)
        restart_bot
        ;;
    status)
        status_bot
        ;;
    logs)
        show_logs "${2:-main}"
        ;;
    setup)
        setup_bot
        ;;
    health)
        health_check
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac

exit $?
