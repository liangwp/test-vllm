FROM python:3.12-slim-bookworm

# Set standard environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Do not pin Debian packages. Packages in Debian stable distribution get
# updated only for major security or usability fixes.
RUN apt-get --yes update \
    && apt-get --yes --no-install-recommends install \
        curl ca-certificates dumb-init vim \
    && rm -rf /var/lib/apt/lists/*

# Create app user, create home directory for app user.
RUN groupadd --gid 3000 appuser \
    && useradd \
        --uid 3000 \
        --gid appuser \
        --shell /bin/bash \
        --create-home \
        --home /opt/app appuser

WORKDIR /opt/app

# Install uv
RUN curl -LsSf https://astral.sh/uv/0.6.14/install.sh | env UV_UNMANAGED_INSTALL="/opt/uv" sh
ENV PATH="/opt/uv:$PATH"

# Install project dependencies
COPY ./.python-version ./pyproject.toml ./uv.lock /opt/app/
RUN uv sync

# Copy project source code
RUN mkdir -p /opt/app/src
COPY ./src /opt/app/src

# Use the non-root user to run the app
USER appuser

# For convenience, add the `ll` alias for the interactive session when we
# docker exec into the container.
RUN echo 'alias ll="ls -alF"' >> ~/.bashrc

# Start the app with dumb-init
ENTRYPOINT ["dumb-init", "--"]
CMD ["uv", "run", "gunicorn", "--bind=0.0.0.0:8000", "--workers=2", "--chdir", "src", "main:server"]
