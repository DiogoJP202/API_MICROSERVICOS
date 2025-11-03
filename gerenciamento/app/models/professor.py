from app.extensions import db

class Professor(db.Model):
    __tablename__ = 'professores'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    materia = db.Column(db.String(100))

    def to_dict(self):
        return {"id": self.id, "nome": self.nome, "materia": self.materia}