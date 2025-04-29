import pandas as pd
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from model import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assetdb.db'
db = SQLAlchemy(app)

def run():
    file = "ink.csv"
    df = pd.read_csv(file)
    for index, row in df.iterrows():
        check_date = None
        buy_date = None
        if pd.notnull(row['check_date']):
            check_date = pd.to_datetime(row['check_date'], format='%d/%m/%Y')
            # print(check_date)
        if pd.notnull(row['buy_date']):
            buy_date = pd.to_datetime(row['buy_date'], format='%d/%m/%Y')
            # print(buy_date)

        asset = Asset(
            asset_code=row['asset_code'],
            name=row['name'],
            nickname=row['nickname'],
            department_id=row['department_id'],  # ระวังหาก column นี้จำเป็น
            brand=row['brand'],
            model=row['model'],
            description=row['description'],
            price=row['price'],
            asset_type_id=row['asset_type_id'],
            status=row['status'],
            type=row['type'],
            cpu_name=row['cpu_name'],
            cpu_type=row['cpu_type'],
            ram=row['ram'],
            ram_memory=row['ram_memory'],
            mainboard_name=row['mainboard_name'],
            mainboard_model=row['mainboard_model'],
            ssd=row['ssd'],
            ssd_model=row['ssd_model'],
            hdd=row['hdd'],
            hdd_model=row['hdd_model'],
            gpu=row['gpu'],
            powersupply=row['powersupply'],
            os=row['os'],
            check_date=check_date,
            account_create=row['create_account'],
            buy_date=buy_date
        )
        db.session.add(asset)

    db.session.commit()
    print("Data imported successfully " + file)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        run()
