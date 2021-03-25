########
# This image compiles the dependencies & is the runtime
########
FROM arkhn/python-db-drivers:0.3.0 as runtime-image

# version
ARG VERSION_SHA
ARG VERSION_NAME
ENV VERSION_SHA $VERSION_SHA
ENV VERSION_NAME $VERSION_NAME

# python
ENV PYTHONUNBUFFERED 1
# prevents python creating .pyc files
ENV PYTHONDONTWRITEBYTECODE 1

# poetry
ENV POETRY_VERSION=1.1.4
# make poetry install to this location
ENV POETRY_HOME="/srv/poetry"
# make poetry create the virtual environment in the project's root
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
# do not ask any interactive question
ENV POETRY_NO_INTERACTION=1

# paths
ENV PYSETUP_PATH="/srv/pysetup"
ENV VENV_PATH="/srv/pysetup/.venv"
# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

RUN apt-get update \
    && ACCEPT_EULA=Y apt-get upgrade -y \
    && apt-get install -y --no-install-recommends build-essential git nodejs npm \
    && apt-get autoremove --purge -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

# copy the project code
COPY . $PYSETUP_PATH

# install the dependencies
WORKDIR $PYSETUP_PATH
RUN poetry install --no-dev

# start the API
EXPOSE 7000
ENTRYPOINT ["./docker-entrypoint.sh"]
