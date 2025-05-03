# Use Railway's base image
FROM ghcr.io/railwayapp/nixpacks:ubuntu-1731369831

# Set the working directory
WORKDIR /app

# Update and install required dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    texlive-luatex \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    dvipng \
    texlive-science \
    poppler-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Ensure `python` points to `python3`
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Copy the application code to the container
COPY . /app/

# Set up Python environment and install dependencies
RUN python -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

# Add the virtual environment to PATH
ENV PATH="/opt/venv/bin:$PATH"

RUN python manage.py makemigrations && python manage.py migrate && python manage.py collectstatic --no-input

# Run migrations and collect static files
CMD gunicorn layoutGenerator.wsgi