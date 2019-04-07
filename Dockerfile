FROM frolvlad/alpine-python3

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

EXPOSE 4443

CMD ["python3", "proxy.py"]