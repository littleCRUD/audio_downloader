FROM python:3.12

RUN mkdir /audio_downloader_bot

WORKDIR /audio_downloader_bot

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "main.py" ] -- bind=0.0.0.0:7000