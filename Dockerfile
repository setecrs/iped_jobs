FROM python:3.8-alpine

WORKDIR /app
COPY requirements.txt .
RUN python3 -m pip install waitress wheel -r requirements.txt
COPY . .
RUN python3 setup.py bdist_wheel
RUN python3 -m pip install /app/dist/*.whl

CMD ["waitress-serve", "--port=80", "--call", "iped_jobs:app.create_app"]

