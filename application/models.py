from application import db

class Table(db.Model):
    id = db.Columns(db.Integer, primary_key=True)
    name = db.Columns(db.String(30), default='ABC')

    def __str__(self):
        return self.id