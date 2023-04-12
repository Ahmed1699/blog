from flask import Flask, render_template, redirect, url_for, flash ,abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm,RegisterForm,LoginForm,CommentForm
from flask_gravatar import Gravatar
from functools import wraps
import os 
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.app_context().push()

csrf=CSRFProtect(app)

app.config['SECRET_KEY'] =os.environ.get("SECRET_KEY") 
ckeditor = CKEditor(app)
Bootstrap(app)

gravatar=Gravatar(app,size=100,rating='g',default='retro',force_default=False, force_lower=False, use_ssl=False, base_url=None)

login_manager=LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CONFIGURE TABLES
class User(db.Model,UserMixin):
    __tablename__="users"
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(250), nullable=False)
    email=db.Column(db.String(250), nullable=False,unique=True)
    password=db.Column(db.String(250), nullable=False)
    posts=relationship("BlogPost",back_populates="author")
    comments=relationship("Comment",back_populates="comment_author")


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)

    author_id=db.Column(db.Integer,db.ForeignKey("users.id")) 
    author =relationship("User",back_populates="posts")

    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    comments=relationship("Comment",back_populates="comment_post")

  
class Comment(db.Model):
    __tablename__="comments"
    id = db.Column(db.Integer, primary_key=True)
    comment=db.Column(db.Text,nullable=False)

    author_id=db.Column(db.Integer,db.ForeignKey("users.id")) 
    comment_author=relationship('User',back_populates="comments")

    post_id=db.Column(db.Integer,db.ForeignKey("blog_posts.id")) 
    comment_post=relationship('BlogPost',back_populates="comments")


db.create_all()

def just_admins(func):
    @wraps(func)
    def wrap(*args,**kw):
        if current_user.id!=1:
            return abort(403)
        return func(*args,**kw)
    return wrap


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts,logged_in=current_user.is_authenticated)


@app.route('/register',methods=["POST","GET"])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        name=form.name.data
        email=form.email.data
        password=form.password.data
        user=User.query.filter_by(email=email).first()
        if user:
            flash('this email already signed up!')
            return redirect(url_for('login'))
        hash_pass=generate_password_hash(password,"pbkdf2:sha256",8)
        new_u=User(name=name,email=email,password=hash_pass)
        db.session.add(new_u)
        db.session.commit()

        login_user(new_u)
        return redirect(url_for('get_all_posts'))

    return render_template("register.html",form=form,logged_in=current_user.is_authenticated)


@app.route('/login',methods=["POST","GET"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        email=form.email.data
        password=form.password.data
        user=User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password,password):
                login_user(user)
                return redirect(url_for('get_all_posts'))
            else:
                flash("rong password")
                return redirect(url_for('login'))
        else:
            flash("email not exist")
            return redirect(url_for('login'))

    return render_template("login.html",form=form,logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>",methods=["POST","GET"])
def show_post(post_id):
    com_form=CommentForm()
    requested_post = BlogPost.query.get(post_id)
    if com_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("you need to login")
            return redirect(url_for('login'))
        new_com=Comment(
            comment=com_form.comment_text.data,
            comment_author=current_user ,
            comment_post=requested_post )
        db.session.add(new_com)
        db.session.commit()
    return render_template("post.html",form=com_form ,post=requested_post,logged_in=current_user.is_authenticated)


@app.route("/about")
def about():
    return render_template("about.html",logged_in=current_user.is_authenticated)


@app.route("/contact")
def contact():
    return render_template("contact.html",logged_in=current_user.is_authenticated)


@app.route("/new-post",methods=['POST','GET'])
@login_required
@just_admins
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form,logged_in=current_user.is_authenticated)


@app.route("/edit-post/<int:post_id>")
@login_required
@just_admins
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form,logged_in=current_user.is_authenticated)


@app.route("/delete/<int:post_id>")
@login_required
@just_admins
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(debug=True)
 