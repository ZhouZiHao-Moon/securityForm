from flask import *
import xlrd, xlwt, json
import time
from xlutils.copy import *

app = Flask(__name__)


def check(clas, grade, name, password):
    workbook = xlrd.open_workbook('static/users.xls')
    sheet1 = workbook.sheet_by_index(0)
    sheet2 = workbook.sheet_by_index(1)
    if sheet1.cell(int(clas), int(grade)).value != name:
        return '班主任与班级不一致'
    if sheet2.cell(int(clas), int(grade)).value != password:
        return '验证码错误'
    return 'success'


def check1(clas, grade, password):
    workbook = xlrd.open_workbook('static/users.xls')
    sheet1 = workbook.sheet_by_index(0)
    sheet2 = workbook.sheet_by_index(1)
    if sheet2.cell(int(clas), int(grade)).value != password:
        return 'fail'
    return sheet1.cell(int(clas), int(grade)).value


def get_index(name):
    workbook = xlrd.open_workbook('static/submit.xls')
    for i in range(0, len(workbook.sheets())):
        if workbook.sheet_by_index(i).name == name:
            return i


def getstring(text):
    text = text.replace("'", "“")
    text = text.replace("\"", "”")
    return text


def tograde(grade):
    if grade == 1:
        return '高一'
    if grade == 2:
        return '高二'
    if grade == 3:
        return '高三'


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/get/')
def get():
    workbook = xlrd.open_workbook('static/submit.xls')
    sheetname = time.strftime('%Y%m', time.localtime(time.time()))
    try:
        sheet = workbook.sheet_by_name(sheetname)
    except:
        newbook = copy(workbook)
        sheet = newbook.add_sheet(sheetname)
        for i in range(1, 4):
            for j in range(1, 21):
                sheet.write(j, i, 0)
        newbook.save('static/submit.xls')
        return '[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], ' \
               '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], ' \
               '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]'
    returndata = []
    for i in range(1, 4):
        grade = []
        for j in range(1, 21):
            grade.append(int(sheet.cell(j, i).value))
        returndata.append(grade)
    return str(returndata)


@app.route('/submit/<grade>/<clas>/', methods=['GET'])
def submit(grade, clas):
    filename = 'static/' + grade + '/' + clas + '/' + time.strftime('%Y%m', time.localtime(time.time())) + '.txt'
    try:
        file = open(filename, 'r', encoding='utf-8')
    except:
        return render_template('submit.html')
    data = json.loads(file.read().replace("'", "\""))
    file.close()
    return render_template('submit.html', **data)


@app.route('/submit/<grade>/<clas>/', methods=['POST'])
def submit_post(grade, clas):
    result = check(clas, grade, request.form.get('master'), request.form.get('password'))
    if result != 'success':
        return result
    filename = 'static/' + grade + '/' + clas + '/' + time.strftime('%Y%m', time.localtime(time.time())) + '.txt'
    file = open(filename, 'w', encoding='utf-8')
    data = {
        'master': getstring(request.form.get('master')),
        'week1': getstring(request.form.get('week1')),
        'week2': getstring(request.form.get('week2')),
        'week3': getstring(request.form.get('week3')),
        'week4': getstring(request.form.get('week4')),
        'danger': getstring(request.form.get('danger')),
        'action': getstring(request.form.get('action')),
        'accident': getstring(request.form.get('accident')),
        'password': getstring(request.form.get('password'))
    }
    file.write(str(data))
    file.close()
    workbook = xlrd.open_workbook('static/submit.xls')
    sheetname = time.strftime('%Y%m', time.localtime(time.time()))
    newbook = copy(workbook)
    sheet = newbook.get_sheet(get_index(sheetname))
    sheet.write(int(clas), int(grade), 1)
    newbook.save('static/submit.xls')
    return 'success'


@app.route('/check/', methods=['POST'])
def login():
    result = check1(request.form.get('class'), request.form.get('grade'), request.form.get('password'))
    return result


@app.route('/admin/', methods=['GET'])
def admin_get():
    return render_template('admin.html')


@app.route('/admin/', methods=['POST'])
def admin_post():
    file = open("static/adminpassword.txt", 'r', encoding='utf-8')
    if file.read() != request.form.get('password'):
        print(file.read(), request.form.get("password"))
        file.close()
        return "错误的管理员密码"
    file.close()
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = book.add_sheet(request.form.get('yearmonth'), cell_overwrite_ok=True)
    sheet.write(0, 0, '年级')
    sheet.write(0, 1, '班级')
    sheet.write(0, 2, '班主任')
    sheet.write(0, 3, '本月安全教育内容：第一周')
    sheet.write(0, 4, '本月安全教育内容：第二周')
    sheet.write(0, 5, '本月安全教育内容：第三周')
    sheet.write(0, 6, '本月安全教育内容：第四周')
    sheet.write(0, 7, '存在隐患')
    sheet.write(0, 8, '主要措施')
    sheet.write(0, 9, '安全事故')
    for grade in range(1, 4):
        for clas in range(1, 19):
            row = grade * 20 + clas - 20
            sheet.write(row, 0, tograde(grade))
            sheet.write(row, 1, clas)
            filename = 'static/' + str(grade) + '/' + str(clas) + '/' + request.form.get('yearmonth') + '.txt'
            try:
                file = open(filename, 'r', encoding='utf-8')
                data = json.loads(file.read().replace("'", "\""))
                sheet.write(row, 2, data['master'])
                sheet.write(row, 3, data['week1'])
                sheet.write(row, 4, data['week2'])
                sheet.write(row, 5, data['week3'])
                sheet.write(row, 6, data['week4'])
                sheet.write(row, 7, data['danger'])
                sheet.write(row, 8, data['action'])
                sheet.write(row, 9, data['accident'])
                file.close()
            except:
                pass
    book.save('static/excel/' + request.form.get('yearmonth') + '.xls')
    return send_from_directory('static/excel', request.form.get('yearmonth') + '.xls', as_attachment=True)


if __name__ == '__main__':
    app.run('0.0.0.0', 14250, threaded=True)
