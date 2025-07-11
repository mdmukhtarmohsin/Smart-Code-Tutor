#!/bin/bash

# Smart Code Tutor Setup Script
# This script sets up the entire Smart Code Tutor application

set -e  # Exit on any error

echo "🚀 Smart Code Tutor Setup Script"
echo "================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python3
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 is required but not installed"
        exit 1
    fi
    print_success "Python3 found: $(python3 --version)"
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is required but not installed"
        exit 1
    fi
    print_success "Node.js found: $(node --version)"
    
    # Check pnpm
    if ! command -v pnpm &> /dev/null; then
        print_warning "pnpm not found. Installing pnpm..."
        npm install -g pnpm
    fi
    print_success "pnpm found: $(pnpm --version)"
    
    # Check if we're in the right directory
    if [[ ! -f "package.json" ]] || [[ ! -d "backend" ]] || [[ ! -d "frontend" ]]; then
        print_error "Please run this script from the Smart Code Tutor root directory"
        exit 1
    fi
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Check if virtual environment exists
    if [[ ! -d "venv" ]]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    print_status "Activating virtual environment and installing dependencies..."
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    python3 -m pip install --upgrade pip
    
    # Install requirements
    print_status "Installing Python dependencies..."
    if [[ -f "requirements-minimal.txt" ]]; then
        print_status "Using minimal requirements for lightweight installation..."
        python3 -m pip install -r requirements-minimal.txt
    elif [[ -f "requirements.txt" ]]; then
        print_status "Using full requirements..."
        python3 -m pip install -r requirements.txt
    else
        print_error "No requirements file found"
        exit 1
    fi
    
    # Check if .env file exists
    if [[ ! -f ".env" ]]; then
        if [[ -f ".env.example" ]]; then
            print_status "Creating .env file from .env.example..."
            cp .env.example .env
            print_warning "Please update .env file with your API keys if needed"
        else
            print_error ".env.example file not found"
            exit 1
        fi
    fi
    
    # Test import
    print_status "Testing backend setup..."
    if python3 -c "import uvicorn, fastapi; print('Backend dependencies OK')" 2>/dev/null; then
        print_success "Backend dependencies verified"
    else
        print_error "Backend setup verification failed"
        exit 1
    fi
    
    cd ..
    print_success "Backend setup completed"
}

# Setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing frontend dependencies..."
    pnpm install
    
    cd ..
    print_success "Frontend setup completed"
}

# Install root dependencies
setup_root() {
    print_status "Setting up root dependencies..."
    pnpm install
    print_success "Root dependencies installed"
}

# Start the application
start_application() {
    print_status "Starting Smart Code Tutor..."
    
    # Check if backend is already running
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port 8000 is already in use. Stopping existing process..."
        pkill -f "uvicorn main:app" || true
        sleep 2
    fi
    
    # Check if frontend is already running
    if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port 3000 is already in use. Will try port 3001..."
    fi
    
    print_status "Starting both backend and frontend..."
    print_status "Backend will run on: http://localhost:8000"
    print_status "Frontend will run on: http://localhost:3000 (or 3001 if 3000 is busy)"
    print_status ""
    print_status "Press Ctrl+C to stop both services"
    print_status ""
    
    # Start both services using the dev script
    pnpm dev
}

# Main execution
main() {
    case "${1:-setup}" in
        "setup")
            check_requirements
            setup_root
            setup_backend
            setup_frontend
            print_success "Setup completed successfully!"
            print_status ""
            print_status "To start the application, run:"
            print_status "  ./setup.sh start"
            print_status ""
            print_status "Or manually:"
            print_status "  pnpm dev"
            ;;
        "start")
            start_application
            ;;
        "backend")
            print_status "Starting backend only..."
            ./backend/start.sh
            ;;
        "frontend")
            print_status "Starting frontend only..."
            cd frontend
            pnpm dev
            ;;
        "clean")
            print_status "Cleaning up..."
            rm -rf backend/venv
            rm -rf frontend/node_modules
            rm -rf node_modules
            rm -rf backend/__pycache__
            rm -rf backend/**/__pycache__
            print_success "Cleanup completed"
            ;;
        "help"|"-h"|"--help")
            echo "Smart Code Tutor Setup Script"
            echo ""
            echo "Usage: ./setup.sh [command]"
            echo ""
            echo "Commands:"
            echo "  setup     - Full setup (default)"
            echo "  start     - Start the application"
            echo "  backend   - Start backend only"
            echo "  frontend  - Start frontend only"
            echo "  clean     - Clean all dependencies"
            echo "  help      - Show this help"
            ;;
        *)
            print_error "Unknown command: $1"
            print_status "Run './setup.sh help' for available commands"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@" 