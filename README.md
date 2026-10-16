# Fiesta Planner

Event planning and arrangement management system for a small business specializing in Mexican celebrations — quinceañeras, weddings, birthdays, and special events.

## Features

- **Catalog Management** — Browse and manage products/services: floral arrangements, balloon designs, centerpieces, table linens, silverware, and chair covers. Filter by category.
- **Catering Packages** — Food and beverage packages with per-person pricing and minimum guest requirements.
- **Client Management** — Track clients with contact info and notes.
- **Event Planning** — Create events, assign clients, set dates/venues/guest counts, track status (draft → confirmed → completed). Build event packages by adding catalog items and catering to each event.
- **Analytics** — Most requested items, revenue by event type, seasonal demand patterns, cost-vs-price margins.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, Vite 8, Axios |
| Backend | Flask 2.3, Flask-CORS |
| Database | SQLite 3 |
| Dev Tools | Concurrently (npm) |

## Project Structure

```
fiesta-planner/
├── frontend/                 # React application (Vite)
│   ├── src/
│   │   ├── App.jsx           # Tab navigation
│   │   ├── App.css           # Application styles
│   │   ├── main.jsx          # Entry point
│   │   ├── index.css         # Global styles
│   │   └── components/
│   │       ├── ClientList.jsx
│   │       ├── CatalogList.jsx
│   │       ├── CateringList.jsx
│   │       ├── EventList.jsx
│   │       └── Analytics.jsx
│   ├── package.json
│   └── vite.config.ts        # Proxy /api → Flask
├── backend/                  # Flask API
│   ├── src/
│   │   ├── app.py            # REST endpoints
│   │   └── db.py             # SQLiteDB class, schema, CRUD, analytics
│   ├── requirements.txt
│   └── .env.example
├── interface/                # Base classes (Process, Component, Page)
├── tests/
│   └── test_backend.py
├── start.bat                 # Launch both services (Windows)
├── start_backend.bat
├── start_frontend.bat
├── cleanup.bat
└── package.json              # Root scripts (concurrently)
```

## Prerequisites

- Python 3.8+
- Node.js 16+ and npm

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
copy .env.example .env       # Windows
# cp .env.example .env       # macOS/Linux
pip install -r requirements.txt
python src/app.py
```

Flask starts on `http://localhost:5000`. Demo data is seeded on first run.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

React dev server starts on `http://localhost:5173`. The Vite proxy forwards `/api/*` to Flask.

### 3. Or use batch scripts (Windows)

- `start.bat` — launches both backend and frontend in separate terminals
- `start_backend.bat` — backend only (creates venv if missing)
- `start_frontend.bat` — frontend only (installs deps if missing)
- `cleanup.bat` — kills all related processes and frees ports

## API Endpoints

### Clients
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/clients` | List all clients |
| GET | `/api/clients/:id` | Get one client |
| POST | `/api/clients` | Create client |
| PUT | `/api/clients/:id` | Update client |
| DELETE | `/api/clients/:id` | Delete client |

### Catalog Items
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/catalog` | List all (optional `?category=floral`) |
| GET | `/api/catalog/:id` | Get one item |
| POST | `/api/catalog` | Create item |
| PUT | `/api/catalog/:id` | Update item |
| DELETE | `/api/catalog/:id` | Delete item |

### Catering Packages
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/catering` | List all (optional `?type=food`) |
| GET | `/api/catering/:id` | Get one package |
| POST | `/api/catering` | Create package |
| PUT | `/api/catering/:id` | Update package |
| DELETE | `/api/catering/:id` | Delete package |

### Events
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/events` | List all events |
| GET | `/api/events/:id` | Get event with line items |
| POST | `/api/events` | Create event |
| PUT | `/api/events/:id` | Update event |
| DELETE | `/api/events/:id` | Delete event (cascades line items) |

### Event Line Items
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/events/:id/items` | List line items for event |
| POST | `/api/events/:id/items` | Add line item |
| DELETE | `/api/events/:id/items/:itemId` | Remove line item |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/top-items` | Most requested catalog items |
| GET | `/api/analytics/revenue` | Revenue by event type |
| GET | `/api/analytics/seasonal` | Event count and revenue by month |
| GET | `/api/analytics/margins` | Cost vs price margin per event |

## Database Schema

Five tables in SQLite (`backend/events.db`):

- **clients** — id, name, phone, email, notes, created_at
- **catalog_items** — id, name, category, description, unit_cost, unit_price, stock_qty, image_url, created_at
- **catering_packages** — id, name, type, description, price_per_person, min_guests, created_at
- **events** — id, client_id (FK), event_type, event_date, venue, guest_count, status, special_requirements, created_at
- **event_line_items** — id, event_id (FK), item_type, catalog_item_id (FK), catering_package_id (FK), quantity, unit_price_at_booking, subtotal

Categories: `floral`, `balloon`, `centerpiece`, `linen`, `silverware`, `chair_cover`
Event types: `quinceañera`, `wedding`, `birthday`, `special`
Statuses: `draft`, `confirmed`, `completed`, `cancelled`

## Demo Data

On first run, the database is seeded with:
- 5 clients
- 15 catalog items across 6 categories
- 7 catering packages (4 food, 3 beverage)
- 5 events with 22 line items

## Troubleshooting

- **Backend not starting** — Check Python version (`python --version`), ensure venv is activated, verify `.env` exists
- **Frontend can't reach backend** — Both must be running. Check Flask on `http://localhost:5000/api/health`
- **Empty JSON responses** — Restart the backend; SQLite connections must be created per-request
- **Port in use** — Run `cleanup.bat` to kill stale processes
