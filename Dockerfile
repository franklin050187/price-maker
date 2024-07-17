# Use debian:11-slim as the base image for building
FROM python:3.11-slim AS build

# Install necessary build dependencies and set up Python virtual environment
RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes \
        python3-venv \
        gcc \
        libpython3-dev \
        unzip \
        wget && \
    python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip setuptools wheel

# Download the project source code from GitHub
WORKDIR /app
RUN wget https://github.com/franklin050187/price-maker/archive/refs/heads/distroless.zip

# Unzip the downloaded file
RUN unzip distroless.zip && rm distroless.zip && mv price-maker-distroless price-maker

# Change the working directory to the project directory
WORKDIR /app/price-maker

# Install Python dependencies from the provided requirements.txt
RUN /venv/bin/pip install --disable-pip-version-check -r requirements.txt

# Manually clean up the virtual environment
RUN find /venv -type d -name "__pycache__" -exec rm -r {} + && \
    find /venv -type f -name "*.pyc" -exec rm -r {} + && \
    rm -rf /root/.cache/pip

# Use the build stage as the source for the virtual environment
FROM gcr.io/distroless/python3-debian11

# Copy the virtual environment from the build stage
COPY --from=build /venv /venv

# Copy the application code from the build stage
COPY --from=build /app/price-maker /app

# Set the working directory
WORKDIR /venv

# Expose port 8501 for Streamlit
EXPOSE 8501

# Set the entrypoint to run the Streamlit app
ENTRYPOINT ["/venv/bin/python3", "-m", "streamlit", "run", "/app/app.py"]
