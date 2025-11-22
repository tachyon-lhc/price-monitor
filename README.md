# Supermarket Price Tracker

Automated data pipeline for collecting and analyzing supermarket prices in Argentina. Built to demonstrate data engineering skills: web scraping, ETL processes, database design, and task automation.

## Overview

This project scrapes product prices from government and e-commerce sources, stores historical data in a relational database, and provides tools for price analysis. The system runs automatically on a daily schedule, accumulating data for temporal analysis and trend detection.

The main goal is to create a practical tool for tracking grocery costs while showcasing technical skills in data collection, processing, and storage.

## Key Features

- Automated daily scraping from Precios Claros API (Argentine government platform)
- Historical price storage with SQLite database
- Scheduled execution with APScheduler
- Basic basket cost calculation (tracking essential products)
- CSV backups for each scraping session
- Detailed execution logs
- Interactive data exploration tools

## Technical Stack

- Python 3.13
- SQLAlchemy (ORM and database operations)
- Requests (HTTP client for API calls)
- Pandas (data manipulation)
- APScheduler (task scheduling)
- SQLite (relational database)

## Architecture

The project follows a modular structure separating concerns:

```
price-monitor/
├── src/
│   ├── scrapers/          # Scraping modules (one per source)
│   │   └── precios_claros.py
│   ├── database/          # Data models and CRUD operations
│   │   ├── models.py
│   │   └── operations.py
│   └── utils/             # Shared utilities (paths, analysis)
├── scripts/
│   ├── run_pipeline.py    # Manual execution
│   ├── scheduler.py       # Automated scheduler
│   └── explorar_datos.py  # Interactive data exploration
├── config.py              # Centralized configuration
├── data/backups/          # CSV backups
├── logs/                  # Execution logs
└── price_monitor.db       # SQLite database
```

## Installation

```bash
# Clone repository
git clone https://github.com/your-username/supermarket-price-tracker.git
cd supermarket-price-tracker

# Install dependencies
pip install -r requirements.txt

# Run initial data collection
python scripts/run_pipeline.py
```

## Usage

### Manual execution

Run the data collection pipeline once:

```bash
python scripts/run_pipeline.py
```

### Automated scheduling

Start the scheduler for daily automatic execution:

```bash
python scripts/scheduler.py
```

The scheduler runs at 8:00 AM daily by default. Configuration can be modified in `scheduler.py`.

### Data exploration

Interactive CLI for exploring collected data:

```bash
python scripts/explorar_datos.py
```

## Database Schema

The main table stores product information:

```sql
CREATE TABLE productos (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    categoria VARCHAR(100),
    nombre VARCHAR(300),
    marca VARCHAR(100),
    precio FLOAT,
    precio_min FLOAT,
    precio_max FLOAT,
    presentacion VARCHAR(100),
    ean VARCHAR(50),
    sucursales_disponibles INTEGER,
    lat FLOAT,
    lng FLOAT
);
```

Indexes on `categoria`, `timestamp`, and `fuente` for optimized queries.

## Analysis Examples

### Basic basket cost

The system calculates the minimum cost for a basic grocery basket:

```
Productos en canasta (8 items):
  leche entera         | Casanto Leche Entera 3 Sachet      | $1525.00
  arroz blanco         | Arroz Gallo Oro 1kg                | $1200.00
  aceite girasol       | Aceite Cocinero 900ml              | $2150.00
  azucar               | Azucar Comun Ledesma 1kg           | $1300.00
  yerba mate           | Yerba Playadito 500g               | $1800.00
  pan lactal           | Pan Bimbo Blanco                   | $2100.00
  fideos               | Fideos Matarazzo 500g              | $950.00
  harina               | Harina 0000 Favorita 1kg           | $1100.00

COSTO TOTAL                                                | $12,125.00
```

### SQL queries for analysis

Price evolution over time:

```sql
SELECT
    DATE(timestamp) as fecha,
    AVG(precio) as precio_promedio
FROM productos
WHERE categoria = 'leche entera'
GROUP BY DATE(timestamp)
ORDER BY fecha DESC;
```

Compare prices across brands:

```sql
SELECT
    marca,
    COUNT(*) as productos,
    AVG(precio) as precio_promedio
FROM productos
WHERE categoria = 'arroz blanco'
GROUP BY marca
ORDER BY precio_promedio;
```

## Configuration

Product categories and search terms are defined in `config.py`:

```python
CATEGORIAS_PRODUCTOS = [
    'leche entera',
    'arroz blanco',
    'aceite girasol',
    # ...
]

COORDENADAS = {
    'CABA': {'lat': -34.6037, 'lng': -58.3816},
    'MAR_DEL_PLATA': {'lat': -38.0055, 'lng': -57.5426}
}
```

## Technical Decisions

**Why SQLite?**
Lightweight, serverless, and sufficient for this data volume. Easy to deploy and backup.

**Why modular structure?**
Separation of concerns allows independent testing of scrapers, database operations, and analysis tools. Easy to add new data sources.

**Why scheduled execution vs real-time?**
Supermarket prices don't change frequently. Daily scraping provides sufficient granularity for trend analysis while respecting API rate limits.

**Data quality approach:**
Specific search terms reduce noise. Price ceiling filter (< $50,000) removes incorrect matches (electronics, appliances). Post-scraping validation ensures data consistency.

## Lessons Learned

This project helped me develop:

- Web scraping techniques and API integration
- ETL pipeline design and implementation
- Relational database modeling and optimization
- Task automation with schedulers
- Exploratory data analysis workflows
- Clean code architecture and modularity
- Handling real-world messy data (cleaning, validation, filtering)

## Potential Improvements

- Add more data sources (other supermarket chains)
- Implement price change alerts (email/Telegram notifications)
- Build interactive dashboard with Streamlit
- Add unit tests for critical components
- Create REST API for external data access
- Implement data validation layer with Pydantic

## Contact

[Your Name]

- Email: <valentingonzalezdaumes@gmail.com>

## License

MIT License
