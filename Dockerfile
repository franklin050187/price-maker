# Use official Python image as the base image for building
FROM python:3.12-slim AS builder

# Install necessary build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        libc-dev \
        libffi-dev \
        libssl-dev \
        unzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Download the project source code from GitHub
ADD https://github.com/franklin050187/price-maker/archive/refs/heads/distroless.zip /app

# Unzip the downloaded file
RUN unzip distroless.zip && rm distroless.zip && mv price-maker-distroless price-maker

# Change the working directory to the project directory
WORKDIR /app/price-maker

# Install Python dependencies
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Use Distroless as the base image for the final stage
FROM gcr.io/distroless/python3-debian11

# Set the working directory in the container
WORKDIR /app

# Copy the application code from the builder stage
COPY --from=builder /app/price-maker /app

# Copy installed Python packages from the builder stage
COPY --from=builder /install /usr/local

# Expose port 8501
EXPOSE 8501

# Command to start the server
CMD ["streamlit", "run", "app.py"]
