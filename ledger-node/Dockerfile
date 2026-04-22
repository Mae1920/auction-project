FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install flask
RUN pip install flask cryptography
CMD ["python", "ledger.py"]