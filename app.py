from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import *
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from model import *
from datetime import datetime
import os
from flask_migrate import Migrate
app = Flask(__name__)
app.config['SECRET_KEY'] = 'SUPERGAYBASS2025'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assetdb.db' 
print(f"Load database from {app.config['SQLALCHEMY_DATABASE_URI']}")
migrate = Migrate(app, db)
db.init_app(app)
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return redirect(url_for('dashboard'))

def checkAdmin():
    user_id = session.get('user_id')
    user = User.query.join(Department).filter(User.user_id == user_id).first()
    if user and user.department and user.department.name.strip().upper() == "IT":
        return True
    else:
        return False
    
# def getUser():
#     user_id = session.get('user_id')
#     if not user_id:
#         return None, None  
#     user_info = db.session.query(User, Department).join(Department, User.department_id == Department.department_id).filter(User.user_id == user_id).first()
#     if user_info:
#         user, department = user_info
#         return user, department
#     else:
#         return None, None  

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.user_id
            # session['department'] = user.department
            # flash('เข้าสู่ระบบสำเร็จ!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    data = Department.query.all()
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        lastname = request.form['lastname']
        nickname = request.form['nickname']
        department = request.form['department_id']

        if User.query.filter_by(username=username).first():
            flash('ชื่อผู้ใช้งานนี้มีอยู่ในระบบแล้ว', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, name=name, lastname=lastname, nickname=nickname, department_id=department)
        db.session.add(new_user)
        db.session.commit()
        flash('ลงทะเบียนสำเร็จ! กรุณาเข้าสู่ระบบ', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', departments=data)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session.get(User, session['user_id'])
    user_info = db.session.query(User, Department).join(Department, User.department_id == Department.department_id).filter(User.user_id == user_id).first()
    user, department = user_info
    
    status_counts = {
        'normal': db.session.query(Asset).filter(Asset.status == 'ปกติ').count(),
        'faulty': db.session.query(Asset).filter(Asset.status == 'เสีย').count(),
        'backup': db.session.query(Asset).filter(Asset.status == 'สำรอง').count(),
        'not_found': db.session.query(Asset).filter(Asset.status == 'หาไม่เจอ').count(),
    }
    isAdmin = checkAdmin()
    

    return render_template('dashboard.html', user=user, department=department, status_counts=status_counts, isAdmin=isAdmin)


@app.route('/chart_data')
def chart_data():

    department_counts = db.session.query(
        Department.name,  
        func.count(Asset.asset_id).label('asset_count')
    ).join(Asset, Asset.department_id == Department.department_id).group_by(Department.department_id).all() 

    result = [{'department': dept_name, 'asset_count': count} for dept_name, count in department_counts]
    return jsonify(result)


@app.route('/assets')
def assets():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session.get(User, session['user_id'])
    user_info = db.session.query(User, Department).join(Department, User.department_id == Department.department_id).filter(User.user_id == user_id).first()
    user, department = user_info
    
    department = Department.query.all()
    # data = Asset.query.join(User).join(Department).join(AssetType).all()
    data = (
        Asset.query
        .options(
            joinedload(Asset.department),
            joinedload(Asset.asset_type)
        ) 
        .order_by(Asset.asset_code.asc())
        .all()
    )
    
    isAdmin = checkAdmin()
    
    return render_template('assets.html', user=user,  assets=data, departments=department, isAdmin=isAdmin)



@app.route('/admin/assets')
def admin_assets():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    department = Department.query.all()
    # data = Asset.query.join(User).join(Department).join(AssetType).all()
    data = (
        Asset.query
        .options(
            joinedload(Asset.department),
            joinedload(Asset.asset_type)
        ) 
        .order_by(Asset.asset_code.asc())
        .all()
    )
    isAdmin = checkAdmin()
    return render_template('admin/assets.html', assets=data, isAdmin=isAdmin, departments=department)

@app.route('/assets/view/<int:asset_id>')
def view_asset(asset_id):
    isPc = False
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # asset = Asset.query.get(asset_id) 
    asset = db.session.get(Asset, asset_id)
    if not asset:
        return "ไม่พบข้อมูลสินทรัพย์"
    
    if asset.asset_type_id in [1,2]:
        isPc = True
        
    return render_template('view_asset.html', asset=asset, isPc=isPc)

@app.route('/assets/search')
def search():
    query = request.args.get('query')
    assets = Asset.query.join(Department).join(AssetType).filter(
        (Asset.asset_code.ilike(f'%{query}%')) | 
        (Asset.name.ilike(f'%{query}%')) | 
        (Asset.nickname.ilike(f'%{query}%')) | 
        (Asset.status.ilike(f'%{query}%')) |  
        (AssetType.name.ilike(f'%{query}%')) | 
        (Department.name.ilike(f'%{query}%')) 
 
    ).all()
    isAdmin = checkAdmin()
    department = Department.query.all()
    return render_template('assets.html', assets=assets, departments=department)



@app.route('/admin/assets/search')
def admin_search():
    query = request.args.get('query')
    assets = Asset.query.join(Department).join(AssetType).filter(
        (Asset.asset_code.ilike(f'%{query}%')) | 
        (Asset.name.ilike(f'%{query}%')) | 
        (Asset.nickname.ilike(f'%{query}%')) | 
        (Asset.status.ilike(f'%{query}%')) |  
        (AssetType.name.ilike(f'%{query}%')) | 
        (Department.name.ilike(f'%{query}%')) 
 
    ).all()
    isAdmin = checkAdmin()
    department = Department.query.all()
    return render_template('admin/assets.html', assets=assets, isAdmin=isAdmin, departments=department)


@app.route('/assets/add', methods=['GET', 'POST'])
def add_asset():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        asset_code = request.form['asset_code']
        name = request.form['name']
        nickname = request.form['nickname']
        department_id = request.form['department_id']
        brand = request.form['brand']
        model = request.form['model']
        description = request.form['description']
        price = request.form['price']
        asset_type_id = request.form['asset_type_id']
        status = request.form['status']
        type = request.form['type']
        cpu_name = request.form['cpu_name']
        cpu_type = request.form['cpu_type']
        ram = request.form['ram']
        ram_memory = request.form['ram_memory']
        mainboard_name = request.form['mainboard_name']
        mainboard_model = request.form['mainboard_model']
        ssd = request.form['ssd']
        ssd_model = request.form['ssd_model']
        hdd = request.form['hdd']
        hdd_model = request.form['hdd_model']
        gpu = request.form['gpu']
        powersupply = request.form['powersupply']
        os = request.form['os']
        check_date = request.form['check_date']
        account_create = request.form['account_create']
        buy_date = request.form['buy_date']
        
        checkAssetCode = Asset.query.filter_by(asset_code=asset_code).first()
        if checkAssetCode:
            flash('รหัสทรัพย์สินซ้ำ', 'danger')
            return redirect(url_for('add_asset'))
        
        if buy_date:
            buy_date = datetime.strptime(buy_date, "%Y-%m-%dT%H:%M")
        else:
            buy_date = None
            
        if check_date:
            check_date = datetime.strptime(check_date, "%Y-%m-%dT%H:%M")
        else:
            check_date = None
          

        add = Asset(
            asset_code=asset_code,
            name=name,
            nickname=nickname,
            department_id=department_id,
            brand=brand,
            model=model,
            description=description,
            price=price,
            asset_type_id=asset_type_id,
            status=status,
            type=type,
            cpu_name=cpu_name,
            cpu_type=cpu_type,
            ram=ram,
            ram_memory=ram_memory,
            mainboard_name=mainboard_name,
            mainboard_model=mainboard_model,
            ssd=ssd,
            ssd_model=ssd_model,
            hdd=hdd,
            hdd_model=hdd_model,
            gpu=gpu,
            powersupply=powersupply,
            os=os,
            check_date=check_date,
            account_create=account_create,
            buy_date=buy_date
        )
        try:
            db.session.add(add)
            db.session.commit()
            flash(f'เพิ่มทรัพย์สินสําเร็จ {asset_code}', 'success')
        except:
            flash(f'เกิดข้อผิดพลาด', 'danger')
        
    department = Department.query.all()
    asset_type = AssetType.query.all()
    
    return render_template('add_asset.html', departments=department, asset_types=asset_type)

@app.route('/assets/edit/<int:asset_id>', methods=['GET', 'POST'])
def edit_asset(asset_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    isAdmin = checkAdmin()
    
    department = Department.query.all()
    asset_type = AssetType.query.all()
    asset = db.session.get(Asset, asset_id, 
    options=[joinedload(Asset.department), joinedload(Asset.asset_type)])

    if asset.buy_date:
        buy_date = asset.buy_date.strftime('%Y-%m-%dT%H:%M')
    else:
        buy_date = ""
        
    if asset.check_date:
        check_date = asset.buy_date.strftime('%Y-%m-%dT%H:%M')
    else:
        check_date = ""
    
    if request.method == 'POST':
        asset.asset_code = request.form['asset_code']
        asset.name = request.form['name']
        asset.nickname = request.form['nickname']
        asset.department_id = request.form['department_id']
        asset.brand = request.form['brand']
        asset.model = request.form['model']
        asset.description = request.form['description']
        asset.price = float(request.form['price']) if request.form['price'] else 0.0
        asset.asset_type_id = request.form['asset_type_id']
        asset.status = request.form['status']
        asset.type = request.form['type']
        asset.cpu_name = request.form['cpu_name']
        asset.cpu_type = request.form['cpu_type']
        asset.ram = request.form['ram']
        asset.ram_memory = request.form['ram_memory']
        asset.mainboard_name = request.form['mainboard_name']
        asset.mainboard_model = request.form['mainboard_model']
        asset.ssd = request.form['ssd']
        asset.ssd_model = request.form['ssd_model']
        asset.hdd = request.form['hdd']
        asset.hdd_model = request.form['hdd_model']
        asset.gpu = request.form['gpu']
        asset.powersupply = request.form['powersupply']
        asset.os = request.form['os']
        # asset.check_date = request.form['check_date']
        asset.check_date = datetime.strptime(request.form['check_date'], "%Y-%m-%dT%H:%M") if request.form['check_date'] else None

        # asset.buy_date = request.form['buy_date']
        asset.buy_date = datetime.strptime(request.form['buy_date'], "%Y-%m-%dT%H:%M") if request.form['buy_date'] else None

        asset.account_create = request.form['account_create']

        try:
            db.session.commit()
            flash(f'แก้ไขทรัพย์สินสําเร็จ {asset.asset_code}', 'success')
        except:
            flash(f'เกิดข้อผิดพลาด', 'danger')
       


    
    return render_template('edit/edit_asset.html', isAdmin=isAdmin, asset=asset, departments=department, asset_types=asset_type, buy_date=buy_date, check_date=check_date)

@app.route('/logout')
def logout():
    
    if 'user_id' in session:
        session.clear()
        # session.pop('user_id', None)
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))
    
@app.errorhandler(404)
def notfound(error):
    return "404 ไม่พบหน้าเพจ"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)