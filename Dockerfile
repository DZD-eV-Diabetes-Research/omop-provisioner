
# BACKEND BUILD AND RUN STAGE
FROM python:3.11
ARG BASEDIR=/opt/omop_provisioner
ARG VOCABDIR=/data/vocab

# prep dirs
RUN mkdir -p $BASEDIR
RUN mkdir -p $VOCABDIR
# Install Server
WORKDIR $BASEDIR

RUN python3 -m pip install --upgrade pip
RUN pip install -U pip-tools

# Generate requirements.txt based on depenencies defined in pyproject.toml
COPY pyproject.toml $BASEDIR/pyproject.toml
RUN pip-compile -o $BASEDIR/requirements.txt $BASEDIR/pyproject.toml

# Install requirements
RUN pip install -U -r $BASEDIR/requirements.txt

# install app
COPY omop_provisioner $BASEDIR

# copy .git folder to be able to generate version file
COPY .git $BASEDIR/.git
RUN echo "__version__ = '$(python -m setuptools_scm 2>/dev/null | tail -n 1)'" > $BASEDIR/__version__.py
# Remove git folder
RUN rm -r $BASEDIR/.git

# set base config

ENV SQL_DATABASE_URL="sqlite+aiosqlite:///$BASEDIR/data/medlog.db"
ENTRYPOINT ["python", "./main.py"]
#CMD [ "python", "./main.py" ]