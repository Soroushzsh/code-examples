FROM bitnami/python:3.12-debian-12

# Install Curl for HealthCheck
RUN apt update -y && apt install -y curl

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Change Container TimeZone To Tehran
ENV TZ="Asia/Tehran"
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY ./requirements.txt requirements.txt

# Install Project Requirements
RUN pip install --upgrade pip
#RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# Copy everything into /app dir
COPY . /app

CMD ["python", "consumer.py"]
