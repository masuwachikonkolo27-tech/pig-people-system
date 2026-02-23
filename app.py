from flask import Flask, render_template, request, redirect, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import extract
from datetime import datetime
import os

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pigfarm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ================= MODELS =================

class Pig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pig_id = db.Column(db.Integer)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200))
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

# ================= HOME =================

@app.route("/")
def home():
    return redirect("/dashboard")

# ================= DASHBOARD =================

@app.route("/dashboard")
def dashboard():
    pigs = Pig.query.all()

    total_sales = db.session.query(db.func.sum(Sale.amount)).scalar() or 0
    total_expenses = db.session.query(db.func.sum(Expense.amount)).scalar() or 0
    profit = total_sales - total_expenses

    return render_template("dashboard.html",
                           pigs=pigs,
                           total_sales=total_sales,
                           total_expenses=total_expenses,
                           profit=profit)

# ================= ADD PIG =================

@app.route("/add_pig", methods=["POST"])
def add_pig():
    weight = request.form["weight"]
    age = request.form["age"]

    new_pig = Pig(weight=weight, age=age)
    db.session.add(new_pig)
    db.session.commit()

    return redirect("/dashboard")

# ================= DELETE PIG =================

@app.route("/delete_pig/<int:id>")
def delete_pig(id):
    pig = Pig.query.get(id)
    if pig:
        db.session.delete(pig)
        db.session.commit()
    return redirect("/dashboard")

# ================= ADD SALE =================

@app.route("/add_sale", methods=["POST"])
def add_sale():
    pig_id = request.form["pig_id"]
    amount = request.form["amount"]

    new_sale = Sale(pig_id=pig_id, amount=amount)
    db.session.add(new_sale)
    db.session.commit()

    return redirect("/dashboard")

# ================= ADD EXPENSE =================

@app.route("/add_expense", methods=["POST"])
def add_expense():
    description = request.form["description"]
    amount = request.form["amount"]

    new_expense = Expense(description=description, amount=amount)
    db.session.add(new_expense)
    db.session.commit()

    return redirect("/dashboard")

# ================= MONTHLY REPORT =================

@app.route("/monthly_report")
def monthly_report():
    now = datetime.now()
    month = now.month
    year = now.year

    monthly_sales = db.session.query(db.func.sum(Sale.amount))\
        .filter(extract('month', Sale.date) == month)\
        .filter(extract('year', Sale.date) == year)\
        .scalar() or 0

    monthly_expenses = db.session.query(db.func.sum(Expense.amount))\
        .filter(extract('month', Expense.date) == month)\
        .filter(extract('year', Expense.date) == year)\
        .scalar() or 0

    profit = monthly_sales - monthly_expenses

    return render_template("monthly_report.html",
                           monthly_sales=monthly_sales,
                           monthly_expenses=monthly_expenses,
                           profit=profit)

# ================= DOWNLOAD PDF =================

@app.route("/download_report")
def download_report():
    now = datetime.now()
    month = now.month
    year = now.year

    monthly_sales = db.session.query(db.func.sum(Sale.amount))\
        .filter(extract('month', Sale.date) == month)\
        .filter(extract('year', Sale.date) == year)\
        .scalar() or 0

    monthly_expenses = db.session.query(db.func.sum(Expense.amount))\
        .filter(extract('month', Expense.date) == month)\
        .filter(extract('year', Expense.date) == year)\
        .scalar() or 0

    profit = monthly_sales - monthly_expenses

    file_path = "monthly_report.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=A4)

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Pig People Monthly Report", styles["Title"]))
    elements.append(Spacer(1, 0.5 * inch))

    data = [
        ["Total Sales", f"ZMW {monthly_sales}"],
        ["Total Expenses", f"ZMW {monthly_expenses}"],
        ["Profit", f"ZMW {profit}"],
    ]

    table = Table(data, colWidths=[3 * inch, 2 * inch])
    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))

    elements.append(table)
    doc.build(elements)

    return send_file(file_path, as_attachment=True)

# ================= RUN =================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)