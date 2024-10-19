CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS activities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    cost VARCHAR(10) NOT NULL,
    season VARCHAR(20) NOT NULL,
    average_rating FLOAT DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS itineraries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    user_id INTEGER REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS itinerary_activities (
    itinerary_id INTEGER REFERENCES itineraries(id),
    activity_id INTEGER REFERENCES activities(id),
    PRIMARY KEY (itinerary_id, activity_id)
);

CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    rating INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(id),
    activity_id INTEGER REFERENCES activities(id)
);