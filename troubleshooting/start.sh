#!/bin/bash

echo "🔒 VulnScan - Web Vulnerability Scanner"
echo "========================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if ports are available
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo "⚠️  Port $1 is already in use"
        return 1
    fi
    return 0
}

echo "Checking port availability..."
check_port 3000 || echo "   You may need to stop the process using port 3000"
check_port 8000 || echo "   You may need to stop the process using port 8000"
check_port 8080 || echo "   You may need to stop the process using port 8080"
echo ""

echo "🚀 Starting VulnScan..."
echo ""

# Start Docker Compose
docker-compose up --build -d

echo ""
echo "✅ VulnScan is starting up!"
echo ""
echo "📍 Access points:"
echo "   Frontend:  http://localhost:3000"
echo "   API:       http://localhost:8000"
echo "   DVWA:      http://localhost:8080"
echo ""
echo "⏳ Please wait 30-60 seconds for all services to fully start"
echo ""
echo "📝 To view logs: docker-compose logs -f"
echo "🛑 To stop:      docker-compose down"
echo ""
