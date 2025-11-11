BASE_URL="http://localhost:8000"

echo "Quick API Test"
echo "======================================"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' 

# Test 1: Health Check
echo -e "\n${BLUE}TEST 1: Health Check${NC}"
curl -s $BASE_URL/health | jq '.'

# Test 2: Cache Stats
echo -e "\n${BLUE}TEST 2: Cache Statistics${NC}"
curl -s $BASE_URL/cache/stats | jq '.'

# Test 3: AI Summarization
echo -e "\n${BLUE}TEST 3: AI Email Summarization${NC}"
curl -s -X POST $BASE_URL/ai/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Quick Meeting",
    "body": "Hi, can we meet tomorrow at 2pm to discuss the project? Let me know if that works. Thanks!"
  }' | jq '.'

# Test 4: Sync Emails
echo -e "\n${BLUE}TEST 4: Sync Emails (3 emails)${NC}"
curl -s -X POST "$BASE_URL/emails/sync?max_results=3" | jq '.'

# Wait for processing
echo -e "\n${YELLOW}Waiting 2 seconds for processing...${NC}"
sleep 2

# Test 5: Statistics
echo -e "\n${BLUE}TEST 5: Email Statistics${NC}"
curl -s $BASE_URL/emails/statistics | jq '.'

# Test 6: List Emails
echo -e "\n${BLUE}TEST 6: List All Emails${NC}"
curl -s "$BASE_URL/emails/list?limit=5" | jq '.'

# Test 7: High Priority Emails
echo -e "\n${BLUE}TEST 7: High Priority Emails${NC}"
curl -s $BASE_URL/emails/filter/high-priority | jq '.'

# Test 8: Meeting Emails
echo -e "\n${BLUE}TEST 8: Meeting Emails${NC}"
curl -s $BASE_URL/emails/filter/meetings | jq '.'

echo -e "\n${GREEN}All tests completed!${NC}\n"