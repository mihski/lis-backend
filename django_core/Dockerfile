# получаем image для нашего питона
FROM python:3.10

# устанавливаем рабочую директорию
WORKDIR /django_core

# задаём переменные окружения, чтобы
# предотвратить ряд событий, а именно:
# создания .pyc файлов и использования
# питоном буффера для stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# opencv для работы с аватарками персонажей
RUN apt-get update
RUN apt-get install python3-opencv -y

# ставим зависимости
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# копируем проект
COPY . .

CMD ["bash", "entrypoint.sh"]
