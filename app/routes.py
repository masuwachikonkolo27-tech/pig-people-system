from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Pig, Sale, Expense
from . import db, login_manager
from sqlalchemy import extract
from datetime import datetime


def register_routes(app):

    # ================= USER LOADER =================
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    # ================= HOME =================
    @app.route("/")
    def home():
        return redirect(url_for("login"))


    # ================= LOGIN =================
    @app.route("/login", methods=["GET", "POST"])
    def login():

        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            user = User.query.filter_by(username=username).first()

            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for("dashboard"))

            flash("Invalid username or password")

        return render_template("login.html")


    # ================= LOGOUT =================
    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("login"))


    # ================= DASHBOARD =================
    @app.route("/dashboard")
    @login_required
    def dashboard():

        if current_user.role == "admin":
            pigs = Pig.query.all()
            sales = Sale.query.all()
            expenses = Expense.query.all()
        else:
            pigs = Pig.query.filter_by(user_id=current_user.id).all()
            sales = Sale.query.filter_by(user_id=current_user.id).all()
            expenses = Expense.query.filter_by(user_id=current_user.id).all()

        total_sales = sum(s.amount for s in sales)
        total_expenses = sum(e.amount for e in expenses)
        profit = total_sales - total_expenses if current_user.role == "admin" else None

        return render_template(
            "dashboard.html",
            pigs=pigs,
            sales=sales,
            expenses=expenses,
            total_sales=total_sales,
            total_expenses=total_expenses,
            profit=profit
        )


    # ================= MANAGE USERS =================
    @app.route("/users", methods=["GET", "POST"])
    @login_required
    def users():

        if current_user.role != "admin":
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            role = request.form.get("role")

            if not username or not password or not role:
                flash("All fields required")
                return redirect(url_for("users"))

            new_user = User(username=username, role=role)
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()

            flash("User created successfully")

        all_users = User.query.all()
        return render_template("users.html", users=all_users)


    # ================= DELETE USER =================
    @app.route("/delete_user/<int:id>")
    @login_required
    def delete_user(id):

        if current_user.role != "admin":
            return redirect(url_for("dashboard"))

        user = User.query.get_or_404(id)

        if user.id == current_user.id:
            flash("You cannot delete yourself.")
            return redirect(url_for("users"))

        db.session.delete(user)
        db.session.commit()

        return redirect(url_for("users"))


    # ================= ADD PIG =================
    @app.route("/add_pig", methods=["POST"])
    @login_required
    def add_pig():

        name = request.form.get("name")
        breed = request.form.get("breed")
        weight = request.form.get("weight")
        age = request.form.get("age")

        if not name or not breed or not weight or not age:
            flash("All pig fields are required")
            return redirect(url_for("dashboard"))

        pig = Pig(
            name=name,
            breed=breed,
            weight=float(weight),
            age=int(age),
            user_id=current_user.id
        )

        db.session.add(pig)
        db.session.commit()

        return redirect(url_for("dashboard"))


    # ================= EDIT PIG =================
    @app.route("/edit_pig/<int:id>", methods=["GET", "POST"])
    @login_required
    def edit_pig(id):

        pig = Pig.query.get_or_404(id)

        if pig.user_id != current_user.id and current_user.role != "admin":
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            pig.breed = request.form.get("breed")
            pig.weight = float(request.form.get("weight"))
            pig.age = int(request.form.get("age"))

            db.session.commit()
            return redirect(url_for("dashboard"))

        return render_template("edit_pig.html", pig=pig)


    # ================= DELETE PIG =================
    @app.route("/delete_pig/<int:id>")
    @login_required
    def delete_pig(id):

        pig = Pig.query.get_or_404(id)

        if pig.user_id != current_user.id and current_user.role != "admin":
            return redirect(url_for("dashboard"))

        db.session.delete(pig)
        db.session.commit()

        return redirect(url_for("dashboard"))


    # ================= ADD SALE =================
    @app.route("/add_sale", methods=["POST"])
    @login_required
    def add_sale():

        pig_id = request.form.get("pig_id")
        description = request.form.get("description")
        amount = request.form.get("amount")

        if not pig_id or not description or not amount:
            flash("All sale fields are required")
            return redirect(url_for("dashboard"))

        new_sale = Sale(
            pig_id=int(pig_id),
            description=description,
            amount=float(amount),
            user_id=current_user.id
        )

        db.session.add(new_sale)
        db.session.commit()

        return redirect(url_for("dashboard"))


    # ================= EDIT SALE =================
    @app.route("/edit_sale/<int:id>", methods=["GET", "POST"])
    @login_required
    def edit_sale(id):

        sale = Sale.query.get_or_404(id)

        if sale.user_id != current_user.id and current_user.role != "admin":
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            sale.pig_id = int(request.form.get("pig_id"))
            sale.description = request.form.get("description")
            sale.amount = float(request.form.get("amount"))

            db.session.commit()
            return redirect(url_for("dashboard"))

        pigs = Pig.query.all()
        return render_template("edit_sale.html", sale=sale, pigs=pigs)


    # ================= DELETE SALE =================
    @app.route("/delete_sale/<int:id>")
    @login_required
    def delete_sale(id):

        sale = Sale.query.get_or_404(id)

        if sale.user_id != current_user.id and current_user.role != "admin":
            return redirect(url_for("dashboard"))

        db.session.delete(sale)
        db.session.commit()

        return redirect(url_for("dashboard"))


    # ================= ADD EXPENSE =================
    @app.route("/add_expense", methods=["POST"])
    @login_required
    def add_expense():

        description = request.form.get("description")
        amount = request.form.get("amount")

        if not description or not amount:
            flash("All expense fields required")
            return redirect(url_for("dashboard"))

        new_expense = Expense(
            description=description,
            amount=float(amount),
            user_id=current_user.id
        )

        db.session.add(new_expense)
        db.session.commit()

        return redirect(url_for("dashboard"))


    # ================= EDIT EXPENSE =================
    @app.route("/edit_expense/<int:id>", methods=["GET", "POST"])
    @login_required
    def edit_expense(id):

        expense = Expense.query.get_or_404(id)

        if expense.user_id != current_user.id and current_user.role != "admin":
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            expense.description = request.form.get("description")
            expense.amount = float(request.form.get("amount"))

            db.session.commit()
            return redirect(url_for("dashboard"))

        return render_template("edit_expense.html", expense=expense)


    # ================= DELETE EXPENSE =================
    @app.route("/delete_expense/<int:id>")
    @login_required
    def delete_expense(id):

        expense = Expense.query.get_or_404(id)

        if expense.user_id != current_user.id and current_user.role != "admin":
            return redirect(url_for("dashboard"))

        db.session.delete(expense)
        db.session.commit()

        return redirect(url_for("dashboard"))


    # ================= MONTHLY REPORT =================
    @app.route("/monthly_report")
    @login_required
    def monthly_report():

        if current_user.role != "admin":
            return redirect(url_for("dashboard"))

        month = datetime.utcnow().month
        year = datetime.utcnow().year

        sales = Sale.query.filter(
            extract("month", Sale.date) == month,
            extract("year", Sale.date) == year
        ).all()

        expenses = Expense.query.filter(
            extract("month", Expense.date) == month,
            extract("year", Expense.date) == year
        ).all()

        total_sales = sum(s.amount for s in sales)
        total_expenses = sum(e.amount for e in expenses)

        return render_template(
            "monthly_report.html",
            total_sales=total_sales,
            total_expenses=total_expenses
        )