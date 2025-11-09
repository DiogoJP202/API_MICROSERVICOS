from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models.reserva import Reserva
import requests
import os

reserva_bp = Blueprint("reservas", __name__)

GERENCIAMENTO_URL = os.getenv("GERENCIAMENTO_URL", "http://localhost:8001/api/turmas")

@reserva_bp.route("/", methods=["GET"])
def listar_reservas():
    """
    Lista todas as reservas
    ---
    tags:
      - Reservas
    responses:
      200:
        description: Lista de reservas
        schema:
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
    reservas = Reserva.query.all()
    return jsonify([r.to_dict() for r in reservas])

@reserva_bp.route("/<int:id>", methods=["GET"])
def obter_reserva(id):
    """
    Obtém uma reserva pelo ID
    ---
    tags:
      - Reservas
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID da reserva
    responses:
      200:
        description: Reserva encontrada
        schema:
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
      404:
        description: Reserva não encontrada
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Reserva não encontrada
    """
    reserva = Reserva.query.get(id)
    if not reserva:
        return jsonify({"erro": "Reserva não encontrada"}), 404
    return jsonify(reserva.to_dict()), 200

@reserva_bp.route("/", methods=["POST"])
def criar_reserva():
    """
    Cria uma nova reserva
    ---
    tags:
      - Reservas
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        description: Dados da reserva a ser criada
        schema:
          type: object
          required: [sala, data_reserva, turma_id]
          properties:
            sala:
              type: string
              example: LAB-101
            data_reserva:
              type: string
              format: date
              example: 2025-01-15
            turma_id:
              type: integer
              example: 42
    responses:
      201:
        description: Reserva criada com sucesso
        schema:
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
      400:
        description: Requisição inválida ou turma não encontrada
        schema:
          type: object
          properties:
            erro:
              type: string
      500:
        description: Erro ao comunicar com o serviço de gerenciamento
        schema:
          type: object
          properties:
            erro:
              type: string
    """
    data = request.get_json()
    if not data or "sala" not in data or "data_reserva" not in data or "turma_id" not in data:
        return jsonify({"erro": "Campos obrigatórios: sala, data_reserva, turma_id"}), 400

    turma_id = data["turma_id"]

    # valida se a turma existe no serviço de gerenciamento
    try:
        response = requests.get(f"{GERENCIAMENTO_URL}/{turma_id}")
        if response.status_code != 200:
            return jsonify({"erro": f"Turma {turma_id} não encontrada no serviço de gerenciamento."}), 400
    except requests.exceptions.RequestException:
        return jsonify({"erro": "Falha ao conectar ao serviço de gerenciamento."}), 500

    nova = Reserva(
        sala=data["sala"],
        data_reserva=data["data_reserva"],
        turma_id=turma_id
    )

    db.session.add(nova)
    db.session.commit()
    return jsonify(nova.to_dict()), 201

@reserva_bp.route("/<int:id>", methods=["PUT"])
def atualizar_reserva(id):
    """
    Atualiza uma reserva existente
    ---
    tags:
      - Reservas
    consumes:
      - application/json
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID da reserva
      - in: body
        name: body
        required: true
        description: Campos a serem atualizados
        schema:
          type: object
          properties:
            sala:
              type: string
              example: LAB-202
            data_reserva:
              type: string
              format: date
              example: 2025-02-20
            turma_id:
              type: integer
              example: 77
    responses:
      200:
        description: Reserva atualizada com sucesso
        schema:
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
      400:
        description: Requisição inválida ou turma não encontrada
        schema:
          type: object
          properties:
            erro:
              type: string
      404:
        description: Reserva não encontrada
        schema:
          type: object
          properties:
            erro:
              type: string
      500:
        description: Erro ao comunicar com o serviço de gerenciamento
        schema:
          type: object
          properties:
            erro:
              type: string
    """
    reserva = Reserva.query.get(id)
    if not reserva:
        return jsonify({"erro": "Reserva não encontrada"}), 404

    data = request.get_json()
    if "sala" in data:
        reserva.sala = data["sala"]
    if "data_reserva" in data:
        reserva.data_reserva = data["data_reserva"]
    if "turma_id" in data:
        try:
            turma = requests.get(f"{GERENCIAMENTO_URL}/turmas/{data['turma_id']}")
            if turma.status_code != 200:
                return jsonify({"erro": f"Turma {data['turma_id']} não encontrada."}), 400
            reserva.turma_id = data["turma_id"]
        except requests.exceptions.RequestException:
            return jsonify({"erro": "Falha ao conectar ao serviço de gerenciamento."}), 500

    db.session.commit()
    return jsonify(reserva.to_dict()), 200

@reserva_bp.route("/<int:id>", methods=["DELETE"])
def deletar_reserva(id):
    """
    Remove uma reserva pelo ID
    ---
    tags:
      - Reservas
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID da reserva
    responses:
      200:
        description: Reserva removida com sucesso
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: Reserva 1 removida com sucesso
      404:
        description: Reserva não encontrada
        schema:
          type: object
          properties:
            erro:
              type: string
    """
    reserva = Reserva.query.get(id)
    if not reserva:
        return jsonify({"erro": "Reserva não encontrada"}), 404

    db.session.delete(reserva)
    db.session.commit()
    return jsonify({"mensagem": f"Reserva {id} removida com sucesso"}), 200
