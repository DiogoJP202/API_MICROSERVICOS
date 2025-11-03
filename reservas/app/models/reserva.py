from app.extensions import db

class Reserva(db.Model):
    __tablename__ = "reservas"

    id = db.Column(db.Integer, primary_key=True)
    sala = db.Column(db.String(100), nullable=False)
    data_reserva = db.Column(db.String(20), nullable=False)
    turma_id = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "sala": self.sala,
            "data_reserva": self.data_reserva,
            "turma_id": self.turma_id
        }