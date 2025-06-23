import os
from functools import wraps

import uvicorn
from asgiref.wsgi import WsgiToAsgi
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, cast
from werkzeug.security import check_password_hash, generate_password_hash


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fttb.db"
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "your_fallback_secret_key")
db = SQLAlchemy(app)


class DatabaseModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    ip = db.Column(db.String(16), nullable=False)

    def __init__(self, region, address, ip):
        self.region = region
        self.address = address
        self.ip = ip


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            flash("用户名或密码错误")
    return render_template("login.html")


@app.route("/users")
@login_required
def user_management():
    users = User.query.all()
    return render_template("users.html", users=users)


@app.route("/add_user", methods=["POST"])
@login_required
def add_user():
    username = request.form.get("username")
    password = request.form.get("password")
    if not username or not password:
        flash("用户名和密码不能为空")
        return redirect(url_for("user_management"))

    if User.query.filter_by(username=username).first():
        flash("用户名已存在")
        return redirect(url_for("user_management"))

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    flash("用户添加成功！")
    return redirect(url_for("user_management"))


@app.route("/delete_user/<int:id>", methods=["POST"])
@login_required
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash("用户删除成功！")
    return redirect(url_for("user_management"))


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        form_action = request.form.get("form_action")
        if form_action == "add":
            region = request.form["region"]
            address = request.form["address"]
            ip = request.form["ip"]

            try:
                new_entry = DatabaseModel(region=region, address=address, ip=ip)
                db.session.add(new_entry)
                db.session.commit()
                flash("数据库条目添加成功！")
                return redirect(url_for("index"))
            except Exception as e:
                db.session.rollback()
                flash(f"添加数据库条目时发生错误: {str(e)}")
                return redirect(url_for("index"))

    # 获取查询参数
    region_filter = request.args.get("region", "")
    address_filter = request.args.get("address", "")
    ip_filter = request.args.get("ip", "")

    # 构建基础查询
    query = db.select(DatabaseModel)

    # 应用过滤器
    if region_filter:
        query = query.filter(
            cast(DatabaseModel.region, String).ilike(f"%{region_filter}%")  # type: ignore
        )
    if address_filter:
        query = query.filter(
            cast(DatabaseModel.address, String).ilike(f"%{address_filter}%")  # type: ignore
        )
    if ip_filter:
        query = query.filter(cast(DatabaseModel.ip, String).ilike(f"%{ip_filter}%"))  # type: ignore

    entries = db.session.execute(query).scalars().all()
    users = User.query.all()
    return render_template(
        "index.html",
        entries=entries,
        users=users,
        region_filter=region_filter,
        address_filter=address_filter,
        ip_filter=ip_filter,
    )


@app.route("/edit/<int:id>", methods=["POST"])
@login_required
def edit_database(id):
    try:
        database = DatabaseModel.query.get_or_404(id)
        database.region = request.form["region"]
        database.address = request.form["address"]
        database.ip = request.form["ip"]
        db.session.commit()
        flash("数据库条目更新成功！")
        return redirect(url_for("index"))
    except Exception as e:
        db.session.rollback()
        flash(f"更新数据库条目时发生错误: {str(e)}")
        return redirect(url_for("index"))


@app.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_database(id):
    try:
        database = DatabaseModel.query.get_or_404(id)
        db.session.delete(database)
        db.session.commit()
        flash("数据库条目删除成功！")
        return redirect(url_for("index"))
    except Exception as e:
        db.session.rollback()
        flash(f"删除数据库条目时发生错误: {str(e)}")
        return redirect(url_for("index"))


# 初始化数据库表
with app.app_context():
    db.create_all()

    # 添加默认管理员用户（如果不存在）
    admin_exists = User.query.filter_by(username="admin").first()
    if not admin_exists:
        admin_user = User(username="admin", password="Password")
        db.session.add(admin_user)
        db.session.commit()


# 包装为 ASGI 应用
asgi_app = WsgiToAsgi(app)

if __name__ == "__main__":
    uvicorn.run("main:asgi_app", host="0.0.0.0", port=5000)
