#!/usr/bin/env python3
# setup_trip_database.py
import sqlite3
import os

DB_FILE = "destinations.db"

# Delete the database file if it exists to ensure a clean start
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

# Connect to the SQLite database (this will create the file)
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Create the 'destinations' table
cursor.execute("""
CREATE TABLE destinations (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    type TEXT NOT NULL, -- e.g., 'Museum', 'Beach', 'Restaurant', 'Landmark'
    rating REAL NOT NULL, -- Rating out of 5
    average_cost INTEGER NOT NULL -- Estimated cost for a visit
);
""")

# Sample destination data
destinations_data = [
    ('Eiffel Tower', 'Paris', 'France', 'Landmark', 4.6, 25),
    ('Louvre Museum', 'Paris', 'France', 'Museum', 4.7, 17),
    ('Colosseum', 'Rome', 'Italy', 'Landmark', 4.7, 18),
    ('Trevi Fountain', 'Rome', 'Italy', 'Landmark', 4.8, 0),
    ('Vatican Museums', 'Rome', 'Italy', 'Museum', 4.6, 20),
    ('Statue of Liberty', 'New York', 'USA', 'Landmark', 4.7, 24),
    ('Central Park', 'New York', 'USA', 'Park', 4.8, 0),
    ('The MET', 'New York', 'USA', 'Museum', 4.8, 30),
    ('Senso-ji Temple', 'Tokyo', 'Japan', 'Landmark', 4.5, 0),
    ('Shibuya Crossing', 'Tokyo', 'Japan', 'Landmark', 4.4, 0),
    ('Ueno Park and Zoo', 'Tokyo', 'Japan', 'Park', 4.4, 5)
]

# Insert the data into the table
cursor.executemany("""
INSERT INTO destinations (name, city, country, type, rating, average_cost)
VALUES (?, ?, ?, ?, ?, ?);
""", destinations_data)

# Commit the changes and close the connection
conn.commit()
conn.close()

print(f"Database '{DB_FILE}' created and populated successfully.")
print(f"Absolute path: {os.path.abspath(DB_FILE)}")