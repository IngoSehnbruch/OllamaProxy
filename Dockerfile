# Use the official Python image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory content into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the application
CMD ["gunicorn", "-c", "gunicorn.conf.py", "ollamaproxy:app"]