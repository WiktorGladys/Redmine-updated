FROM python:3.9.18-bookworm
WORKDIR /tmp/app
COPY requirements.txt graph.txt /tmp/app/
RUN pip install -r requirements.txt
CMD ["pytest", "Initialized graph testing"]