FROM python:3.12.4-slim-bookworm

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Create the uploads directory
RUN mkdir -p /app/uploads

RUN mkdir -p /tmp

# Set the environment variable for Flask
ENV FLASK_APP=wsgi.py

# Expose port 8080
EXPOSE 8080

# Run the application with Gunicorn without timeout, so that the application can run indefinitely without being killed after 30
CMD ["gunicorn", "-b", "0.0.0.0:8080", "--workers", "1", "--threads", "1", "--timeout", "0", "wsgi:application"]
