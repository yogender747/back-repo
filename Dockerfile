# Use the official Python 3.10 image.
FROM python:3.10

# Set the working directory in the container.
WORKDIR /app

# Install system dependencies (including distutils and venv support).
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

# Install Python dependencies.
RUN pip install -r requirements.txt

# Expose port 5000 (this is the container's listening port).
EXPOSE 5000

# (Optional) Set a default PORT if none is provided by the environment.
ENV PORT 5000

# Copy the entrypoint script and make it executable.
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Use the entrypoint script as the container's startup command.
CMD ["/app/entrypoint.sh"]
