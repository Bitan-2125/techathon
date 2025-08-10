#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Blood Shortage Alert and Donor Mobilization System
Tests all backend endpoints with realistic data scenarios
"""

import requests
import json
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

class BloodDonationTester:
    def __init__(self):
        self.session = requests.Session()
        self.hospital_token = None
        self.donor_token = None
        self.hospital_user = None
        self.donor_user = None
        self.test_alert_id = None
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    def log_result(self, test_name, success, message=""):
        if success:
            print(f"✅ {test_name}: PASSED {message}")
            self.results['passed'] += 1
        else:
            print(f"❌ {test_name}: FAILED {message}")
            self.results['failed'] += 1
            self.results['errors'].append(f"{test_name}: {message}")
    
    def make_request(self, method, endpoint, data=None, headers=None, token=None):
        """Make HTTP request with proper error handling and retries"""
        url = f"{API_BASE}{endpoint}"
        
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f"Bearer {token}"
        
        # Retry logic for connection issues
        for attempt in range(3):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, headers=headers, timeout=10)
                elif method.upper() == 'POST':
                    response = self.session.post(url, json=data, headers=headers, timeout=10)
                elif method.upper() == 'PUT':
                    response = self.session.put(url, json=data, headers=headers, timeout=10)
                elif method.upper() == 'DELETE':
                    response = self.session.delete(url, headers=headers, timeout=10)
                
                return response
            except Exception as e:
                if attempt == 2:  # Last attempt
                    print(f"Request error after 3 attempts: {str(e)}")
                    return None
                time.sleep(1)  # Wait before retry
        
        return None
    
    def test_hospital_registration(self):
        """Test hospital staff registration"""
        print("\n🏥 Testing Hospital Staff Registration...")
        
        hospital_data = {
            "email": "dr.sarah.johnson@cityhospital.com",
            "password": "SecurePass123!",
            "name": "Dr. Sarah Johnson",
            "role": "hospital_staff",
            "phone": "+1-555-0123",
            "hospital_name": "City General Hospital",
            "hospital_address": "123 Medical Center Drive, Downtown"
        }
        
        response = self.make_request('POST', '/register', hospital_data)
        
        if response and response.status_code == 200:
            data = response.json()
            if 'access_token' in data and 'user' in data:
                self.hospital_token = data['access_token']
                self.hospital_user = data['user']
                self.log_result("Hospital Registration", True, f"User ID: {data['user']['id']}")
                return True
            else:
                self.log_result("Hospital Registration", False, "Missing token or user data")
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
            self.log_result("Hospital Registration", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        return False
    
    def test_donor_registration(self):
        """Test donor registration"""
        print("\n🩸 Testing Donor Registration...")
        
        donor_data = {
            "email": "mike.chen@email.com",
            "password": "DonorPass456!",
            "name": "Mike Chen",
            "role": "donor",
            "phone": "+1-555-0456",
            "blood_type": "O+",
            "city": "Downtown",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "last_donation_date": None
        }
        
        response = self.make_request('POST', '/register', donor_data)
        
        if response and response.status_code == 200:
            data = response.json()
            if 'access_token' in data and 'user' in data:
                self.donor_token = data['access_token']
                self.donor_user = data['user']
                self.log_result("Donor Registration", True, f"User ID: {data['user']['id']}")
                return True
            else:
                self.log_result("Donor Registration", False, "Missing token or user data")
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
            self.log_result("Donor Registration", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        return False
    
    def test_login_functionality(self):
        """Test login for both roles"""
        print("\n🔐 Testing Login Functionality...")
        
        # Test hospital login
        hospital_login = {
            "email": "dr.sarah.johnson@cityhospital.com",
            "password": "SecurePass123!"
        }
        
        response = self.make_request('POST', '/login', hospital_login)
        if response and response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                self.log_result("Hospital Login", True, "Token received")
            else:
                self.log_result("Hospital Login", False, "No access token")
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
            self.log_result("Hospital Login", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        # Test donor login
        donor_login = {
            "email": "mike.chen@email.com",
            "password": "DonorPass456!"
        }
        
        response = self.make_request('POST', '/login', donor_login)
        if response and response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                self.log_result("Donor Login", True, "Token received")
            else:
                self.log_result("Donor Login", False, "No access token")
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
            self.log_result("Donor Login", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
    
    def test_user_info_endpoint(self):
        """Test /me endpoint for current user info"""
        print("\n👤 Testing User Info Endpoint...")
        
        # Test hospital user info
        if self.hospital_token:
            response = self.make_request('GET', '/me', token=self.hospital_token)
            if response and response.status_code == 200:
                data = response.json()
                if data.get('role') == 'hospital_staff':
                    self.log_result("Hospital User Info", True, f"Role: {data['role']}")
                else:
                    self.log_result("Hospital User Info", False, f"Wrong role: {data.get('role')}")
            else:
                error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
                self.log_result("Hospital User Info", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        # Test donor user info
        if self.donor_token:
            response = self.make_request('GET', '/me', token=self.donor_token)
            if response and response.status_code == 200:
                data = response.json()
                if data.get('role') == 'donor':
                    self.log_result("Donor User Info", True, f"Role: {data['role']}")
                else:
                    self.log_result("Donor User Info", False, f"Wrong role: {data.get('role')}")
            else:
                error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
                self.log_result("Donor User Info", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
    
    def test_blood_alert_creation(self):
        """Test blood alert creation by hospital staff"""
        print("\n🚨 Testing Blood Alert Creation...")
        
        if not self.hospital_token:
            self.log_result("Blood Alert Creation", False, "No hospital token available")
            return False
        
        alert_data = {
            "blood_type": "O+",
            "units_needed": 5,
            "urgency_level": "critical",
            "description": "Emergency surgery patient needs immediate O+ blood transfusion",
            "radius_km": 25
        }
        
        response = self.make_request('POST', '/alerts', alert_data, token=self.hospital_token)
        
        if response and response.status_code == 200:
            data = response.json()
            if 'id' in data and data.get('blood_type') == 'O+':
                self.test_alert_id = data['id']
                self.log_result("Blood Alert Creation", True, f"Alert ID: {data['id']}")
                return True
            else:
                self.log_result("Blood Alert Creation", False, "Missing alert ID or wrong blood type")
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
            self.log_result("Blood Alert Creation", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        return False
    
    def test_donor_cannot_create_alert(self):
        """Test that donors cannot create alerts"""
        print("\n🚫 Testing Donor Alert Creation Restriction...")
        
        if not self.donor_token:
            self.log_result("Donor Alert Restriction", False, "No donor token available")
            return
        
        alert_data = {
            "blood_type": "A+",
            "units_needed": 2,
            "urgency_level": "medium",
            "description": "Test alert",
            "radius_km": 10
        }
        
        response = self.make_request('POST', '/alerts', alert_data, token=self.donor_token)
        
        if response and response.status_code == 403:
            self.log_result("Donor Alert Restriction", True, "Correctly blocked donor from creating alert")
        else:
            self.log_result("Donor Alert Restriction", False, f"Expected 403, got {response.status_code if response else 'None'}")
    
    def test_alert_retrieval(self):
        """Test alert retrieval for both roles"""
        print("\n📋 Testing Alert Retrieval...")
        
        # Hospital staff should see their alerts
        if self.hospital_token:
            response = self.make_request('GET', '/alerts', token=self.hospital_token)
            if response and response.status_code == 200:
                alerts = response.json()
                if isinstance(alerts, list):
                    self.log_result("Hospital Alert Retrieval", True, f"Retrieved {len(alerts)} alerts")
                else:
                    self.log_result("Hospital Alert Retrieval", False, "Response is not a list")
            else:
                error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
                self.log_result("Hospital Alert Retrieval", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        # Donor should see matching alerts
        if self.donor_token:
            response = self.make_request('GET', '/alerts', token=self.donor_token)
            if response and response.status_code == 200:
                alerts = response.json()
                if isinstance(alerts, list):
                    self.log_result("Donor Alert Retrieval", True, f"Retrieved {len(alerts)} matching alerts")
                else:
                    self.log_result("Donor Alert Retrieval", False, "Response is not a list")
            else:
                error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
                self.log_result("Donor Alert Retrieval", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
    
    def test_alert_details(self):
        """Test getting specific alert details"""
        print("\n🔍 Testing Alert Details...")
        
        if not self.test_alert_id:
            self.log_result("Alert Details", False, "No test alert ID available")
            return
        
        # Test with hospital token
        if self.hospital_token:
            response = self.make_request('GET', f'/alerts/{self.test_alert_id}', token=self.hospital_token)
            if response and response.status_code == 200:
                alert = response.json()
                if alert.get('id') == self.test_alert_id:
                    self.log_result("Alert Details (Hospital)", True, f"Retrieved alert {self.test_alert_id}")
                else:
                    self.log_result("Alert Details (Hospital)", False, "Wrong alert ID returned")
            else:
                error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
                self.log_result("Alert Details (Hospital)", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        # Test with donor token
        if self.donor_token:
            response = self.make_request('GET', f'/alerts/{self.test_alert_id}', token=self.donor_token)
            if response and response.status_code == 200:
                alert = response.json()
                if alert.get('id') == self.test_alert_id:
                    self.log_result("Alert Details (Donor)", True, f"Retrieved alert {self.test_alert_id}")
                else:
                    self.log_result("Alert Details (Donor)", False, "Wrong alert ID returned")
            else:
                error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
                self.log_result("Alert Details (Donor)", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
    
    def test_donor_response(self):
        """Test donor responding to alerts"""
        print("\n💬 Testing Donor Response...")
        
        if not self.donor_token or not self.test_alert_id:
            self.log_result("Donor Response", False, "Missing donor token or alert ID")
            return
        
        response_data = {
            "response": "available",
            "message": "I'm available to donate immediately. Can be at the hospital within 30 minutes."
        }
        
        response = self.make_request('POST', f'/alerts/{self.test_alert_id}/respond', response_data, token=self.donor_token)
        
        if response and response.status_code == 200:
            data = response.json()
            if 'message' in data and 'response' in data:
                self.log_result("Donor Response", True, "Response recorded successfully")
            else:
                self.log_result("Donor Response", False, "Missing response data")
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
            self.log_result("Donor Response", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
    
    def test_duplicate_response_prevention(self):
        """Test that donors cannot respond twice to same alert"""
        print("\n🚫 Testing Duplicate Response Prevention...")
        
        if not self.donor_token or not self.test_alert_id:
            self.log_result("Duplicate Response Prevention", False, "Missing donor token or alert ID")
            return
        
        response_data = {
            "response": "not_available",
            "message": "Changed my mind"
        }
        
        response = self.make_request('POST', f'/alerts/{self.test_alert_id}/respond', response_data, token=self.donor_token)
        
        if response and response.status_code == 400:
            self.log_result("Duplicate Response Prevention", True, "Correctly prevented duplicate response")
        else:
            self.log_result("Duplicate Response Prevention", False, f"Expected 400, got {response.status_code if response else 'None'}")
    
    def test_hospital_view_responses(self):
        """Test hospital staff viewing responses to their alerts"""
        print("\n👥 Testing Hospital View Responses...")
        
        if not self.hospital_token or not self.test_alert_id:
            self.log_result("Hospital View Responses", False, "Missing hospital token or alert ID")
            return
        
        response = self.make_request('GET', f'/alerts/{self.test_alert_id}/responses', token=self.hospital_token)
        
        if response and response.status_code == 200:
            responses = response.json()
            if isinstance(responses, list):
                self.log_result("Hospital View Responses", True, f"Retrieved {len(responses)} responses")
            else:
                self.log_result("Hospital View Responses", False, "Response is not a list")
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
            self.log_result("Hospital View Responses", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
    
    def test_donor_response_email_inclusion(self):
        """Test that donor responses include both email and phone information"""
        print("\n📧 Testing Donor Response Email Inclusion...")
        
        if not self.hospital_token or not self.test_alert_id:
            self.log_result("Donor Response Email Inclusion", False, "Missing hospital token or alert ID")
            return
        
        response = self.make_request('GET', f'/alerts/{self.test_alert_id}/responses', token=self.hospital_token)
        
        if response and response.status_code == 200:
            responses = response.json()
            if isinstance(responses, list) and len(responses) > 0:
                # Check the first response for required fields
                donor_response = responses[0]
                required_fields = ['donor_email', 'donor_phone', 'donor_name', 'response']
                missing_fields = [field for field in required_fields if field not in donor_response]
                
                if not missing_fields:
                    # Verify the email matches our test donor
                    if donor_response.get('donor_email') == 'mike.chen@email.com':
                        self.log_result("Donor Response Email Inclusion", True, 
                                      f"Response includes email: {donor_response['donor_email']}, phone: {donor_response.get('donor_phone', 'N/A')}")
                    else:
                        self.log_result("Donor Response Email Inclusion", False, 
                                      f"Email mismatch. Expected: mike.chen@email.com, Got: {donor_response.get('donor_email')}")
                else:
                    self.log_result("Donor Response Email Inclusion", False, 
                                  f"Missing required fields: {missing_fields}")
            else:
                self.log_result("Donor Response Email Inclusion", False, "No responses found to verify email inclusion")
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
            self.log_result("Donor Response Email Inclusion", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
    
    def test_donor_cannot_view_responses(self):
        """Test that donors cannot view responses to alerts"""
        print("\n🚫 Testing Donor Response Access Restriction...")
        
        if not self.donor_token or not self.test_alert_id:
            self.log_result("Donor Response Access Restriction", False, "Missing donor token or alert ID")
            return
        
        response = self.make_request('GET', f'/alerts/{self.test_alert_id}/responses', token=self.donor_token)
        
        if response and response.status_code == 403:
            self.log_result("Donor Response Access Restriction", True, "Correctly blocked donor from viewing responses")
        else:
            self.log_result("Donor Response Access Restriction", False, f"Expected 403, got {response.status_code if response else 'None'}")
    
    def test_dashboard_stats(self):
        """Test dashboard statistics for both roles"""
        print("\n📊 Testing Dashboard Statistics...")
        
        # Hospital dashboard
        if self.hospital_token:
            response = self.make_request('GET', '/dashboard/stats', token=self.hospital_token)
            if response and response.status_code == 200:
                stats = response.json()
                required_fields = ['total_alerts', 'active_alerts', 'total_responses']
                if all(field in stats for field in required_fields):
                    self.log_result("Hospital Dashboard Stats", True, f"Stats: {stats}")
                else:
                    self.log_result("Hospital Dashboard Stats", False, f"Missing required fields. Got: {list(stats.keys())}")
            else:
                error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
                self.log_result("Hospital Dashboard Stats", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        # Donor dashboard
        if self.donor_token:
            response = self.make_request('GET', '/dashboard/stats', token=self.donor_token)
            if response and response.status_code == 200:
                stats = response.json()
                required_fields = ['total_responses', 'available_responses', 'active_alerts_for_blood_type']
                if all(field in stats for field in required_fields):
                    self.log_result("Donor Dashboard Stats", True, f"Stats: {stats}")
                else:
                    self.log_result("Donor Dashboard Stats", False, f"Missing required fields. Got: {list(stats.keys())}")
            else:
                error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
                self.log_result("Donor Dashboard Stats", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
    
    def test_mock_email_notifications(self):
        """Test mock email notification system"""
        print("\n📧 Testing Mock Email Notifications...")
        
        # Wait a moment for email notifications to be created
        time.sleep(2)
        
        # Donor should see their emails
        if self.donor_token:
            response = self.make_request('GET', '/mock-emails', token=self.donor_token)
            if response and response.status_code == 200:
                emails = response.json()
                if isinstance(emails, list):
                    self.log_result("Donor Mock Emails", True, f"Retrieved {len(emails)} mock emails")
                else:
                    self.log_result("Donor Mock Emails", False, "Response is not a list")
            else:
                error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
                self.log_result("Donor Mock Emails", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        
        # Hospital staff should see all emails
        if self.hospital_token:
            response = self.make_request('GET', '/mock-emails', token=self.hospital_token)
            if response and response.status_code == 200:
                emails = response.json()
                if isinstance(emails, list):
                    self.log_result("Hospital Mock Emails", True, f"Retrieved {len(emails)} mock emails")
                else:
                    self.log_result("Hospital Mock Emails", False, "Response is not a list")
            else:
                error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
                self.log_result("Hospital Mock Emails", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
    
    def test_authentication_required(self):
        """Test that endpoints require authentication"""
        print("\n🔒 Testing Authentication Requirements...")
        
        # Test endpoints without token
        endpoints_to_test = [
            ('/me', 'GET'),
            ('/alerts', 'GET'),
            ('/dashboard/stats', 'GET'),
            ('/mock-emails', 'GET')
        ]
        
        for endpoint, method in endpoints_to_test:
            response = self.make_request(method, endpoint)
            if response and response.status_code == 401:
                self.log_result(f"Auth Required {endpoint}", True, "Correctly requires authentication")
            else:
                self.log_result(f"Auth Required {endpoint}", False, f"Expected 401, got {response.status_code if response else 'None'}")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🩸 Starting Blood Donation System Backend Tests")
        print(f"🌐 Testing against: {API_BASE}")
        print("=" * 60)
        
        # Authentication tests
        if not self.test_hospital_registration():
            print("⚠️  Hospital registration failed, skipping dependent tests")
            return
        
        if not self.test_donor_registration():
            print("⚠️  Donor registration failed, skipping dependent tests")
            return
        
        self.test_login_functionality()
        self.test_user_info_endpoint()
        self.test_authentication_required()
        
        # Blood alert tests
        if self.test_blood_alert_creation():
            self.test_alert_retrieval()
            self.test_alert_details()
            self.test_donor_response()
            self.test_duplicate_response_prevention()
            self.test_hospital_view_responses()
            self.test_donor_response_email_inclusion()  # New test for email inclusion
            self.test_donor_cannot_view_responses()
        
        # Access control tests
        self.test_donor_cannot_create_alert()
        
        # Dashboard and notification tests
        self.test_dashboard_stats()
        self.test_mock_email_notifications()
        
        # Print final results
        print("\n" + "=" * 60)
        print("🏁 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Total: {self.results['passed'] + self.results['failed']}")
        
        if self.results['errors']:
            print("\n🚨 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed'])) * 100 if (self.results['passed'] + self.results['failed']) > 0 else 0
        print(f"\n🎯 Success Rate: {success_rate:.1f}%")
        
        return self.results

if __name__ == "__main__":
    tester = BloodDonationTester()
    results = tester.run_all_tests()