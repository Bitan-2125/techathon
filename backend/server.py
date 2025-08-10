from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import math

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create geospatial index for location-based queries
async def create_indexes():
    await db.users.create_index([("location", "2dsphere")])
    await db.blood_alerts.create_index([("created_at", 1)])

# JWT and Password setup
SECRET_KEY = os.environ.get('SECRET_KEY', 'blood-donation-secret-key-2025')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Pydantic Models
class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str  # "hospital_staff" or "donor"
    phone: Optional[str] = None
    # Hospital staff specific fields
    hospital_name: Optional[str] = None
    hospital_address: Optional[str] = None
    # Donor specific fields
    blood_type: Optional[str] = None  # A+, A-, B+, B-, AB+, AB-, O+, O-
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    last_donation_date: Optional[datetime] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: str
    role: str
    phone: Optional[str] = None
    hospital_name: Optional[str] = None
    hospital_address: Optional[str] = None
    blood_type: Optional[str] = None
    city: Optional[str] = None
    location: Optional[Dict[str, Any]] = None  # GeoJSON Point
    last_donation_date: Optional[datetime] = None
    is_available: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BloodAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    hospital_id: str
    hospital_name: str
    blood_type: str
    units_needed: int
    urgency_level: str  # "critical", "high", "medium"
    description: Optional[str] = None
    location: Dict[str, Any]  # GeoJSON Point
    radius_km: float = 50  # Search radius in kilometers
    status: str = "active"  # "active", "fulfilled", "cancelled"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

class BloodAlertCreate(BaseModel):
    blood_type: str
    units_needed: int
    urgency_level: str
    description: Optional[str] = None
    radius_km: float = 50

class DonorResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    alert_id: str
    donor_id: str
    donor_name: str
    donor_email: str
    donor_phone: Optional[str] = None
    response: str  # "available", "not_available"
    message: Optional[str] = None
    responded_at: datetime = Field(default_factory=datetime.utcnow)

class DonorResponseCreate(BaseModel):
    response: str
    message: Optional[str] = None

class MockEmailNotification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    to_email: str
    to_name: str
    subject: str
    body: str
    alert_id: str
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "sent"

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        user = await db.users.find_one({"email": email})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return User(**user)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    distance = R * c
    
    return distance

async def send_mock_email_notification(donor: User, alert: BloodAlert):
    """Mock email notification - stores email in database instead of sending"""
    email_notification = MockEmailNotification(
        to_email=donor.email,
        to_name=donor.name,
        subject=f"🩸 URGENT: {alert.blood_type} Blood Needed at {alert.hospital_name}",
        body=f"""
Dear {donor.name},

We urgently need your help! {alert.hospital_name} has requested {alert.units_needed} units of {alert.blood_type} blood.

Urgency Level: {alert.urgency_level.upper()}
Description: {alert.description or 'Emergency blood requirement'}

Your blood type matches and you are within the search radius. If you are available to donate, please respond as soon as possible.

To respond to this alert, please log in to the Blood Donation Portal.

Thank you for your willingness to save lives!

Best regards,
Blood Donation Alert System
        """,
        alert_id=alert.id
    )
    
    await db.email_notifications.insert_one(email_notification.dict())
    print(f"📧 Mock email sent to {donor.email} for alert {alert.id}")
    return email_notification

# Authentication Routes
@api_router.post("/register")
async def register(user_data: UserRegistration):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate role-specific fields
    if user_data.role == "hospital_staff":
        if not user_data.hospital_name:
            raise HTTPException(status_code=400, detail="Hospital name is required for hospital staff")
    elif user_data.role == "donor":
        if not user_data.blood_type or not user_data.city:
            raise HTTPException(status_code=400, detail="Blood type and city are required for donors")
    else:
        raise HTTPException(status_code=400, detail="Role must be 'hospital_staff' or 'donor'")
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user object
    user_dict = user_data.dict()
    user_dict["password"] = hashed_password
    user_dict["id"] = str(uuid.uuid4())
    user_dict["created_at"] = datetime.utcnow()
    user_dict["is_available"] = True
    
    # Add location for donors (simplified - using city coordinates)
    if user_data.role == "donor" and user_data.latitude and user_data.longitude:
        user_dict["location"] = {
            "type": "Point",
            "coordinates": [user_data.longitude, user_data.latitude]
        }
    
    await db.users.insert_one(user_dict)
    
    # Create and return access token
    access_token = create_access_token(data={"sub": user_data.email})
    return {"access_token": access_token, "token_type": "bearer", "user": User(**user_dict)}

