from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fttb.db"
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


@app.route("/", methods=["GET", "POST"])
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
                return redirect(url_for("index"))
            except Exception as e:
                db.session.rollback()
                return f"Error adding database: {str(e)}", 400

    # 获取查询参数
    region_filter = request.args.get("region", "")
    address_filter = request.args.get("address", "")
    ip_filter = request.args.get("ip", "")

    # 构建基础查询
    query = db.session.query(DatabaseModel)

    # 应用过滤器
    if region_filter:
        query = query.filter(text("region LIKE :region")).params(
            region=f"%{region_filter}%"
        )
    if address_filter:
        query = query.filter(text("address LIKE :address")).params(
            address=f"%{address_filter}%"
        )
    if ip_filter:
        query = query.filter(text("ip LIKE :ip")).params(ip=f"%{ip_filter}%")

    entries = query.all()
    return render_template(
        "index.html",
        entries=entries,
        region_filter=region_filter,
        address_filter=address_filter,
        ip_filter=ip_filter,
    )


@app.route("/edit/<int:id>", methods=["POST"])
def edit_database(id):
    try:
        database = DatabaseModel.query.get_or_404(id)
        database.region = request.form["region"]
        database.address = request.form["address"]
        database.ip = request.form["ip"]
        db.session.commit()
        return redirect(url_for("index"))
    except Exception as e:
        db.session.rollback()
        return f"Error updating database: {str(e)}", 400


@app.route("/delete/<int:id>", methods=["POST"])
def delete_database(id):
    try:
        database = DatabaseModel.query.get_or_404(id)
        db.session.delete(database)
        db.session.commit()
        return redirect(url_for("index"))
    except Exception as e:
        db.session.rollback()
        return f"Error deleting database: {str(e)}", 400


# 初始化数据库表
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=False)
