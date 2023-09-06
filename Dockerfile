FROM python:3.10
WORKDIR /savel
COPY requirements.txt /savel/
RUN pip install -r requirements.txt
COPY . /savel
CMD python ./savel/savel.py