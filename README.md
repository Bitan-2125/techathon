# Real-Time Blood Shortage Alert and Donor Mobilization System

## Overview

This repository contains a prototype for an emergency blood donation web platform. The system is designed to optimize emergency response by connecting hospitals, blood banks, and potential blood donors in real-time. The main objective is to quickly address critical blood shortages by mobilizing eligible donors within a specific geographic area.

**Demo Video:**  
[Watch on YouTube](https://www.youtube.com/watch?v=o1wo_7QGuuA)

## Problem Statement

**Design and implement a software prototype for an emergency blood donation web platform.**

The system should:
- Allow hospitals and blood banks to raise real-time alerts for specific blood type shortages.
- Identify eligible past donors within a defined radius, using blood group, geolocation, and donation history.
- Notify eligible donors via SMS, email, or web push notifications.
- Provide a hospital-facing dashboard to:
  - Display current emergency requests.
  - Track donor responses.
  - Monitor blood inventory levels.
  - Enable coordination and unit sharing between hospitals.
- Ensure security, donor eligibility logic, and role-based access control.
- Simulate geolocation matching using MongoDB geospatial queries or coordinate-based logic.

## Features

- **Real-Time Alert System:** Hospitals and blood banks can trigger alerts for urgent blood type shortages.
- **Donor Matching:** 
  - Filters past donors by blood type, donation history, and proximity (geolocation).
  - Utilizes MongoDB geospatial queries for efficient matching (or coordinate logic as a fallback).
- **Hospital Dashboard:** 
  - View and manage emergency requests.
  - Track in-progress and fulfilled donations.
  - Monitor live blood inventory.
  - Coordinate with other hospitals for sharing blood units.
- **Security and Access Control:** 
  - Role-based access (donor, hospital staff, admin).
  - Data privacy for donor and hospital information.
  - Secure authentication and authorization.
- **Donor Eligibility Logic:** 
  - Ensures only eligible donors are notified (based on last donation date, health checks, etc.).

## Technologies Used

- **Backend:** Node.js / Express (suggested)
- **Database:** MongoDB (for donor, hospital, and inventory data; includes geospatial support)
- **Frontend:** React.js (suggested for dashboard and web app)
- **Notifications:** Integration with SMS/email APIs (e.g., Twilio, SendGrid)
- **Authentication:** JWT or OAuth2 (recommended)
- **Geospatial Matching:** MongoDB Geospatial Queries or custom coordinate logic

## Getting Started

### Prerequisites

- Node.js (>= 14.x)
- MongoDB (with geospatial support enabled)
- [Optional] Accounts for SMS/Email APIs (Twilio, SendGrid, etc.)

## Installation Guide

Follow these steps to set up the project on your local machine.

### Backend Installation

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Create a `.env` file inside the `backend` directory. Use `.env.example` as a reference for the required variables (e.g., database URI, API keys).
   
4. **Start the backend server:**
   ```bash
   uvicorn server:app --reload
   ```
   - The backend server should now be running (commonly on `http://localhost:5000` or as specified in your environment).

### Frontend Installation

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm i
   ```

3. **Set up environment variables:**
   - Create a `.env` file inside the `frontend` directory if needed (e.g., for API base URLs). Refer to any provided `.env.example` file for required variables.

4. **Start the frontend app:**
   ```bash
   npm start
   ```
   - The frontend app should be running (commonly on `http://localhost:3000`).

### Project Structure

```
/backend         # Server-side code (APIs, DB, logic)
/frontend        # Client-side code (React dashboard & app)
/docs            # Documentation and diagrams
.env.example     # Example environment config
README.md
```

## Usage

- **Hospitals/Blood Banks:** Log in to dashboard, raise alerts, monitor inventory, view donor responses, coordinate with other hospitals.
- **Donors:** Register and update profile, receive alerts, confirm donation intent, view donation history.

## Security

- All endpoints are protected via authentication and role-based authorization.
- Sensitive data is encrypted and access is restricted based on user roles.

## Contribution

Contributions are welcome! Please open issues or submit pull requests for improvements and bug fixes.

## License

This project is for educational and prototype purposes.

---

**Contact:**  
For questions or collaboration, reach out via GitHub Issues or contact the repository maintainer.
