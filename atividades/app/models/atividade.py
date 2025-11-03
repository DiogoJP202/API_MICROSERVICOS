from app.extensions import db

class Atividade(db.Model):
    __tablename__ = "atividades"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255))
    nota = db.Column(db.Float)
    professor_id = db.Column(db.Integer, nullable=False)
    turma_id = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "nota": self.nota,
            "professor_id": self.professor_id,
            "turma_id": self.turma_id
        }   