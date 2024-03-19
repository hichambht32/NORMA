from api.connection import db

class codification(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(10), nullable=False, unique=True)
    name = db.Column(db.String(1000))
    category = db.Column(db.String(1000))
    

class Importers(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(10), db.ForeignKey('codification.code'), nullable=False)

class Exporters(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(10), db.ForeignKey('codification.code'), nullable=False)

class AccordConvention(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    country = db.Column(db.String(255), nullable=False)
    agreement = db.Column(db.String(255), nullable=False)
    di_percentage = db.Column(db.String(255), nullable=False)
    tpi_percentage = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(10), db.ForeignKey('codification.code'), nullable=False)

class DocumentRequired(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    document_number = db.Column(db.String(255), nullable=False)
    document_name = db.Column(db.String(255), nullable=False)
    libelle_d_extrait = db.Column(db.String(255))
    issuer = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(10), db.ForeignKey('codification.code'), nullable=False)

class ImportDuty(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    DI = db.Column(db.String(255), nullable=False)
    TPI = db.Column(db.String(255), nullable=False)
    TVA = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(10), db.ForeignKey('codification.code'), nullable=False)

class AnnualImport(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.String(255), nullable=False)
    weight = db.Column(db.String(255), nullable=False)
    value = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(10), db.ForeignKey('codification.code'), nullable=False)

class AnnualExport(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.String(255), nullable=False)
    weight = db.Column(db.String(255), nullable=False)
    value = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(10), db.ForeignKey('codification.code'), nullable=False)

class Clients(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    country = db.Column(db.String(255), nullable=False)
    value = db.Column(db.String(255), nullable=False) 
    weight = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(10), db.ForeignKey('codification.code'), nullable=False)

class Fournisseurs(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    country = db.Column(db.String(255), nullable=False)
    value = db.Column(db.String(255), nullable=False) 
    weight = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(10), db.ForeignKey('codification.code'), nullable=False)

