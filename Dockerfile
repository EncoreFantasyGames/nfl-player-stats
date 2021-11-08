FROM python:3.6

COPY . .

RUN ls
RUN pip install -r requirements.txt

CMD [ "python", "main.py"]

