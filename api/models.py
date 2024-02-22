from api.connection import db

class codification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    importers = db.relationship('Importers', backref='codification', lazy=True)
    exporters = db.relationship('Exporters', backref='codification', lazy=True)
    accord_conventions = db.relationship('AccordConvention', backref='codification', lazy=True)
    document_requireds = db.relationship('DocumentRequired', backref='codification', lazy=True)
    import_duties = db.relationship('ImportDuty', backref='codification', lazy=True)
    annual_imports = db.relationship('AnnualImport', backref='codification', lazy=True)
    annual_export = db.relationship('AnnualExport', backref='codification', lazy=True)
    clients = db.relationship('Clients', backref='codification', lazy=True)
    fournisseurs = db.relationship('Fournisseurs', backref='codification', lazy=True)

class Importers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    codification_id = db.Column(db.Integer, db.ForeignKey('codification.id'), nullable=False)

class Exporters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    codification_id = db.Column(db.Integer, db.ForeignKey('codification.id'), nullable=False)

class AccordConvention(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(255), nullable=False)
    agreement = db.Column(db.String(255), nullable=False)
    di_percentage = db.Column(db.String(255), nullable=False)
    tpi_percentage = db.Column(db.String(255), nullable=False)
    codification_id = db.Column(db.Integer, db.ForeignKey('codification.id'), nullable=False)

class DocumentRequired(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_number = db.Column(db.String(255), nullable=False)
    document_name = db.Column(db.String(255), nullable=False)
    libelle_d_extrait = db.Column(db.String(255), nullable=False)
    issuer = db.Column(db.String(255), nullable=False)
    codification_id = db.Column(db.Integer, db.ForeignKey('codification.id'), nullable=False)

class ImportDuty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    DI = db.Column(db.String(255), nullable=False)
    TPI = db.Column(db.String(255), nullable=False)
    TVA = db.Column(db.String(255), nullable=False)
    codification_id = db.Column(db.Integer, db.ForeignKey('codification.id'), nullable=False)

class AnnualImport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(255), nullable=False)
    weight = db.Column(db.String(255), nullable=False)
    value = db.Column(db.String(255), nullable=False)
    codification_id = db.Column(db.Integer, db.ForeignKey('codification.id'), nullable=False)

class AnnualExport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(255), nullable=False)
    weight = db.Column(db.String(255), nullable=False)
    value = db.Column(db.String(255), nullable=False)
    codification_id = db.Column(db.Integer, db.ForeignKey('codification.id'), nullable=False)

class Clients(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(255), nullable=False)
    value = db.Column(db.String(255), nullable=False) 
    weight = db.Column(db.String(255), nullable=False)
    codification_id = db.Column(db.Integer, db.ForeignKey('codification.id'), nullable=False)

class Fournisseurs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(255), nullable=False)
    value = db.Column(db.String(255), nullable=False) 
    weight = db.Column(db.String(255), nullable=False)
    codification_id = db.Column(db.Integer, db.ForeignKey('codification.id'), nullable=False)
