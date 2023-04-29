import sqlite3
import random
import string
import os
from hashlib import sha256
from flask import Flask, send_file, request, send_from_directory, make_response, render_template, redirect, Response

app = Flask(__name__, template_folder='templates')

promocodes = [
    "vFR1prugSGILYaKtGkqS",
    "OHzG4hlEz4bLsY420GpY",
    "P0KHHwTIQZuuYiWz9QWs",
    "NB3EPt4OHGF0BvLko0GT",
    "rFQLWHwJQSoPKKh59n7B",
    "GNSTyn8abD7jyF2oudmj",
    "2BcPIEBtBpgnKohit3ld",
    "mWX3rmU4ejtwveo007oR",
    "DC4lT09ClTNYDsmiFlJZ",
    "9RZCb7CLj6wm4o1D5Bw9",
    "HBHPZm7Q2BdSPk0tHZdN",
    "6OumzXZ0vno51bVpCw4Z",
    "3s9GCCygUAzBVrtUk1vD"
]

achievements_names = [
    "Get energized",
    "Clean Mission",
    "Recipe 007",
    "Everyone in a box",
    "Hand access",
    "Do you need a healthy lifestyle?",
    "Water blow",
    "Who doesn't smoke or drink...",
    "For shrimps",
    "Can I have some water?",
    "Rainbow prism",
    "Sounds like a toast",
    "Pig in a poke"
]

achievements_texts =[
    "Begin your morning right",
    "And how many life hacks did you know?",
    "Even a child can cook it",
    "Be trendy like Cheburashka",
    "You were allowed to wash your hands",
    "You made the desman laugh",
    "Surprise your body: drink water",
    "I do NOT smoke where I want!",
    "Straight back is the key to good health",
    "Of course, you need to!",
    "What is you favourite color?",
    "\"Comrades, to a healthy life!\"",
    "But its a cat!"
]

achievements_names_ru = [
    "Заряжайся",
    "Чистая миссия",
    "Рецепт 007",
    "Все в коробку",
    "Ручной доступ",
    "ЗОЖ ннадо?",
    "Водный удар",
    "Кто не курит и не пьёт...",
    "Для креветок",
    "Можно воды?",
    "Разноцветная призма",
    "Звучит как тост",
    "Кот в мешке!"
]

achievements_texts_ru =[
    "Начинай своё утро правильно",
    "А сколько лайфхаков знал ты?",
    "Сможет приготовить даже ребенок",
    "Будь в тренде, как Чебурашка",
    "Вам было разрешено мыть руки",
    "Вы насмешили выхухоль",
    "Удиви свой организм: папей воды",
    "НЕ курю, где хочу!",
    "Прямая спина — залог здоровья",
    "Конечно, нужно!",
    "Какой цвет твой любимый?",
    "\"Товарищи, за здоровую жизнь!\"",
    "Передай другому"
]

hrefs = [
    "/content/sport",
    "/content/hygiene_rules",
    "/content/recipe",
    "/content/cheburashka",
    "/content/access",
    "/content/desman",
    "/content/liver",
    "/content/rhyme",
    "/content/back",
    "/content/water_balance_ach",
    "/content/prism",
    "/content/comrade",
    "/content/cat"
]


def get_current_language():
    lang = request.cookies.get("lang")
    if lang not in ["en", "ru"]:
        lang = "ru"
    return lang


def choose_language(path):
    lang = get_current_language()
    if lang != "en":
        path += '_ru'
    return path


def get_achivements(qr_codes, lang):
    global achievements_texts, achievements_names, hrefs
    global achievements_texts_ru, achievements_names_ru, hrefs

    a_texts = achievements_texts
    a_names = achievements_names
    if lang == "ru":
        a_texts = achievements_texts_ru
        a_names = achievements_names_ru

    names = []
    texts = []
    styles = []
    for i in range(13):
        name = a_names[i]
        text = a_texts[i]
        style = ""
        if qr_codes[i] == '0':
            text = ""
            style = "filter:grayscale(1);"
        else:
            href = hrefs[i]
            name = f'<a href="{href}" class="t-card__link"> {name} </a>'
        names += [name]
        texts += [text]
        styles += [style]
    return names, texts, styles


def generate_salted_hash(salt, password):
    return sha256((salt + password).encode('utf-8')).hexdigest()


def get_connection_and_cursor():
    database_path = os.path.join(os.getcwd(), "database.db")
    conn = sqlite3.connect()
    cur = conn.cursor()
    return conn, cur


def apply_promocode(promocode, user_id, qr_codes):
    if promocode not in promocodes:
        return "Invalid QR code", None

    i = promocodes.index(promocode)

    qr_codes = list(qr_codes)
    qr_codes[i] = '1'
    qr_codes = ''.join(qr_codes)

    conn, cur = get_connection_and_cursor()
    cur.execute("UPDATE users SET qr_codes=? WHERE id=?", (qr_codes, user_id))
    conn.commit()

    redir = hrefs[i]
    return "Success!", redir

@app.route('/get-achievement')
def promocode():
    conn, cur = get_connection_and_cursor()
    promocode = request.args.get("promocode")
    if promocode is None:
        return redirect("/")

    session = request.cookies.get("session")

    cur.execute("SELECT id, qr_codes FROM users WHERE session=?", (session,))
    user_data = cur.fetchall()
    print(session)
    print(user_data)
    if session is None or len(user_data) != 1:
        return redirect(f"/login?promocode={promocode}")
    user_id, qr_codes = user_data[0]
    result, redir = apply_promocode(promocode, user_id, qr_codes)
    if result != "Success!":
        return result

    return redirect(redir)


