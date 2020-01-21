FROM python:3.7-alpine AS base
ENV PYROOT /pyroot
ENV PYTHONUSERBASE $PYROOT

WORKDIR /opt/blackcat
COPY blackcat ./blackcat
COPY config.example.yml ./
# Make an empty config file if one doesn't exist.
RUN touch /opt/blackcat/config.yml

# I commented this out because it would create security risks
# if images were built/published with legitimate configs included.
# If config is empty, replace with example config, else remove example config.
#RUN if [ ! -s '/opt/blackcat/config.yml' ]; then  mv -f /opt/blackcat/config.example.yml /opt/blackcat/config.yml;\
# else  rm -f /opt/blackcat/config.example.yml; \
#fi
RUN mv -f /opt/blackcat/config.example.yml /opt/blackcat/config.yml

FROM base as builder
COPY Pipfile* ./
RUN pip install pipenv
RUN pipenv install --python 3.7
RUN PIP_USER=1 PIP_IGNORE_INSTALLED=1 pipenv install --system --deploy --ignore-pipfile
COPY setup.py ./
RUN python3 setup.py install

FROM base
COPY --from=builder $PYROOT/lib $PYROOT/lib

RUN addgroup -S usergroup && adduser -S blackcat -G usergroup
USER blackcat
ENTRYPOINT ["python", "blackcat/main.py"]