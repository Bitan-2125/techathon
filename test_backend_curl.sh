#!/bin/bash

# Blood Donation System Backend Test Script using curl
API_BASE="https://ebb0cab7-e7f2-4e8f-8928-22586870551f.preview.emergentagent.com/api"

echo "🩸 Blood Donation System Backend Tests"
echo "🌐 Testing against: $API_BASE"
echo "============================================================"

# Test 1: Hospital Registration
echo "🏥 Testing Hospital Registration..."
HOSPITAL_RESPONSE=$(curl -s -X POST "$API_BASE/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dr.smith@hospital.com",
    "password": "HospitalPass123!",
    "name": "Dr. Smith",
    "role": "hospital_staff",
    "hospital_name": "City Medical Center",
    "hospital_address": "123 Health St"
  }')

if echo "$HOSPITAL_RESPONSE" | grep -q "access_token"; then
    echo "✅ Hospital Registration: PASSED"
    HOSPITAL_TOKEN=$(echo "$HOSPITAL_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
else
    echo "❌ Hospital Registration: FAILED"
    echo "$HOSPITAL_RESPONSE"
    exit 1
fi

# Test 2: Donor Registration
echo "🩸 Testing Donor Registration..."
DONOR_RESPONSE=$(curl -s -X POST "$API_BASE/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.donor@email.com",
    "password": "DonorPass123!",
    "name": "John Donor",
    "role": "donor",
    "blood_type": "O+",
    "city": "Downtown",
    "latitude": 40.7128,
    "longitude": -74.0060
  }')

if echo "$DONOR_RESPONSE" | grep -q "access_token"; then
    echo "✅ Donor Registration: PASSED"
    DONOR_TOKEN=$(echo "$DONOR_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
else
    echo "❌ Donor Registration: FAILED"
    echo "$DONOR_RESPONSE"
    exit 1
fi

# Test 3: User Info Endpoint
echo "👤 Testing User Info Endpoint..."
USER_INFO=$(curl -s -X GET "$API_BASE/me" \
  -H "Authorization: Bearer $HOSPITAL_TOKEN")

if echo "$USER_INFO" | grep -q "hospital_staff"; then
    echo "✅ Hospital User Info: PASSED"
else
    echo "❌ Hospital User Info: FAILED"
fi

# Test 4: Blood Alert Creation
echo "🚨 Testing Blood Alert Creation..."
ALERT_RESPONSE=$(curl -s -X POST "$API_BASE/alerts" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $HOSPITAL_TOKEN" \
  -d '{
    "blood_type": "O+",
    "units_needed": 3,
    "urgency_level": "high",
    "description": "Emergency surgery requires O+ blood",
    "radius_km": 30
  }')

if echo "$ALERT_RESPONSE" | grep -q '"id"'; then
    echo "✅ Blood Alert Creation: PASSED"
    ALERT_ID=$(echo "$ALERT_RESPONSE" | grep -o '"id":"[^"]*' | cut -d'"' -f4)
else
    echo "❌ Blood Alert Creation: FAILED"
    echo "$ALERT_RESPONSE"
fi

# Test 5: Alert Retrieval
echo "📋 Testing Alert Retrieval..."
ALERTS=$(curl -s -X GET "$API_BASE/alerts" \
  -H "Authorization: Bearer $HOSPITAL_TOKEN")

if echo "$ALERTS" | grep -q "$ALERT_ID"; then
    echo "✅ Hospital Alert Retrieval: PASSED"
else
    echo "❌ Hospital Alert Retrieval: FAILED"
fi

# Test 6: Donor Response
echo "💬 Testing Donor Response..."
RESPONSE_RESULT=$(curl -s -X POST "$API_BASE/alerts/$ALERT_ID/respond" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DONOR_TOKEN" \
  -d '{
    "response": "available",
    "message": "I can donate within 1 hour"
  }')

if echo "$RESPONSE_RESULT" | grep -q "Response recorded successfully"; then
    echo "✅ Donor Response: PASSED"
else
    echo "❌ Donor Response: FAILED"
    echo "$RESPONSE_RESULT"
fi

# Test 7: Hospital View Responses
echo "👥 Testing Hospital View Responses..."
RESPONSES=$(curl -s -X GET "$API_BASE/alerts/$ALERT_ID/responses" \
  -H "Authorization: Bearer $HOSPITAL_TOKEN")

if echo "$RESPONSES" | grep -q "available"; then
    echo "✅ Hospital View Responses: PASSED"
else
    echo "❌ Hospital View Responses: FAILED"
fi

# Test 8: Dashboard Stats
echo "📊 Testing Dashboard Statistics..."
HOSPITAL_STATS=$(curl -s -X GET "$API_BASE/dashboard/stats" \
  -H "Authorization: Bearer $HOSPITAL_TOKEN")

if echo "$HOSPITAL_STATS" | grep -q "total_alerts"; then
    echo "✅ Hospital Dashboard Stats: PASSED"
else
    echo "❌ Hospital Dashboard Stats: FAILED"
fi

DONOR_STATS=$(curl -s -X GET "$API_BASE/dashboard/stats" \
  -H "Authorization: Bearer $DONOR_TOKEN")

if echo "$DONOR_STATS" | grep -q "total_responses"; then
    echo "✅ Donor Dashboard Stats: PASSED"
else
    echo "❌ Donor Dashboard Stats: FAILED"
fi

# Test 9: Access Control - Donor cannot create alert
echo "🚫 Testing Access Control..."
DONOR_ALERT_ATTEMPT=$(curl -s -X POST "$API_BASE/alerts" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DONOR_TOKEN" \
  -d '{
    "blood_type": "A+",
    "units_needed": 1,
    "urgency_level": "medium",
    "description": "Test",
    "radius_km": 10
  }')

if echo "$DONOR_ALERT_ATTEMPT" | grep -q "Only hospital staff can create alerts"; then
    echo "✅ Donor Alert Restriction: PASSED"
else
    echo "❌ Donor Alert Restriction: FAILED"
fi

# Test 10: Mock Email Notifications
echo "📧 Testing Mock Email Notifications..."
sleep 2  # Wait for notifications to be processed
MOCK_EMAILS=$(curl -s -X GET "$API_BASE/mock-emails" \
  -H "Authorization: Bearer $DONOR_TOKEN")

if echo "$MOCK_EMAILS" | grep -q '\['; then
    echo "✅ Mock Email Notifications: PASSED"
else
    echo "❌ Mock Email Notifications: FAILED"
fi

echo ""
echo "============================================================"
echo "🏁 Backend Core Functionality Tests Complete"
echo "============================================================"