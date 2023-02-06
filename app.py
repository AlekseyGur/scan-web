#!/usr/bin/env python
import os
import glob
import subprocess
import time
from flask import Flask
from flask import send_from_directory
from flask import url_for
from waitress import serve

config = {
    'port': os.environ.get('PORT', 8080),
    'debug': os.environ.get('DEBUG', True)
}

app = Flask(__name__)
dir_app = os.path.dirname(os.path.realpath(__file__))
dir_static = f'{dir_app}/static'
dir_scan = f'{dir_static}/scan'
file_is_scan = f'{dir_scan}/is_scan'
file_do_scan = f'{dir_app}/do_scan.sh'
app.config['UPLOAD_FOLDER'] = dir_static

if not os.path.exists(dir_static):
    os.makedirs(dir_static)
if not os.path.exists(dir_scan):
    os.makedirs(dir_scan)

if os.path.exists(dir_app):
    """Скрипт для запуска сканирования через командную строку"""
    rec = ''
    rec += "# Этот файл перезаписывается автоматически при старте веб сервера\n"
    # rec += f'file_name="{dir_scan}/$(date +%Y-%m-%d_%H:%M:%S).jpg"' + "\n" # У сервера нет батарейки - время не спасается!
    rec += f'file_name="{dir_scan}/$(( $(find {dir_scan}/ -name "*.jpg" | wc -l) + 1 )).jpg"' + "\n" # имя файла = кол-во сохранённых сканов jpg в папке + 1
    rec += '''device="$(hp-info -i 2>/dev/null | grep 'scan-uri' | awk '{print $NF}')"''' + "\n"
    rec += f'echo "1" > "{file_is_scan}"'
    rec += ' && '
    rec += 'hp-scan -i -d ${device} --output=${file_name} --res=300 --compression=jpg > /dev/null 2>&1'
    rec += ' && '
    rec += f'rm "{file_is_scan}" ' + "\n"
    with open(file_do_scan, 'w') as f:
        f.write(rec)


@app.route("/")
def hello():
    return fun_html(fun_scan_list())

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(dir_static,
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


# === API ===

@app.route("/api")
def api():
    return """
    /api/scan - Начать сканирование и сохранение файла
    <br>
    /api/is_scan - Сейчас сканирует? (1 - да, 0 - нет)
    <br>
    /api/rm_scan - Удалить метку 'сейчас сканирует'
    <br>
    /api/rm_files - Удалить ВСЕ сканированные сохранённые файлы
    <br>
    /api/files - Список сохранённых файлов
    """

@app.route("/api/scan")
def scan():
    """Начать сканирование и сохранение файла"""
    if not fun_is_scan(): # уже сканирует? если нет, то начинаем
        bashCommand = f"bash {file_do_scan}"
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        time.sleep(1)
        return "1"
    else:
        return "0"

@app.route("/api/is_scan")
def is_scan():
    """Сейчас сканирует"""
    return '1' if fun_is_scan() else '0'

@app.route("/api/rm_scan")
def rm_scan():
    """Удалить метку 'сейчас сканирует' """
    return '1' if fun_rm_scan() else '0'

@app.route("/api/rm_files")
def rm_files():
    """Удалить ВСЕ сканированные файлы"""
    return '1' if fun_rm_files() else '0'

@app.route("/api/files")
def list_files():
    """Список сохранённых файлов"""
    return fun_scan_list()




# === функции ===

def fun_scan_list():
    """Список сохранённых файлов"""
    files = []
    for i in sorted(glob.glob(f'{dir_scan}/*.jpg'), key=os.path.getmtime, reverse=True):
        m = i.split('/')
        files.append(f'/{m[-3]}/{m[-2]}/{m[-1]}')

    if files:
        td = [f'''<div class="file">
            <div><a href="{i}"><img src="{i}" height="100px"></a></div>
            <div>{i.split('/')[-1]}</div>
            <div><a href="{i}" download>(скачать)</a></div>
        </div>''' for i in files]

        return f"""
            <div>
                {''.join(td)}
            </div>
            <div class="btn red" onmouseup="RmFiles();">Удалить все файлы</div>
        """
    else:
        return "Нет сохранённых файлов"

def fun_is_scan():
    """Сейчас сканирует"""
    if os.path.isfile(file_is_scan):
        return True
    else:
        return False

def fun_rm_scan():
    """Удалить метку 'сейчас сканирует' """
    os.remove(file_is_scan)
    return True

def fun_set_scan():
    """Установить метку 'сейчас сканирует' """
    with open(file_is_scan, 'w') as f:
        f.write('1')
    return True

def fun_rm_files():
    """Удалить ВСЕ сканированные файлы"""
    files = []
    for i in glob.glob(f'{dir_scan}/*.jpg'):
        os.remove(i)
    time.sleep(1)
    return True

def fun_html(body):
    return f"""
        <!DOCTYPE html>
        <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <meta charset="UTF-8" http-equiv="Content-Type" content="text/html;" >
                <title>Сканирование</title>
                <link rel="stylesheet" href="/static/css/main.css">
                <link rel="stylesheet" href="/static/css/imagelightbox.css">
            </head>
            <body>
                <div class="header">
                    <div class="btn" onmouseup="NewScan();">Новое сканирование</div>
                    <div class="btn orange" onmouseup="ShowFiles();">Обновить список</div>
                </div>

                <div class="js_scanner_status"></div>

                <div class="js_scanner_files files">
                    {body}
                </div>

                <script src="/static/js/jq.js"></script>
                <script src="/static/js/imagelightbox.min.js"></script>
                <script src="/static/js/main.js"></script>
            </body>
        </html>"""


# === запуск приложения ===

if __name__ == "__main__":
    if fun_is_scan():
        fun_rm_scan()

    # app.run(host="0.0.0.0", port=config["port"], debug=config["debug"])
    serve(app, host='0.0.0.0', port=config["port"])
