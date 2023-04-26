FROM puckel/docker-airflow:1.10.9

COPY ./requirements.txt .

RUN python -m pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . /usr/local/airflow/