@api_router.post("/login")
async def login(login_data: UserLogin):
    user = await db.users.find_one({"email": login_data.email})
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(data={"sub": login_data.email})
    return {"access_token": access_token, "token_type": "bearer", "user": User(**user)}

@api_router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# Blood Alert Routes
@api_router.post("/alerts", response_model=BloodAlert)
async def create_blood_alert(alert_data: BloodAlertCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != "hospital_staff":
        raise HTTPException(status_code=403, detail="Only hospital staff can create alerts")
    
    # Create alert
    alert = BloodAlert(
        hospital_id=current_user.id,
        hospital_name=current_user.hospital_name,
        blood_type=alert_data.blood_type,
        units_needed=alert_data.units_needed,
        urgency_level=alert_data.urgency_level,
        description=alert_data.description,
        radius_km=alert_data.radius_km,
        location={
            "type": "Point",
            "coordinates": [0, 0]  # Simplified for MVP
        }
    )
    
    # Set expiration based on urgency
    if alert_data.urgency_level == "critical":
        alert.expires_at = datetime.utcnow() + timedelta(hours=2)
    elif alert_data.urgency_level == "high":
        alert.expires_at = datetime.utcnow() + timedelta(hours=6)
    else:
        alert.expires_at = datetime.utcnow() + timedelta(hours=24)
    
    await db.blood_alerts.insert_one(alert.dict())
    
    # Find matching donors and send notifications
    await notify_matching_donors(alert)
    
    return alert

async def notify_matching_donors(alert: BloodAlert):
    """Find matching donors and send mock email notifications"""
    # Find donors with matching blood type who are available
    query = {
        "role": "donor",
        "blood_type": alert.blood_type,
        "is_available": True
    }
    
    # Check if donor donated recently (should wait at least 3 months)
    three_months_ago = datetime.utcnow() - timedelta(days=90)
    query["$or"] = [
        {"last_donation_date": {"$lt": three_months_ago}},
        {"last_donation_date": {"$exists": False}}
    ]
    
    matching_donors = await db.users.find(query).to_list(100)
    print(f"Found {len(matching_donors)} matching donors for {alert.blood_type}")
    
    # Send mock email notifications
    for donor_data in matching_donors:
        donor = User(**donor_data)
        await send_mock_email_notification(donor, alert)

@api_router.get("/alerts", response_model=List[BloodAlert])
async def get_blood_alerts(current_user: User = Depends(get_current_user)):
    if current_user.role == "hospital_staff":
        # Hospital staff see their own alerts
        alerts = await db.blood_alerts.find({"hospital_id": current_user.id}).sort("created_at", -1).to_list(100)
    else:
        # Donors see active alerts for their blood type
        alerts = await db.blood_alerts.find({
            "blood_type": current_user.blood_type,
            "status": "active"
        }).sort("created_at", -1).to_list(50)
    
    return [BloodAlert(**alert) for alert in alerts]

@api_router.get("/alerts/{alert_id}", response_model=BloodAlert)
async def get_alert_details(alert_id: str, current_user: User = Depends(get_current_user)):
    alert = await db.blood_alerts.find_one({"id": alert_id})
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return BloodAlert(**alert)

# Donor Response Routes
@api_router.post("/alerts/{alert_id}/respond")
async def respond_to_alert(alert_id: str, response_data: DonorResponseCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != "donor":
        raise HTTPException(status_code=403, detail="Only donors can respond to alerts")
    
    # Check if alert exists
    alert = await db.blood_alerts.find_one({"id": alert_id})
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Check if already responded
    existing_response = await db.donor_responses.find_one({
        "alert_id": alert_id,
        "donor_id": current_user.id
    })
    if existing_response:
        raise HTTPException(status_code=400, detail="You have already responded to this alert")
    
    # Create response
    response = DonorResponse(
        alert_id=alert_id,
        donor_id=current_user.id,
        donor_name=current_user.name,
        donor_email=current_user.email,
        donor_phone=current_user.phone,
        response=response_data.response,
        message=response_data.message
    )
    
    await db.donor_responses.insert_one(response.dict())
    
    # Update donor availability if they responded as available
    if response_data.response == "available":
        await db.users.update_one(
            {"id": current_user.id},
            {"$set": {"is_available": False, "last_donation_date": datetime.utcnow()}}
        )
    
    return {"message": "Response recorded successfully", "response": response}

@api_router.get("/alerts/{alert_id}/responses", response_model=List[DonorResponse])
async def get_alert_responses(alert_id: str, current_user: User = Depends(get_current_user)):
    # Only hospital staff can see responses to their alerts
    if current_user.role != "hospital_staff":
        raise HTTPException(status_code=403, detail="Access denied")
    
    alert = await db.blood_alerts.find_one({"id": alert_id, "hospital_id": current_user.id})
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found or access denied")
    
    responses = await db.donor_responses.find({"alert_id": alert_id}).sort("responded_at", -1).to_list(100)
    return [DonorResponse(**response) for response in responses]

# Dashboard Routes
@api_router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    if current_user.role == "hospital_staff":
        # Hospital dashboard stats
        total_alerts = await db.blood_alerts.count_documents({"hospital_id": current_user.id})
        active_alerts = await db.blood_alerts.count_documents({
            "hospital_id": current_user.id,
            "status": "active"
        })
        
        # Get response stats for hospital's alerts
        responses = await db.donor_responses.aggregate([
            {"$lookup": {
                "from": "blood_alerts",
                "localField": "alert_id",
                "foreignField": "id",
                "as": "alert"
            }},
            {"$match": {"alert.hospital_id": current_user.id}},
            {"$group": {
                "_id": "$response",
                "count": {"$sum": 1}
            }}
        ]).to_list(10)
        
        response_stats = {item["_id"]: item["count"] for item in responses}
        
        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "total_responses": sum(response_stats.values()),
            "available_responses": response_stats.get("available", 0),
            "not_available_responses": response_stats.get("not_available", 0)
        }
    else:
        # Donor dashboard stats
        total_responses = await db.donor_responses.count_documents({"donor_id": current_user.id})
        available_responses = await db.donor_responses.count_documents({
            "donor_id": current_user.id,
            "response": "available"
        })
        
        # Count active alerts for donor's blood type
        active_alerts = await db.blood_alerts.count_documents({
            "blood_type": current_user.blood_type,
            "status": "active"
        })
        
        return {
            "total_responses": total_responses,
            "available_responses": available_responses,
            "active_alerts_for_blood_type": active_alerts,
            "last_donation": current_user.last_donation_date.isoformat() if current_user.last_donation_date else None
        }

# Mock Email Routes (for testing)
@api_router.get("/mock-emails", response_model=List[MockEmailNotification])
async def get_mock_emails(current_user: User = Depends(get_current_user)):
    if current_user.role == "donor":
        emails = await db.email_notifications.find({"to_email": current_user.email}).sort("sent_at", -1).to_list(50)
    else:
        # Hospital staff can see emails sent for their alerts
        emails = await db.email_notifications.find().sort("sent_at", -1).to_list(100)
    
    return [MockEmailNotification(**email) for email in emails]

# Initialize database
@app.on_event("startup")
async def startup_event():
    await create_indexes()
    print("🩸 Blood Donation System Started!")
    print("📧 Using mock email notifications")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()