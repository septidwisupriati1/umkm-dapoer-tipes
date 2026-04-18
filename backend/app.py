from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='../frontend', static_folder='../frontend')
CORS(app)

# Konfigurasi Database
database_url = os.getenv('DATABASE_URL', 'sqlite:///umkm_dapoer_tipes.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ===== MODEL DATABASE =====

class Pelanggan(db.Model):
    __tablename__ = 'pelanggan'
    
    ID_Pelanggan = db.Column(db.Integer, primary_key=True)
    Nama_Pelanggan = db.Column(db.String(100), nullable=False)
    Telepon = db.Column(db.String(15))
    Email = db.Column(db.String(100))
    Alamat = db.Column(db.Text)
    Tipe_Pelanggan = db.Column(db.String(50), default='Retail')
    Status = db.Column(db.String(50), default='Aktif')
    Total_Pembelian = db.Column(db.Float, default=0)
    Tanggal_Daftar = db.Column(db.DateTime, default=datetime.utcnow)
    
    penjualan = db.relationship('Penjualan', backref='pelanggan', lazy=True)
    
    def to_dict(self):
        return {
            'ID_Pelanggan': self.ID_Pelanggan,
            'Nama_Pelanggan': self.Nama_Pelanggan,
            'Telepon': self.Telepon,
            'Email': self.Email,
            'Alamat': self.Alamat,
            'Tipe_Pelanggan': self.Tipe_Pelanggan,
            'Status': self.Status,
            'Total_Pembelian': self.Total_Pembelian
        }

class Produk(db.Model):
    __tablename__ = 'produk'
    
    ID_Produk = db.Column(db.Integer, primary_key=True)
    Nama_Produk = db.Column(db.String(100), nullable=False)
    Harga_Satuan = db.Column(db.Float, nullable=False)
    Harga_Grosir = db.Column(db.Float)
    Stok = db.Column(db.Integer, default=0)
    Stok_Minimal = db.Column(db.Integer, default=5)
    Kategori = db.Column(db.String(50))
    Deskripsi = db.Column(db.Text)
    Status = db.Column(db.String(50), default='Aktif')
    Tanggal_Dibuat = db.Column(db.DateTime, default=datetime.utcnow)
    
    penjualan = db.relationship('Penjualan', backref='produk', lazy=True)
    
    def to_dict(self):
        return {
            'ID_Produk': self.ID_Produk,
            'Nama_Produk': self.Nama_Produk,
            'Harga_Satuan': self.Harga_Satuan,
            'Harga_Grosir': self.Harga_Grosir,
            'Stok': self.Stok,
            'Kategori': self.Kategori,
            'Status': self.Status
        }

class Penjualan(db.Model):
    __tablename__ = 'penjualan'
    
    ID_Penjualan = db.Column(db.Integer, primary_key=True)
    ID_Pelanggan = db.Column(db.Integer, db.ForeignKey('pelanggan.ID_Pelanggan'), nullable=False)
    ID_Produk = db.Column(db.Integer, db.ForeignKey('produk.ID_Produk'), nullable=False)
    Jumlah = db.Column(db.Integer, nullable=False)
    Harga_Satuan = db.Column(db.Float, nullable=False)
    Harga_Total = db.Column(db.Float, nullable=False)
    Diskon = db.Column(db.Float, default=0)
    Jumlah_Setelah_Diskon = db.Column(db.Float)
    Tanggal_Penjualan = db.Column(db.DateTime, default=datetime.utcnow)
    Status = db.Column(db.String(50), default='Selesai')
    Metode_Pembayaran = db.Column(db.String(50), default='Tunai')
    Catatan = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'ID_Penjualan': self.ID_Penjualan,
            'Nama_Pelanggan': self.pelanggan.Nama_Pelanggan,
            'Nama_Produk': self.produk.Nama_Produk,
            'Jumlah': self.Jumlah,
            'Harga_Total': self.Harga_Total,
            'Diskon': self.Diskon,
            'Tanggal_Penjualan': self.Tanggal_Penjualan.strftime('%Y-%m-%d %H:%M:%S'),
            'Status': self.Status,
            'Metode_Pembayaran': self.Metode_Pembayaran
        }

