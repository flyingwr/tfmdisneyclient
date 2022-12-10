FROM nginx
COPY nginx.conf /etc/nginx/conf.d/nginx.conf

FROM python:3.11.1

WORKDIR /

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "server.py"]