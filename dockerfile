FROM python:3.9.18-bookworm
WORKDIR /tmp/app
COPY src/ /tmp/app/src
COPY pyproject.toml /tmp/app
RUN pip install .
CMD ["python3", "src/redmine_management/app/app.py"]