class Pengeluaran(db.Model):
    __tablename__ = 'pengeluaran'
    
    ID_Pengeluaran = db.Column(db.Integer, primary_key=True)
    Kategori = db.Column(db.String(100), nullable=False)
    Deskripsi = db.Column(db.String(200))
    Jumlah = db.Column(db.Float, nullable=False)
    Tanggal_Pengeluaran = db.Column(db.Date, nullable=False)
    Status = db.Column(db.String(50), default='Belum Verifikasi')
    Catatan = db.Column(db.Text)
    Tanggal_Dibuat = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'ID_Pengeluaran': self.ID_Pengeluaran,
            'Kategori': self.Kategori,
            'Deskripsi': self.Deskripsi,
            'Jumlah': self.Jumlah,
            'Tanggal_Pengeluaran': str(self.Tanggal_Pengeluaran),
            'Status': self.Status
        }

# ===== ROUTES =====

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/sales', methods=['GET'])
def sales():
    return render_template('sales.html')

@app.route('/financial-reports', methods=['GET'])
def financial_reports():
    return render_template('financial-reports.html')

@app.route('/direct-sales', methods=['GET'])
def direct_sales():
    return render_template('direct-sales.html')

# ===== API ENDPOINTS =====

# PELANGGAN
@app.route('/api/pelanggan', methods=['GET'])
def get_pelanggan():
    pelanggan_list = Pelanggan.query.all()
    return jsonify([p.to_dict() for p in pelanggan_list])

@app.route('/api/pelanggan', methods=['POST'])
def create_pelanggan():
    data = request.json
    pelanggan = Pelanggan(
        Nama_Pelanggan=data['Nama_Pelanggan'],
        Telepon=data.get('Telepon'),
        Email=data.get('Email'),
        Alamat=data.get('Alamat'),
        Tipe_Pelanggan=data.get('Tipe_Pelanggan', 'Retail')
    )
    db.session.add(pelanggan)
    db.session.commit()
    return jsonify(pelanggan.to_dict()), 201

@app.route('/api/pelanggan/<int:id>', methods=['PUT'])
def update_pelanggan(id):
    pelanggan = Pelanggan.query.get(id)
    if not pelanggan:
        return jsonify({'error': 'Pelanggan not found'}), 404
    
    data = request.json
    pelanggan.Nama_Pelanggan = data.get('Nama_Pelanggan', pelanggan.Nama_Pelanggan)
    pelanggan.Telepon = data.get('Telepon', pelanggan.Telepon)
    pelanggan.Email = data.get('Email', pelanggan.Email)
    pelanggan.Alamat = data.get('Alamat', pelanggan.Alamat)
    pelanggan.Tipe_Pelanggan = data.get('Tipe_Pelanggan', pelanggan.Tipe_Pelanggan)
    
    db.session.commit()
    return jsonify(pelanggan.to_dict())

@app.route('/api/pelanggan/<int:id>', methods=['DELETE'])
def delete_pelanggan(id):
    pelanggan = Pelanggan.query.get(id)
    if not pelanggan:
        return jsonify({'error': 'Pelanggan not found'}), 404
    
    db.session.delete(pelanggan)
    db.session.commit()
    return jsonify({'message': 'Pelanggan deleted'}), 200

# PRODUK
@app.route('/api/produk', methods=['GET'])
def get_produk():
    produk_list = Produk.query.all()
    return jsonify([p.to_dict() for p in produk_list])

@app.route('/api/produk', methods=['POST'])
def create_produk():
    data = request.json
    produk = Produk(
        Nama_Produk=data['Nama_Produk'],
        Harga_Satuan=data['Harga_Satuan'],
        Harga_Grosir=data.get('Harga_Grosir'),
        Stok=data.get('Stok', 0),
        Kategori=data.get('Kategori')
    )
    db.session.add(produk)
    db.session.commit()
    return jsonify(produk.to_dict()), 201

@app.route('/api/produk/<int:id>', methods=['PUT'])
def update_produk(id):
    produk = Produk.query.get(id)
    if not produk:
        return jsonify({'error': 'Produk not found'}), 404
    
    data = request.json
    produk.Nama_Produk = data.get('Nama_Produk', produk.Nama_Produk)
    produk.Harga_Satuan = data.get('Harga_Satuan', produk.Harga_Satuan)
    produk.Harga_Grosir = data.get('Harga_Grosir', produk.Harga_Grosir)
    produk.Stok = data.get('Stok', produk.Stok)
    produk.Kategori = data.get('Kategori', produk.Kategori)
    
    db.session.commit()
    return jsonify(produk.to_dict())

