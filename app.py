from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///facts.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # Для flash-сообщений
db = SQLAlchemy(app)

# Модель данных
class Fact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False, unique=True)

@app.route('/')
def index():
    facts = Fact.query.all()  # Получаем все факты из базы данных
    return render_template('index.html', facts=facts)

@app.route('/add', methods=['GET', 'POST'])
def add_fact():
    if request.method == 'POST':
        new_fact = request.form.get('content')  # Получаем новый факт из формы
        if new_fact:
            # Проверяем, существует ли факт уже в базе данных
            existing_fact = Fact.query.filter_by(content=new_fact).first()
            if existing_fact:
                flash('Этот факт уже существует!', 'error')
            else:
                fact = Fact(content=new_fact)
                db.session.add(fact)
                db.session.commit()
                flash('Факт успешно добавлен!', 'success')
                return redirect(url_for('index'))
        else:
            flash('Факт не может быть пустым!', 'error')
    
    return render_template('add_fact.html')

@app.route('/edit/<int:fact_id>', methods=['GET', 'POST'])
def edit_fact(fact_id):
    fact = Fact.query.get_or_404(fact_id)  # Получаем факт по ID
    if request.method == 'POST':
        new_content = request.form.get('content')
        if new_content:
            existing_fact = Fact.query.filter_by(content=new_content).first()
            if existing_fact and existing_fact.id != fact_id:
                flash('Этот факт уже существует!', 'error')
            else:
                fact.content = new_content
                db.session.commit()
                flash('Факт успешно обновлен!', 'success')
                return redirect(url_for('index'))
    return render_template('edit_fact.html', fact=fact)

@app.route('/clear', methods=['POST'])
def clear_facts():
    db.session.query(Fact).delete()  # Очищаем таблицу фактов
    db.session.commit()
    flash('Все факты успешно очищены!', 'success')
    return redirect(url_for('index'))

# Обработчики ошибок
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создает базу данных при первом запуске
    app.run(debug=True)