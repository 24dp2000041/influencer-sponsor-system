import sqlite3
from flask import g

def connect_to_Database():
    sql = sqlite3.connect("C:\Users\user\Documents\GitHub\influencer-sponsor-system\employee.db")
    sql.row_factory = sqlite3.Row
    return sql

def get_databases():
    if not hasattr(g, "employee_db"):
        g.employee_db = connect_to_Database()
    return g.employee_db