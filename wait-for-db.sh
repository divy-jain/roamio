#!/bin/bash
# wait-for-db.sh

# This script waits for the database to be available before starting the Flask app.
# It checks the database connection by running `pg_isready`.

HOST=$1
PORT=$2
USER=$3
DBNAME=$4
CMD="${@:5}"  # The remaining arguments are the command to run (Flask app)

# Wait for PostgreSQL to become available
until pg_isready -h $HOST -p $PORT -U $USER -d $DBNAME; do
  echo "Waiting for PostgreSQL at $HOST:$PORT to become available..."
  sleep 2
done

echo "PostgreSQL is up and running. Starting Flask app..."

# Run the Flask app
exec $CMD
