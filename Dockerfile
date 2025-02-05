# Use the official Python 3.10 image as the base image.
FROM python:3.10

# Set the working directory in the container.
WORKDIR /app

# Install system dependencies needed for building Python packages,
# including distutils and the virtual environment support.
RUN apt-get update && \
    apt-get install -y python3-distutils python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Copy all project files into the container.
COPY . /app

# Create a virtual environment.
RUN python3 -m venv /opt/venv

# Set the PATH to use the virtual environment's executables.
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and essential build tools.
RUN pip install --upgrade pip setuptools wheel

# Install Python dependencies from requirements.txt.
RUN pip install -r requirements.txt

# Expose the port (make sure this matches the default PORT if not provided).
EXPOSE 5000

# Set a default PORT value (if not provided externally).
ENV PORT 5000

# Copy the entrypoint script into the container (if not already copied).
# (Assuming entrypoint.sh is in the backend folder)
COPY entrypoint.sh /app/entrypoint.sh

# Ensure the entrypoint script is executable.
RUN chmod +x /app/entrypoint.sh

# Use the entrypoint script as the container's startup command.
CMD ["/app/entrypoint.sh"]
