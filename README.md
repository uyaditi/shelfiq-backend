# 🛒 ShelfIQ Backend

FastAPI backend for the ShelfIQ Retail Intelligence Dashboard — powering shelf analytics, inventory management, demand forecasting, and AI-driven retail decisions.

---

## 🗂 Project Structure

```
SHELFIQ-BACKEND/
├── app.py                  # FastAPI app entry point
├── db.py                   # Database connection & session config
├── models.py               # SQLAlchemy ORM models
├── schemas.py              # Pydantic request/response schemas
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not committed)
├── .gitignore
├── routes/
│   ├── chat.py             # AI Retail Copilot chat route
│   ├── rag.py              # RAG (Retrieval Augmented Generation) route
│   └── data.py             # CRUD routes for stock & customer data
└── services/
    └── bedrock.py          # AWS Bedrock AI service
```

---

## ⚙️ Setup & Installation

### 1. Clone the repo
```bash
git clone <your-repo-url>
cd shelfiq-backend
```

### 2. Create & activate virtual environment
```bash
python -m venv env

# Windows
env\Scripts\activate

# Mac/Linux
source env/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` file
```env
FRONTEND_URL=http://localhost:5173

# AWS RDS PostgreSQL
DB_HOST=retail-dashboard-db.cvwyeswgqozz.eu-north-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=postgres
DB_USER=AWS_AFB
DB_PASS=your_password_here
```

### 5. Run the server
```bash
uvicorn app:app --reload
```

Or alternatively:
```bash
python app.py
```

Server runs at: **`http://localhost:8000`**
Swagger docs at: **`http://localhost:8000/docs`**

---

## 🗄️ Database

- **Type:** PostgreSQL on AWS RDS
- **Region:** eu-north-1 (Stockholm)
- **Instance:** `retail-dashboard-db`
- **Tables:**
  - `retail_stock` — 1000 rows of shelf & product data
  - `retail_customer` — 1000 rows of transaction & customer data

---

## 📡 API Endpoints

### Health Check
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Server health status |

---

### 📦 Retail Stock

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/data/stock` | Get all stock records |
| GET | `/api/data/stock/{id}` | Get stock record by ID |
| POST | `/api/data/stock` | Create new stock record |
| PUT | `/api/data/stock/{id}` | Update stock record |
| DELETE | `/api/data/stock/{id}` | Delete stock record |

**Query Filters (GET /api/data/stock):**
- `?store=Store_A`
- `?category=Snacks`
- `?shelf_section=Middle`
- `?skip=0&limit=100`

**Sample POST Body:**
```json
{
  "date": "2026-02-28",
  "store": "Store_A",
  "product_name": "Shampoo",
  "category": "Personal Care",
  "price": 150.0,
  "cost": 100.0,
  "sales_qty": 10,
  "revenue": 1500.0,
  "roi_percent": 50.0,
  "remaining_stock": 90,
  "shelf_section": "Middle",
  "visibility_score": 0.85,
  "rating": 4.2,
  "product_id": "P0019"
}
```

---

### 🛒 Retail Customer

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/data/customer` | Get all customer records |
| GET | `/api/data/customer/{id}` | Get customer record by ID |
| POST | `/api/data/customer` | Create new customer record |
| PUT | `/api/data/customer/{id}` | Update customer record |
| DELETE | `/api/data/customer/{id}` | Delete customer record |

**Query Filters (GET /api/data/customer):**
- `?store=Store_A`
- `?customer_id=C001`
- `?skip=0&limit=100`

**Sample POST Body:**
```json
{
  "transaction_id": "T99999",
  "date": "2026-02-28",
  "store": "Store_A",
  "customer_id": "C001",
  "products": "Shampoo,Chips",
  "categories": "Personal Care,Snacks",
  "review_ratings": "4.2,3.8",
  "total_amount": 250.0,
  "product_ids": "P0019,P0008"
}
```

---

### 🤖 AI Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | AI Retail Copilot chat |
| POST | `/api/rag` | RAG-based document query |

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | FastAPI |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Database | PostgreSQL (AWS RDS) |
| AI | AWS Bedrock |
| Server | Uvicorn |
| Frontend | React (Vite) |

---

## 🚀 Deployment

> Backend is intended to be deployed on **AWS** (EC2 or Elastic Beanstalk) to maintain direct connectivity with RDS on port 5432.
> Local development may face port 5432 restrictions on corporate/ISP networks.

---

## 📌 Notes

- RDS is in `eu-north-1` (Stockholm) — ensure your deployment region matches
- SSL is required for all RDS connections (`sslmode=require`)
- Never commit `.env` to version control