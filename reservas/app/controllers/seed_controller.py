from flask import Blueprint, jsonify
from app.extensions import db
from app.models.reserva import Reserva

seed_bp = Blueprint("seed", __name__)

@seed_bp.route("/seed", methods=["POST"])
def seed_data():
    """
    Reseta o banco e cria dados de exemplo
    ---
    tags:
      - Reservas
    summary: Popular banco de reservas com dados de exemplo
    description: Remove e recria as tabelas e insere reservas de exemplo para uso em desenvolvimento/testes.
    responses:
      201:
        description: Banco populado com sucesso
        schema:
          type: object
          properties:
            message:
              type: string
              example: Banco de reservas populado!
            reservas:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  sala:
                    type: string
                  data_reserva:
                    type: string
                    format: date
                  turma_id:
                    type: integer
    """
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