@app.route('/cabinet')
def cabinet():
    conn, cur = get_connection_and_cursor()
    session = request.cookies.get("session")

    cur.execute("SELECT email, name, qr_codes, from_schoo21 FROM users WHERE session=?", (session,))
    user_data = cur.fetchall()
    print(session)
    print(user_data)
    if session is None or len(user_data) != 1:
        return redirect("/login")

    email, name, qr_codes, from_schoo21 = user_data[0]

    print([email, name, qr_codes, from_schoo21])

    # TODO MAKE CHECK SCHOOL21
    lang = get_current_language()
    achievements_names, achievements_texts, styles = get_achivements(qr_codes, lang)

    path = choose_language('cabinet')
    path += '.html'

    return make_response(render_template(path,
                                         name=name, email=email,
                                         styles = styles,
                                         achievements_names=achievements_names,
                                         achievements_texts=achievements_texts))


@app.route('/register', methods = ['GET', 'POST'])
def registration():
    error = ""

    if request.method == 'POST':
        res, session = user_registration(request)
        if res == "Success!":
            resp = make_response(redirect("/cabinet"))
            resp.set_cookie("session", session)
            return resp
        error = "Error: " + res

    path = choose_language('registration')
    path += '.html'

    resp = make_response(render_template(path, error=error))
    return resp


def user_registration(req):
    conn, cur = get_connection_and_cursor()
    email = req.form.get('Email')
    name = req.form.get('Name')
    password = req.form.get('Password')
    password2 = req.form.get('Password2')
    isYourSchool = (req.form.get('Your school') == 'yes')

    if password != password2:
        return "Passwords don't match", None

    cur.execute("SELECT * FROM users WHERE email=?", (email,))
    if len(cur.fetchall()) != 0:
        return "User with this email already exists", None

    salt = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    password_hash = generate_salted_hash(salt, password)
    qr_codes = "0"*13

    session = ''.join(random.choices(string.ascii_uppercase + string.digits, k=64))

    insert_query = """INSERT INTO users (email, name, salt, password_hash, qr_codes, from_schoo21, session)
    VALUES (?,?,?,?,?,?,?)"""
    cur.execute(insert_query, (email, name, salt, password_hash, qr_codes, isYourSchool, session))
    conn.commit()
    return "Success!", session


@app.route('/login', methods = ['GET', 'POST'])
def login():
    conn, cur = get_connection_and_cursor()
    promocode = request.args.get("promocode")
    error = ""

    session = request.cookies.get("session")
    cur.execute("SELECT email FROM users WHERE session=?", (session,))
    user_data = cur.fetchall()
    if session is not None and len(user_data) == 1:
        return redirect("/cabinet")

    if request.method == 'POST':
        promocode = request.form.get("promocode")
        res, session = user_login(request)
        if res == "Success!":
            to_redir = "/cabinet"
            if promocode is not None:
                to_redir = f"/get-achievement?promocode={promocode}"
            resp = make_response(redirect(to_redir))
            resp.set_cookie("session", session)
            return resp
        # TODO MAKE ERRORS IN RUSSIAN TOO
        error = "Error: " + res

    promocode_html = ""
    if promocode is not None:
        promocode_html = f"<input name=promocode value='{promocode}' style='display:none'>"

    path = choose_language('login')
    path += '.html'
    print(f'path={path}')
    resp = make_response(render_template(path, error=error, promocode_html=promocode_html))
    return resp


def user_login(req):
    conn, cur = get_connection_and_cursor()
    email = req.form.get('Email')
    password = req.form.get('Password')

    cur.execute("SELECT * FROM users WHERE email=? LIMIT 1", (email,))
    user = cur.fetchone()
    if user is None:
        return "Email or password is incorrect", None

    print(user)
    id, _, _, salt, password_hash, _, _, _ = user

    generated_hash = generate_salted_hash(salt, password)
    if password_hash != generated_hash:
        return "Email or password is incorrect", None

    session = ''.join(random.choices(string.ascii_uppercase + string.digits, k=64))

    insert_query = """UPDATE users SET session=? WHERE id=? """
    cur.execute(insert_query, (session, id))
    conn.commit()

    return "Success!", session


@app.route('/content/images/<path:path>')
def static_images(path):
    return send_from_directory("static/images", path)


@app.route('/content/css/<path:path>')
def static_css(path):
    return send_from_directory("static/css", path)


@app.route('/content/files/<path:path>')
def static_files(path):
    return send_from_directory("static/files", path)


@app.route('/content/js/<path:path>')
def static_js(path):
    return send_from_directory("static/js", path)


@app.route('/change-language/<lang>')
def change_lang(lang):
    to_redir = request.referrer
    if to_redir is None:
        to_redir = '/cabinet'

    if lang not in ["en", "ru"]:
        lang = "ru"

    resp = make_response(redirect(to_redir))
    resp.set_cookie("lang", lang)

    return resp


@app.route('/content/<path:path>')
def all_other_pages(path):
    path = choose_language(path)
    path += '.html'
    return render_template(path)


@app.route('/')
def main_page():
    path = choose_language('main')
    path += '.html'
    return render_template(path)


app.add_url_rule('/robots.txt', 'robots.txt', lambda: send_file('static/robots.txt'))
app.add_url_rule('/404.html', '404.html', lambda: send_file('static/404.html'))
app.add_url_rule('/sitemap.xml', 'sitemap.xml', lambda: send_file('static/sitemap.xml'))

app.add_url_rule('/images/<path:path>', 'images_pure', static_images)
app.add_url_rule('/files/<path:path>', 'files_pure', static_files)
app.add_url_rule('/css/<path:path>', 'css_pure', static_css)
app.add_url_rule('/js/<path:path>', 'js_pure', static_js)

if __name__ == '__main__':
    app.run()
