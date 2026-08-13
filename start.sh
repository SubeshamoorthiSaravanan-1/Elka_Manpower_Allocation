#!/bin/bash

# Elkayem Manpower Allocation System – Startup Script
# Usage: ./start.sh [options]

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PORT=8080
MODE="foreground"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -b|--background)
            MODE="background"
            shift
            ;;
        -s|--stop)
            MODE="stop"
            shift
            ;;
        -l|--logs)
            MODE="logs"
            shift
            ;;
        -h|--help)
            echo "Usage: ./start.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -p, --port PORT         Use custom port (default: 8080)"
            echo "  -b, --background        Run in background"
            echo "  -s, --stop              Stop background server"
            echo "  -l, --logs              Show server logs"
            echo "  -h, --help              Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./start.sh              Start in foreground on port 8080"
            echo "  ./start.sh -p 9000      Start on port 9000"
            echo "  ./start.sh -b           Start in background"
            echo "  ./start.sh -s           Stop background server"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    echo "Please install Python 3.6 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${BLUE}Python version: $PYTHON_VERSION${NC}"

# Check if server_advanced.py exists
if [ ! -f "server_advanced.py" ]; then
    echo -e "${RED}✗ server_advanced.py not found${NC}"
    echo "Please ensure server_advanced.py is in the current directory"
    exit 1
fi

if [ ! -f "index_advanced.html" ]; then
    echo -e "${YELLOW}⚠ index_advanced.html not found in current directory${NC}"
    echo "The server may not serve the web interface properly"
fi

case $MODE in
    foreground)
        echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}  Starting Elkayem Manpower Allocation Server${NC}"
        echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
        echo -e "${BLUE}Port: $PORT${NC}"
        echo -e "${BLUE}Mode: Foreground${NC}"
        echo -e "${BLUE}Database: elkayem.db${NC}"
        echo ""
        echo -e "${GREEN}✓ Server starting...${NC}"
        echo -e "${GREEN}✓ Open browser: ${BLUE}http://localhost:$PORT${NC}"
        echo ""
        echo "Default login:"
        echo "  Username: admin"
        echo "  Password: admin123"
        echo ""
        echo "Press Ctrl+C to stop server"
        echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
        echo ""
        
        # Modify PORT in server if needed
        if [ "$PORT" != "8080" ]; then
            python3 -c "
import re
with open('server_advanced.py', 'r') as f:
    content = f.read()
content = re.sub(r'PORT = \d+', f'PORT = {PORT}', content)
with open('server_advanced.py', 'w') as f:
    f.write(content)
" 2>/dev/null || true
        fi
        
        python3 server_advanced.py
        ;;
        
    background)
        echo -e "${BLUE}Starting server in background...${NC}"
        
        # Modify PORT if needed
        if [ "$PORT" != "8080" ]; then
            python3 -c "
import re
with open('server_advanced.py', 'r') as f:
    content = f.read()
content = re.sub(r'PORT = \d+', f'PORT = {PORT}', content)
with open('server_advanced.py', 'w') as f:
    f.write(content)
" 2>/dev/null || true
        fi
        
        nohup python3 server_advanced.py > server.log 2>&1 &
        PID=$!
        sleep 1
        
        if kill -0 $PID 2>/dev/null; then
            echo -e "${GREEN}✓ Server started successfully (PID: $PID)${NC}"
            echo -e "${BLUE}Access at: http://localhost:$PORT${NC}"
            echo -e "${BLUE}View logs: tail -f server.log${NC}"
            echo -e "${BLUE}Stop server: ./start.sh -s${NC}"
        else
            echo -e "${RED}✗ Failed to start server${NC}"
            cat server.log
            exit 1
        fi
        ;;
        
    stop)
        echo -e "${BLUE}Stopping server...${NC}"
        
        if pgrep -f "server_advanced.py" > /dev/null; then
            pkill -f "server_advanced.py"
            sleep 1
            if ! pgrep -f "server_advanced.py" > /dev/null; then
                echo -e "${GREEN}✓ Server stopped${NC}"
            else
                echo -e "${YELLOW}⚠ Server is still running${NC}"
                pkill -9 -f "server_advanced.py"
                echo -e "${GREEN}✓ Forcefully stopped${NC}"
            fi
        else
            echo -e "${YELLOW}⚠ Server is not running${NC}"
        fi
        ;;
        
    logs)
        if [ -f "server.log" ]; then
            echo -e "${BLUE}Showing server logs (press Ctrl+C to exit)...${NC}"
            tail -f server.log
        else
            echo -e "${RED}✗ Log file not found${NC}"
            echo "Run server in background first: ./start.sh -b"
            exit 1
        fi
        ;;
esac

exit 0
