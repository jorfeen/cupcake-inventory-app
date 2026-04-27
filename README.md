# Cupcake Inventory Management System

A desktop inventory management application built with Python and Kivy, designed to help small businesses track, manage, and monitor inventory levels.

## Team

- Similoluwa Onimole (w10187267)
- Riad Benyamna (w10192777)
- Aadarsha Tiwari (w10194142)
- Mithila Jahan (w10192605)

**Course:** CSC 317 Foundations of Software Development  
**Instructor:** Chad McDaniel

---

## Technologies

| Technology | Version |
|------------|---------|
| Python     | 3.13.1  |
| Kivy       | 2.3.1   |

---

## Project Structure

```
cupcake_inventory_app/
├── main.py
├── database/
│   ├── __init__.py
│   └── db.py
└── screens/
    ├── __init__.py
    ├── dashboard.py / dashboard.kv
    ├── inventory.py / inventory.kv
    ├── item_details.py / item_details.kv
    ├── add_item.py / add_item.kv
    ├── reports.py / reports.kv
    └── settings.py / settings.kv
```

---

## How to Run

### 1. Clone the repository

```bash
git clone https://github.com/jorfeen/cupcake-inventory-app
cd cupcake_inventory_app
```

### 2. Install dependencies

```bash
pip install kivy==2.3.1
```

### 3. Run the application

```bash
python3 main.py
```

---

## Features

- **Dashboard** — Overview of total items, low stock alerts, inventory value, and recent activity
- **Inventory** — Searchable list of all inventory items, sortable by quantity or price with ascending/descending toggle
- **Item Details** — Full item info with transaction history, edit and delete (with confirmation)
- **Add Item** — Add new items or edit existing ones with input validation
- **Reports** — Generate filtered reports by summary, low stock, top quantity, or lowest quantity
- **Settings** — Toggle dark mode, set default stock threshold, reset all data (with confirmation)

## Known Limitations

- Dark mode toggle is stored but does not visually apply to the UI
- Inventory data resets when the application is closed