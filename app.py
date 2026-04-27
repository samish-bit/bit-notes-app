from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Note
import os

app = Flask(__name__)

# --- Config ---
app.config['SECRET_KEY'] = 'bitnotes-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# --- Init extensions ---
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

# --- Helper ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# --- Routes ---
@app.route('/')
def home():
    total_notes = Note.query.count()
    total_users = User.query.count()
    recent_notes = Note.query.order_by(Note.uploaded_on.desc()).limit(3).all()
    return render_template('index.html', total_notes=total_notes,
                           total_users=total_users, recent_notes=recent_notes)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email    = request.form['email']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Email already registered.')

        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already taken.')

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login', success='Account created! Please login.'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    success_msg = request.args.get('success')

    if request.method == 'POST':
        email    = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            return render_template('login.html', error='Invalid email or password.')

        login_user(user)
        return redirect(url_for('home'))

    return render_template('login.html', success=success_msg)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        title       = request.form['title']
        subject     = request.form['subject']
        description = request.form['description']
        file        = request.files['file']

        # check a file was actually selected
        if file.filename == '':
            return render_template('upload.html', error='Please select a file.')

        # check file type is allowed
        if not allowed_file(file.filename):
            return render_template('upload.html', error='Only PDF, PNG, JPG files allowed.')

        # make filename safe and save it
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # save note details to database
        new_note = Note(
            title=title,
            subject=subject,
            description=description,
            filename=filename,
            user_id=current_user.id
        )
        db.session.add(new_note)
        db.session.commit()

        return redirect(url_for('browse'))

    return render_template('upload.html')


@app.route('/browse')
def browse():
    subject = request.args.get('subject', '')
    if subject:
        notes = Note.query.filter_by(subject=subject)\
                          .order_by(Note.uploaded_on.desc()).all()
    else:
        notes = Note.query.order_by(Note.uploaded_on.desc()).all()

    subjects = db.session.query(Note.subject).distinct().all()
    subjects = [s[0] for s in subjects]

    return render_template('browse.html', notes=notes,
                           subjects=subjects, selected=subject)

@app.route('/download/<int:note_id>')
def download(note_id):
    note = Note.query.get_or_404(note_id)
    return redirect(url_for('static', filename='uploads/' + note.filename))

@app.route('/delete/<int:note_id>', methods=['POST'])
@login_required
def delete(note_id):
    note = Note.query.get_or_404(note_id)

    # make sure only the uploader can delete it
    if note.user_id != current_user.id:
        return redirect(url_for('browse'))

    # delete the file from the uploads folder
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], note.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    # delete from database
    db.session.delete(note)
    db.session.commit()

    return redirect(url_for('browse'))

if __name__ == '__main__':
    app.run(debug=True)