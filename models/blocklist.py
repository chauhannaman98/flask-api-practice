from db import db

class BLocklistModel(db.Model):
    __tablename__ = 'blocklist'

    jti = db.Column(db.String(80), primary_key=True, unique=True, nullable=False)