FROM python:3.12-slim

# Create a non-root user to run the application
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /usr/src/app

# Install git and other dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        build-essential \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set proper permissions
RUN chown -R appuser:appuser /usr/src/app


# Add streamlit health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Expose the port that Streamlit runs on
EXPOSE 8501

# Switch to non-root user
USER appuser

# Start the Streamlit application
CMD ["sage-app"]