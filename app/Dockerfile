# получаем image для нашего питона
FROM python:3.10

# обновляем  репозитории
RUN apt-get update -y && apt-get upgrade -y

# ставим локализацию
RUN apt-get install libpq-dev

# устанавливаем рабочую директорию
WORKDIR /app

# задаём переменные окружения, чтобы
# предотвратить ряд событий, а именно:
# создания .pyc файлов и использования
# питоном буффера для stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# ставим зависимости
RUN pip install --upgrade pip
COPY requirements/base.txt base.txt
COPY requirements/production.txt requirements.txt
RUN pip install -r requirements.txt

# копируем проект
COPY . .
