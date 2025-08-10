#!/usr/bin/env python3
"""
Focused test for donor response email inclusion functionality
Tests the specific scenarios requested in the review
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

def make_request(method, endpoint, data=None, headers=None, token=None):
    """Make HTTP request with proper error handling"""
    url = f"{API_BASE}{endpoint}"
    
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    
    if token:
        headers['Authorization'] = f"Bearer {token}"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=15)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=15)
        
        return response
    except Exception as e:
        print(f"Request error: {str(e)}")
        return None

def test_donor_response_email_functionality():
    """Test the specific scenarios for donor response email inclusion"""
    print("🩸 Testing Donor Response Email Inclusion Functionality")
    print("=" * 60)
    
    # Step 1: Register a hospital staff user
    print("\n1️⃣ Registering hospital staff user...")
    hospital_data = {
        "email": "emergency.coordinator@cityhospital.org",
        "password": "HospitalSecure2025!",
        "name": "Dr. Emily Rodriguez",
        "role": "hospital_staff",
        "phone": "+1-555-0199",
        "hospital_name": "City Emergency Hospital",
        "hospital_address": "456 Emergency Ave, Medical District"
    }
    
    response = make_request('POST', '/register', hospital_data)
    if not response or response.status_code != 200:
        print(f"❌ Hospital registration failed: {response.status_code if response else 'No response'}")
        if response:
            print(f"Error: {response.json().get('detail', 'Unknown error')}")
        return False
    
    hospital_token = response.json()['access_token']
    print("✅ Hospital staff registered successfully")
    
    # Step 2: Register a donor user
    print("\n2️⃣ Registering donor user...")
    donor_data = {
        "email": "alex.thompson@email.com",
        "password": "DonorSecure2025!",
        "name": "Alex Thompson",
        "role": "donor",
        "phone": "+1-555-0287",
        "blood_type": "A+",
        "city": "Medical District",
        "latitude": 40.7589,
        "longitude": -73.9851
    }
    
    response = make_request('POST', '/register', donor_data)
    if not response or response.status_code != 200:
        print(f"❌ Donor registration failed: {response.status_code if response else 'No response'}")
        if response:
            print(f"Error: {response.json().get('detail', 'Unknown error')}")
        return False
    
    donor_token = response.json()['access_token']
    print("✅ Donor registered successfully")
    
    # Step 3: Hospital creates a blood alert
    print("\n3️⃣ Hospital creating blood alert...")
    alert_data = {
        "blood_type": "A+",
        "units_needed": 3,
        "urgency_level": "high",
        "description": "Patient in ICU requires A+ blood for emergency surgery",
        "radius_km": 30
    }
    
    response = make_request('POST', '/alerts', alert_data, token=hospital_token)
    if not response or response.status_code != 200:
        print(f"❌ Blood alert creation failed: {response.status_code if response else 'No response'}")
        if response:
            print(f"Error: {response.json().get('detail', 'Unknown error')}")
        return False
    
    alert_id = response.json()['id']
    print(f"✅ Blood alert created successfully (ID: {alert_id})")
    
    # Step 4: Donor responds "available" to the alert
    print("\n4️⃣ Donor responding to alert...")
    response_data = {
        "response": "available",
        "message": "I'm available to donate. Can be at the hospital within 45 minutes."
    }
    
    response = make_request('POST', f'/alerts/{alert_id}/respond', response_data, token=donor_token)
    if not response or response.status_code != 200:
        print(f"❌ Donor response failed: {response.status_code if response else 'No response'}")
        if response:
            print(f"Error: {response.json().get('detail', 'Unknown error')}")
        return False
    
    print("✅ Donor responded successfully")
    
    # Step 5: Verify the response includes both donor_email and donor_phone
    print("\n5️⃣ Verifying response includes donor email and phone...")
    response = make_request('GET', f'/alerts/{alert_id}/responses', token=hospital_token)
    if not response or response.status_code != 200:
        print(f"❌ Failed to retrieve responses: {response.status_code if response else 'No response'}")
        if response:
            print(f"Error: {response.json().get('detail', 'Unknown error')}")
        return False
    
    responses = response.json()
    if not responses:
        print("❌ No responses found")
        return False
    
    donor_response = responses[0]
    print(f"📋 Response data: {json.dumps(donor_response, indent=2)}")
    
    # Check for required fields
    required_fields = ['donor_email', 'donor_phone', 'donor_name', 'response']
    missing_fields = [field for field in required_fields if field not in donor_response]
    
    if missing_fields:
        print(f"❌ Missing required fields: {missing_fields}")
        return False
    
    # Verify email and phone are correct
    if donor_response['donor_email'] != 'alex.thompson@email.com':
        print(f"❌ Email mismatch. Expected: alex.thompson@email.com, Got: {donor_response['donor_email']}")
        return False
    
    if donor_response['donor_phone'] != '+1-555-0287':
        print(f"❌ Phone mismatch. Expected: +1-555-0287, Got: {donor_response['donor_phone']}")
        return False
    
    print("✅ Response includes correct donor email and phone")
    
    # Step 6: Hospital staff retrieves responses and confirms email is visible
    print("\n6️⃣ Confirming hospital staff can see donor contact information...")
    print(f"✅ Hospital staff can see:")
    print(f"   📧 Donor Email: {donor_response['donor_email']}")
    print(f"   📱 Donor Phone: {donor_response['donor_phone']}")
    print(f"   👤 Donor Name: {donor_response['donor_name']}")
    print(f"   💬 Response: {donor_response['response']}")
    print(f"   📝 Message: {donor_response.get('message', 'No message')}")
    
    print("\n🎉 ALL TESTS PASSED!")
    print("✅ DonorResponse model includes donor_email field")
    print("✅ Response creation properly includes donor's email")
    print("✅ Hospital staff can see both email and phone when viewing responses")
    
    return True

if __name__ == "__main__":
    success = test_donor_response_email_functionality()
    if success:
        print("\n🏆 Donor response email inclusion functionality is working correctly!")
    else:
        print("\n💥 Some tests failed. Please check the output above.")