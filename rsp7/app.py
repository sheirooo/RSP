from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_socketio import SocketIO, join_room, emit
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from bs4 import BeautifulSoup
import re
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///collab.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, async_mode='gevent', cors_allowed_origins="*")

# ==================== МОДЕЛИ ====================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), default='Без названия')
    content = db.Column(db.Text, default='')

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    level = db.Column(db.String(20), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    position = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()

# ==================== ВСПОМОГАТЕЛЬНЫЕ ====================
def get_access_level(user_id, doc_id):
    if not user_id:
        return None
    perm = Permission.query.filter_by(user_id=user_id, document_id=doc_id).first()
    if perm:
        return perm.level
    doc = Document.query.get(doc_id)
    return 'edit' if doc and doc.owner_id == user_id else None

# ==================== ПАРСИНГ ====================
def parse_habr_search(query):
    url = f"https://habr.com/ru/search/?q={query}&target_type=posts&order=relevance"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
    except requests.RequestException as e:
        return f"Ошибка подключения к Habr: {e}"

    soup = BeautifulSoup(r.text, 'html.parser')
    articles = soup.find_all('article', class_='tm-articles-list__item')[:5]
    result = []
    for a in articles:
        title_tag = a.find('a', class_='tm-title__link')
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        link = "https://habr.com" + title_tag['href']
        time_tag = a.find('time')
        date = time_tag['datetime'][:10] if time_tag else "—"
        result.append(f"• [{date}] {title}\n  {link}")
    return "\n\n".join(result) if result else "Ничего не найдено."

# ==================== РОУТЫ ====================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Пользователь уже существует')
            return redirect(url_for('register'))
        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash('Регистрация успешна!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('index'))
        flash('Неверный логин или пароль')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    owned = Document.query.filter_by(owner_id=user_id).all()
    shared = db.session.query(Document).join(Permission).filter(Permission.user_id == user_id).all()
    all_docs = {d.id: d for d in owned + shared}.values()

    docs = []
    for doc in all_docs:
        level = get_access_level(user_id, doc.id)
        is_owner = doc.owner_id == user_id
        docs.append({'id': doc.id, 'title': doc.title, 'is_owner': is_owner, 'access_level': level or 'edit'})
    return render_template('index.html', docs=docs)

@app.route('/create_doc', methods=['POST'])
def create_doc():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    doc = Document(owner_id=session['user_id'], title="Новый документ")
    db.session.add(doc)
    db.session.flush()
    db.session.add(Permission(user_id=session['user_id'], document_id=doc.id, level='edit'))
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/doc/<int:doc_id>')
def doc(doc_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    document = Document.query.get_or_404(doc_id)
    level = get_access_level(session['user_id'], doc_id)
    if not level:
        flash('Доступ запрещён')
        return redirect(url_for('index'))
    is_owner = document.owner_id == session['user_id']
    return render_template('doc.html', doc=document, doc_id=doc_id, level=level, is_owner=is_owner)

@app.route('/parse', methods=['POST'])
def parse():
    if 'user_id' not in session:
        return jsonify({'error': 'Не авторизован'}), 401
    doc_id = int(request.form['doc_id'])
    query = request.form['query'].strip()
    if not query:
        return jsonify({'error': 'Введите запрос'}), 400

    doc = Document.query.get(doc_id)
    if not doc or doc.owner_id != session['user_id']:
        return jsonify({'error': 'Нет прав на этот документ'}), 403

    result = parse_habr_search(query)

    separator = "\n\n" + "="*60 + f"\nПАРСИНГ: {query.upper()} ({request.remote_addr})\n" + "="*60 + "\n\n"
    doc.content += separator + result
    db.session.commit()

    safe_name = re.sub(r'[^\w\-]', '_', query)[:50]
    filename = f"parse_{doc_id}_{safe_name}.txt"
    os.makedirs("static/downloads", exist_ok=True)
    with open(os.path.join("static/downloads", filename), "w", encoding="utf-8") as f:
        f.write(result)

    socketio.emit('update_text', {'content': doc.content}, room=str(doc_id))

    return jsonify({
        'success': True,
        'filename': filename,
        'content': doc.content
    })

@app.route('/share/<int:doc_id>', methods=['POST'])
def share(doc_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    doc = Document.query.get_or_404(doc_id)
    if doc.owner_id != session['user_id']:
        flash('Только владелец может делиться')
        return redirect(url_for('doc', doc_id=doc_id))
    username = request.form['username'].strip()
    level = request.form['level']
    target = User.query.filter_by(username=username).first()
    if not target:
        flash('Пользователь не найден')
        return redirect(url_for('doc', doc_id=doc_id))
    perm = Permission.query.filter_by(user_id=target.id, document_id=doc_id).first()
    if perm:
        perm.level = level
    else:
        db.session.add(Permission(user_id=target.id, document_id=doc_id, level=level))
    db.session.commit()
    flash(f'Доступ предоставлен: {username} — {level}')
    return redirect(url_for('doc', doc_id=doc_id))

@app.route('/delete_doc/<int:doc_id>', methods=['POST'])
def delete_doc(doc_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    doc = Document.query.get(doc_id)
    if doc and doc.owner_id == session['user_id']:
        Permission.query.filter_by(document_id=doc_id).delete()
        Comment.query.filter_by(document_id=doc_id).delete()
        db.session.delete(doc)
        db.session.commit()
        flash('Документ удалён')
    return redirect(url_for('index'))

# ==================== SOCKETIO ====================
@socketio.on('join')
def on_join(data):
    doc_id = data['doc_id']
    user_id = session.get('user_id')
    if user_id and get_access_level(user_id, doc_id):
        join_room(str(doc_id))
        doc = Document.query.get(doc_id)
        comments = Comment.query.filter_by(document_id=doc_id).all()
        emit('init', {
            'content': doc.content,
            'comments': [{'user': User.query.get(c.user_id).username, 'text': c.text, 'position': c.position} for c in comments]
        })

@socketio.on('edit')
def on_edit(data):
    if session.get('user_id') and get_access_level(session['user_id'], data['doc_id']) == 'edit':
        doc = Document.query.get(data['doc_id'])
        if doc:
            doc.content = data['content']
            db.session.commit()
            emit('update_text', {'content': data['content']}, room=str(data['doc_id']))

@socketio.on('add_comment')
def on_add_comment(data):
    level = get_access_level(session.get('user_id'), data['doc_id'])
    if level in ('comment', 'edit'):
        c = Comment(document_id=data['doc_id'], user_id=session['user_id'], text=data['text'], position=data['position'])
        db.session.add(c)
        db.session.commit()
        emit('new_comment', {
            'user': session['username'],
            'text': data['text'],
            'position': data['position']
        }, room=str(data['doc_id']))

if __name__ == '__main__':
    os.makedirs("static/downloads", exist_ok=True)
    socketio.run(app, host='0.0.0.0', port=5000)