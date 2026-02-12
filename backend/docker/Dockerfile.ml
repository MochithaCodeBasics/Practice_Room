# Machine Learning
FROM practice-room-python:latest

USER root
COPY docker/requirements/ml.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

USER runner
