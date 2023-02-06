# Scan-Web

Сканирование документов на МФУ (принтер+сканер) от фирмы "HP" через веб интерфейс.

## Зачем?

Проблематика и подробное описание ситуации в статье
"[Сетевой принтер или сканер из обычного](https://www.alexgur.ru/articles/7107/)"

## Как оно работает?

Пользуетесь так:

- Подходите с мобильным телефоном или планшетом к сканеру.
- Открываете сайт сканера. Там жмете зелёную кнопку "Новое сканирование". Ждете.
- Скачиваете файл скана, который появится после завершения сканирования.

## Веб интерфейс

![interface](/interface.jpg)

## Технологии

- Flask (+waitress)
- Bash скрипт для запуска сканирования через утилиты в пакете hplip
- JQuery для интерактивности интерфейса

## Установка

Копирем файлы на сервер. Устанавливаем pip зависимости из файла requirements.txt через:

> pip install -r

Создаём файл в системе по адресу

> /etc/systemd/system/scan-web-server.service

Вставляем в него содержимое из файла *systemctl-service*. Но изменяем пути к
запускаемому веб серверу в директиве WorkingDirectory и ExecStart! Ещё не
забываем менять пользователя и группу, от лица которого запускается сервис.

Ставим на автозагрузку и запускаем:

```bash
systemctl enable scan-web-server
systemctl start scan-web-server
```

После чего можно заходить на сервер: *ip_сервера:8080*. Но если использовать
правила iptables из статьи, то можно заходить и просто на 80 порт.

## Лицензии

Проект содержит в себе сторонний код, который используется в работе сайта:

- [JQuery](https://jquery.com/) - небольшая JS библиотека, через которую легко добавлять интерактивность сайтам.
- [imagelightbox](https://github.com/marekdedic/imagelightbox) - просмотровщик изображений во всплывающем окне на сайте.

На данный момент (начало 2023) оба проекта с MIT лицензией.
