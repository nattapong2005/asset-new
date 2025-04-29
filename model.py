from flask_sqlalchemy import SQLAlchemy
import enum
from datetime import datetime

db = SQLAlchemy()

# class StatusEnum(enum.Enum):
#     ปกติ = "ปกติ"
#     เสีย = "เสีย"
#     สำรอง = "สำรอง"
#     หาไม่เจอ = "หาไม่เจอ"

class Department(db.Model):
    __tablename__ = "department"
    department_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    assets = db.relationship('Asset', back_populates='department', lazy=True)
    users = db.relationship('User', back_populates='department', lazy=True)

class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password =  db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    lastname = db.Column(db.String, nullable=False)
    nickname = db.Column(db.String, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.department_id'), nullable=False)
    
    # assets = db.relationship('Asset', backref='user_assets', lazy=True)
    department = db.relationship('Department', back_populates='users', lazy=True)
    # assets_list = db.relationship('Asset', back_populates='user', lazy=True) 
    borrows = db.relationship('Borrow', back_populates='user', lazy=True)

class AssetType(db.Model):
    __tablename__ = "assets_type"
    type_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    # assets = db.relationship('Asset', backref='asset_type', lazy=True)
    assets = db.relationship('Asset', back_populates='asset_type', lazy=True)

class Asset(db.Model):
    __tablename__ = "assets"
    asset_id = db.Column(db.Integer, primary_key=True)
    asset_code = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=True) 
    nickname = db.Column(db.String, nullable=True) 
    department_id = db.Column(db.Integer, db.ForeignKey('department.department_id'), nullable=False)
    # asset_name = db.Column(db.String, nullable=False)
    brand = db.Column(db.String, nullable=True)
    model = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=True)
    price = db.Column(db.Float, nullable=True)
    asset_type_id = db.Column(db.Integer, db.ForeignKey('assets_type.type_id'), nullable=False)
    status = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=True)
    cpu_name = db.Column(db.String, nullable=True)
    cpu_type = db.Column(db.String, nullable=True)
    ram = db.Column(db.String, nullable=True)
    ram_memory = db.Column(db.Integer, nullable=True)
    mainboard_name = db.Column(db.String, nullable=True)
    mainboard_model = db.Column(db.String, nullable=True)
    ssd = db.Column(db.String, nullable=True)
    ssd_model = db.Column(db.String, nullable=True)
    hdd = db.Column(db.String, nullable=True)
    hdd_model = db.Column(db.String, nullable=True)
    gpu = db.Column(db.String, nullable=True)
    powersupply = db.Column(db.String, nullable=True)
    os = db.Column(db.String, nullable=True)
    check_date = db.Column(db.DateTime, nullable=True) 
    account_create = db.Column(db.String, nullable=True)
    buy_date = db.Column(db.DateTime, nullable=True)


    department = db.relationship('Department', back_populates='assets', lazy=True)
    asset_type = db.relationship('AssetType', back_populates='assets', lazy=True)
    borrows = db.relationship('Borrow', back_populates='asset', lazy=True)

class Borrow(db.Model):
    __tablename__ = "borrow"
    borrow_id = db.Column(db.Integer, primary_key=True)
    borrow_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.asset_id'), nullable=False)
    
    user = db.relationship('User', back_populates='borrows', lazy=True)
    asset = db.relationship('Asset', back_populates='borrows', lazy=True)