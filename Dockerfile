########
# This image compile the dependencies
########
FROM arkhn/python-db-drivers:0.3.0 as compile-image

ENV VIRTUAL_ENV /srv/venv
ENV PATH "${VIRTUAL_ENV}/bin:${PATH}"
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
# poetry
ENV POETRY_VERSION=1.1.4
# make poetry create the virtual environment in the project's root
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
# do not ask any interactive question
ENV POETRY_NO_INTERACTION=1

WORKDIR /srv

RUN apt-get update \
    && ACCEPT_EULA=Y apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
    binutils \
    build-essential \
    # git is unfortunately required for company packages
    # that have not been published on pypi (yet)
    git nodejs npm \
    && apt-get autoremove --purge -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry
COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock
RUN poetry install --no-dev



########
# This image is the runtime
########
FROM arkhn/python-db-drivers:0.3.0 as runtime-image

ARG VERSION_SHA
ARG VERSION_NAME
ENV VERSION_SHA $VERSION_SHA
ENV VERSION_NAME $VERSION_NAME

ENV VIRTUAL_ENV /srv/.venv
ENV PYTHONPATH "${PYTHONPATH}:${VIRTUAL_ENV}/bin:/srv/jpyltime"
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /srv

RUN groupadd poetry
RUN useradd --no-log-init -g poetry poetry

RUN pip install poetry

# Copy venv with compiled dependencies
COPY --chown=poetry:poetry --from=compile-image /srv/.venv /srv/.venv
COPY --chown=poetry:poetry ["pyproject.toml", "docker-entrypoint.sh", "/srv/"]
COPY --chown=poetry:poetry jpyltime /srv/jpyltime
COPY --chown=poetry:poetry tests /srv/tests
RUN chmod +x docker-entrypoint.sh

USER poetry
EXPOSE 7000

ENTRYPOINT ["./docker-entrypoint.sh"]