# Use official Python image as the base image
FROM python:3.11 AS build-env

# Set the working directory in the container
WORKDIR /app

# Download the project source code from GitHub
ADD https://github.com/franklin050187/price-maker/archive/refs/heads/main.zip /app

# Unzip the downloaded file
RUN unzip main.zip && rm main.zip && mv price-maker-main price-maker

# Change the working directory to the project directory
WORKDIR /app/price-maker

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Switch to distroless image
FROM gcr.io/distroless/python3

COPY --from=build-env /app /app
COPY --from=build-env /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages

WORKDIR /app/price-maker

# Expose port 8501 (default Streamlit port)
EXPOSE 8501

# Command to start the server
ENTRYPOINT ["python", "-m", "streamlit", "run", "app.py"]