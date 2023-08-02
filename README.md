# Student Loan Disbursement Payout Dashboard

This web application simulates a payout dashboard for student loan disbursements. It allows users to upload an XML file containing multiple transactions, create entities, and perform payouts using the Method API. The dashboard also supports generating CSV reports once payments are complete. The application is built using React, FastAPI, and MongoDB.

## Prerequisites

Before running the application locally, you need to have the following installed and set up:

- [Node.js](https://nodejs.org/) - JavaScript runtime environment
- [Python](https://www.python.org/) - Python programming language (required for FastAPI)
- [MongoDB](https://www.mongodb.com/) - MongoDB database server
- [Method API Key](https://dashboard.methodfi.com/login/) - Get your API key from Method to enable transaction processing

## Installation

1. Clone the repository to your local machine:

```bash
git clone https://github.com/eladsisu/student-loan-payout-dashboard.git
cd payments
```

2. Install the frontend dependencies:

```bash
cd client
npm install
```

3. Install the backend dependencies:

```bash
cd backend
pip install -r requirements.txt
```

## Configuration

1. Set up MongoDB:

Make sure you have a running instance of MongoDB. Update the MongoDB connection details in the `backend/app/config.py` file if needed.

```python
MONGODB_URL = "mongodb://localhost:27017/"  # Change this to your MongoDB connection URL
```

2. Set up Method API Key:

Sign up for an account on [Method](https://dashboard.methodfi.com/login) and obtain your API key. Update the API key in the `backend/app/config.py` file.

```python
METHOD_API_KEY = "your-method-api-key"  # Replace this with your Method API key
```

## Running the Application

1. Start the backend FastAPI server:

```bash
cd backend
uvicorn app.main:app --reload
```

The FastAPI server will run at `http://localhost:8000`.

2. Start the frontend development server:

```bash
cd client
npm start
```

The frontend development server will run at `http://localhost:3000`.

3. Open your web browser and visit `http://localhost:3000` to access the Student Loan Disbursement Payout Dashboard.

## Usage

1. **Upload XML File:** Use the dashboard to upload an XML file containing multiple transactions. The application will parse the XML file and create entities for each transaction.
   see backend/employees.xml for example expected format.

2. **Payout Processing:** Use the Method API to perform payouts for the entities created from the XML file. The application will process the payouts and update the status accordingly.

3. **CSV Reports:** Once the payment process is complete, you can generate CSV reports for the payouts.

## Note

This project is just a poc, and not production ready.

Enjoy using the Student Loan Disbursement Payout Dashboard! If you encounter any issues or have any questions, please don't hesitate to reach out. Happy disbursement management!
