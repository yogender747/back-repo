# Use the official Python 3.10 image as the base image.
FROM python:3.10

# Set the working directory in the container.
WORKDIR /app

# Install system dependencies needed for building Python packages,
# including distutils and the virtual environment support.
RUN apt-get update && \
    apt-get install -y python3-distutils python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Copy all files from your project into the container.
COPY . /app

# Create a virtual environment.
RUN python3 -m venv /opt/venv

# Set the PATH to use the virtual environment's executables.
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and essential build tools.
RUN pip install --upgrade pip setuptools wheel

# Install Python dependencies from requirements.txt.
RUN pip install -r requirements.txt

# Expose the port your Flask app will run on.
EXPOSE 5000

# Define the command to run your Flask app with gunicorn.
CMD sh -c "gunicorn -w 4 -b 0.0.0.0:${PORT:-5000} main:app"

