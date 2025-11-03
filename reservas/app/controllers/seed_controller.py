from flask import Blueprint, jsonify
from app.extensions import db
from app.models.reserva import Reserva

seed_bp = Blueprint("seed", __name__)

@seed_bp.route("/seed", methods=["POST"])
def seed_data():
    db.drop_all()
    db.create_all()

    reservas = [
        Reserva(sala="Sala 101", data_reserva="2025-11-20", turma_id=1),
        Reserva(sala="Sala 202", data_reserva="2025-11-21", turma_id=2),
    ]
    db.session.add_all(reservas)
    db.session.commit()

    return jsonify({
        "message": "Banco de reservas populado!",
        "reservas": [r.to_dict() for r in Reserva.query.all()]
    }), 201
