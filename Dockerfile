# Use the official Python 3.10 image as the base.
FROM python:3.10

# Set the working directory in the container.
WORKDIR /app

# Install system dependencies needed for building Python packages (including distutils and venv support).
RUN apt-get update && \
    apt-get install -y python3-distutils python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Copy all project files into the container.
COPY . /app

# Create a virtual environment.
RUN python3 -m venv /opt/venv

# Set the PATH to use the virtual environment's executables.
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip, setuptools, and wheel.
RUN pip install --upgrade pip setuptools wheel

# Install Python dependencies from requirements.txt.
RUN pip install -r requirements.txt

# Expose the port that your app will run on.
EXPOSE 5000

# (Optional) Set a default PORT value. This ensures that if the deployment platform doesn't set it, it defaults to 5000.
ENV PORT 5000

# Copy the entrypoint script into the container and ensure it's executable.
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Use the entrypoint script to start your app.
CMD ["/app/entrypoint.sh"]