@app.route('/api/produk/<int:id>', methods=['DELETE'])
def delete_produk(id):
    produk = Produk.query.get(id)
    if not produk:
        return jsonify({'error': 'Produk not found'}), 404
    
    db.session.delete(produk)
    db.session.commit()
    return jsonify({'message': 'Produk deleted'}), 200

# PENJUALAN
@app.route('/api/penjualan', methods=['GET'])
def get_penjualan():
    penjualan_list = Penjualan.query.all()
    return jsonify([p.to_dict() for p in penjualan_list])

@app.route('/api/penjualan', methods=['POST'])
def create_penjualan():
    data = request.json
    penjualan = Penjualan(
        ID_Pelanggan=data['ID_Pelanggan'],
        ID_Produk=data['ID_Produk'],
        Jumlah=data['Jumlah'],
        Harga_Satuan=data['Harga_Satuan'],
        Harga_Total=data['Harga_Total'],
        Diskon=data.get('Diskon', 0),
        Metode_Pembayaran=data.get('Metode_Pembayaran', 'Tunai')
    )
    db.session.add(penjualan)
    db.session.commit()
    return jsonify(penjualan.to_dict()), 201

@app.route('/api/penjualan/<int:id>', methods=['PUT'])
def update_penjualan(id):
    penjualan = Penjualan.query.get(id)
    if not penjualan:
        return jsonify({'error': 'Penjualan not found'}), 404
    
    data = request.json
    penjualan.Status = data.get('Status', penjualan.Status)
    penjualan.Metode_Pembayaran = data.get('Metode_Pembayaran', penjualan.Metode_Pembayaran)
    
    db.session.commit()
    return jsonify(penjualan.to_dict())

@app.route('/api/penjualan/<int:id>', methods=['DELETE'])
def delete_penjualan(id):
    penjualan = Penjualan.query.get(id)
    if not penjualan:
        return jsonify({'error': 'Penjualan not found'}), 404
    
    db.session.delete(penjualan)
    db.session.commit()
    return jsonify({'message': 'Penjualan deleted'}), 200

# PENGELUARAN
@app.route('/api/pengeluaran', methods=['GET'])
def get_pengeluaran():
    pengeluaran_list = Pengeluaran.query.all()
    return jsonify([p.to_dict() for p in pengeluaran_list])

@app.route('/api/pengeluaran', methods=['POST'])
def create_pengeluaran():
    data = request.json
    pengeluaran = Pengeluaran(
        Kategori=data['Kategori'],
        Deskripsi=data.get('Deskripsi'),
        Jumlah=data['Jumlah'],
        Tanggal_Pengeluaran=datetime.strptime(data['Tanggal_Pengeluaran'], '%Y-%m-%d').date()
    )
    db.session.add(pengeluaran)
    db.session.commit()
    return jsonify(pengeluaran.to_dict()), 201

@app.route('/api/pengeluaran/<int:id>', methods=['PUT'])
def update_pengeluaran(id):
    pengeluaran = Pengeluaran.query.get(id)
    if not pengeluaran:
        return jsonify({'error': 'Pengeluaran not found'}), 404
    
    data = request.json
    pengeluaran.Status = data.get('Status', pengeluaran.Status)
    
    db.session.commit()
    return jsonify(pengeluaran.to_dict())

@app.route('/api/pengeluaran/<int:id>', methods=['DELETE'])
def delete_pengeluaran(id):
    pengeluaran = Pengeluaran.query.get(id)
    if not pengeluaran:
        return jsonify({'error': 'Pengeluaran not found'}), 404
    
    db.session.delete(pengeluaran)
    db.session.commit()
    return jsonify({'message': 'Pengeluaran deleted'}), 200

# DASHBOARD
@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    total_penjualan = db.session.query(db.func.sum(Penjualan.Harga_Total)).scalar() or 0
    total_pengeluaran = db.session.query(db.func.sum(Pengeluaran.Jumlah)).scalar() or 0
    jumlah_pelanggan = Pelanggan.query.count()
    jumlah_transaksi = Penjualan.query.count()
    
    return jsonify({
        'total_penjualan': float(total_penjualan),
        'total_pengeluaran': float(total_pengeluaran),
        'keuntungan_bersih': float(total_penjualan - total_pengeluaran),
        'jumlah_pelanggan': jumlah_pelanggan,
        'jumlah_transaksi': jumlah_transaksi
    })

# ERROR HANDLER
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)