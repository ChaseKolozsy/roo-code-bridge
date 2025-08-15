#!/bin/bash

echo "🚀 Starting Roo-Code Bridge Components..."
echo "========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if VS Code extension is compiled
echo -e "${YELLOW}Checking VS Code extension...${NC}"
if [ ! -d "extension/out" ]; then
    echo -e "${YELLOW}Compiling VS Code extension...${NC}"
    cd extension
    npm install
    npm run compile
    cd ..
fi
echo -e "${GREEN}✅ Extension ready${NC}"

# Install Python dependencies if needed
echo -e "${YELLOW}Checking Python dependencies...${NC}"
if [ ! -d "server/venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    cd server
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
else
    source server/venv/bin/activate
fi
echo -e "${GREEN}✅ Python environment ready${NC}"

# Start the FastAPI server
echo -e "${YELLOW}Starting FastAPI server...${NC}"
cd server/src
python main.py &
SERVER_PID=$!
cd ../..
echo -e "${GREEN}✅ Server started (PID: $SERVER_PID)${NC}"

echo ""
echo "========================================="
echo -e "${GREEN}🎉 Roo-Code Bridge is starting!${NC}"
echo ""
echo "Next steps:"
echo "1. Open VS Code/Cursor"
echo "2. Install the extension from: extension/"
echo "3. Run the extension (F5 in VS Code)"
echo "4. Execute: 'Roo-Code Bridge: Start Server'"
echo ""
echo "To test the connection:"
echo "  cd server && python tests/test_phase1.py"
echo ""
echo "To stop the server:"
echo "  kill $SERVER_PID"
echo "========================================="

# Keep the script running
wait $SERVER_PID