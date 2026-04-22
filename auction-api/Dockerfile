FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install flask requests
RUN pip install flask requests cryptography
CMD ["python", "app.py"]