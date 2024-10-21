FROM python:3.9

WORKDIR /app

# Copy the application code
COPY . .

# Install the Flask-related dependencies
RUN pip install --no-cache-dir \
    flask \
    flask-sqlalchemy \
    flask-login \
    flask-wtf \
    psycopg2-binary


# Set the environment variables
ENV DATABASE_URL=postgresql://postgres:roamiopass@172.28.237.236:5432/roamio
ENV SECRET_KEY=your-secret-key

# Expose the port your application is running on
EXPOSE 5000

# Start the application
CMD ["flask", "run", "--host=0.0.0.0"]