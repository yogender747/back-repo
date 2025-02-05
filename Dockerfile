# Use the official Python 3.10 image as the base.
FROM python:3.10

# Set the working directory.
WORKDIR /app

# Install system dependencies (distutils and venv support).
RUN apt-get update && \
    apt-get install -y python3-distutils python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Copy all project files into the container.
COPY . /app

# Create a virtual environment.
RUN python3 -m venv /opt/venv

# Set the PATH to use the virtual environment’s executables.
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip, setuptools, and wheel.
RUN pip install --upgrade pip setuptools wheel

# Install Python dependencies.
RUN pip install -r requirements.txt

# Expose the port the app will listen on.
EXPOSE 5000

# (Optional) Set a default PORT if none is provided.
ENV PORT 5000

# Copy the entrypoint script into the container.
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Use the entrypoint script to start the app.
CMD ["/app/entrypoint.sh"]
