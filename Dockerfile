FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

EXPOSE 8000
COPY . /app

RUN python3 -m pip install --upgrade pip
RUN pip3 install -r ./requirements.txt

WORKDIR /app/ws_ums
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
