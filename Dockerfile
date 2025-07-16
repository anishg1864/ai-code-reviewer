# --- Stage 1: Use an official Python runtime as a parent image ---
# We use the slim-bullseye version for a smaller image size
FROM python:3.11-slim-bullseye

# --- Set the working directory inside the container ---
WORKDIR /app

# --- Copy dependency files and install them ---
# This is done in a separate step to leverage Docker's layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Copy the rest of the application code into the container ---
COPY . .

# --- Expose the port the app runs on (for documentation) ---
EXPOSE 8080

# --- Define the command to run the application ---
# This is the command that will be executed when the container starts.
# We use this specific format to ensure the $PORT environment variable is correctly substituted by the shell.
CMD ["/bin/sh", "-c", "gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT main:app"]
