# Product Management System

A Django web application that takes product data collected by a Scrapy project
(exported as a CSV file), stores it in PostgreSQL, and gives  a clean web
interface to browse, filter, correct and remove those products.


## Features

**Data synchronisation (`python manage.py sync_db`)**
- Reads `data/scrapy_data.csv` using a project-relative path.
- Creates new products and updates changed ones, matched by `product_url`.
- Skips and reports invalid rows (missing title, bad price, invalid URL,
  duplicate URL in the file) instead of stopping the whole import.
- Cleans values: `£51.77` becomes `51.77`; `In stock (22 available)` becomes `True`.
- Runs inside one database transaction: if the database fails, nothing is saved.
- Prints a summary: created / updated / unchanged / skipped.

**Web interface**
- Responsive Bootstrap 5 product cards (image, title, price, availability, category, link).
- Pagination (12 products per page) that keeps your active filters.
- Left sidebar filters, styled like the Django admin: **By availability** and
  **By category**.
- Update page with a ModelForm, validation errors and success messages.
- Delete with a confirmation dialog, using POST only (CSRF protected).
- Image fallback when a product has no image or the link is broken.
- Empty states for "no products yet" and "no products match your filters".
- Light and dark theme that follows the system setting.
- Reusable footer, base layout and form partials.

**Admin site (`/admin/`)**
- Product list with search, and filters by availability and category.

## Tech stack

| Part | Technology |
|---|---|
| Language | Python 3.12+ |
| Framework | Django |
| Database | PostgreSQL 17 (Docker) |
| DB driver | psycopg 3 |
| Configuration | django-environ (`.env` file) |
| Frontend | Django templates + Bootstrap 5 (CDN) |

## How to run:

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/product-management-django.git
cd product-management-django
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

### 3. Install dependencies
```bash
uv sync
```

### 5. Configure environment variables
```bash
cp .env.example .env
```
Open `.env` and set a real `SECRET_KEY` and `DB_PASSWORD`.
Generate a secret key with:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

| Variable | Purpose | Example |
|---|---|---|
| `SECRET_KEY` | Django signing key (keep private) | long random string |
| `DEBUG` | Debug mode, `True` for development only | `True` |
| `ALLOWED_HOSTS` | Comma-separated hosts the app may serve | `127.0.0.1,localhost` |
| `DB_NAME` | PostgreSQL database name | `product_management` |
| `DB_USER` | PostgreSQL user | `product_user` |
| `DB_PASSWORD` | PostgreSQL password (keep private) | your own password |
| `DB_HOST` | Database host | `127.0.0.1` |
| `DB_PORT` | Database port | `5435` |


### 6. Apply migrations
```bash
uv run python manage.py migrate
```
(If you change `models.py` later, run `python manage.py makemigrations` first.)

### 7. Import the CSV data
```bash
uv run python manage.py sync_db
```

### 8. Run the tests
```bash
uv run python manage.py test
```


### 10. Start the development server
```bash
uv run python manage.py runserver
```
Open http://127.0.0.1:8000/products/

### 11. (Optional) Create an admin user
```bash
python manage.py createsuperuser
```
Then log in at http://127.0.0.1:8000/admin/

## Application endpoints

This is a server-rendered Django application. It returns HTML pages, not JSON.

| URL | Method | Description | Responses |
|---|---|---|---|
| `/` | GET | Redirects to the product list | 302 |
| `/products/` | GET | Paginated product list | 200 |
| `/products/<id>/update/` | GET | Show the update form for a product | 200, 404 if the id does not exist |
| `/products/<id>/update/` | POST | Validate and save changes, then redirect to the list | 302 on success, 200 with errors if invalid |
| `/products/<id>/delete/` | POST | Delete the product, then redirect to the list | 302, 404 if missing |
| `/products/<id>/delete/` | GET | Not allowed | 405 |
| `/admin/` | GET | Django admin site | 200 |

## Tests

`python manage.py test` covers:

- `sync_db`: runs twice without duplicates, updates a changed row instead of
  adding one, skips invalid rows.
- Views: list page loads, delete rejects GET with 405, delete with POST removes
  the product, an unknown product id returns 404.
- Pagination: correct page sizes, bad page numbers handled, filters kept when
  changing page.
- Filters: category and availability combine, unknown values are ignored,
  sidebar links keep the other active filters.

## License

Created as an  w3engineers internship assignment.