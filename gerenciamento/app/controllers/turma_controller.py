from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models.turma import Turma

turma_bp = Blueprint("turmas", __name__)

# 🔹 Listar todas as turmas
@turma_bp.route("/", methods=["GET"])
def listar_turmas():
    """
    Listar todas as turmas
    ---
    tags:
      - Turmas
    summary: Lista todas as turmas
    description: Retorna uma lista com todas as turmas cadastradas.
    responses:
      200:
        description: Lista de turmas
        schema:
          type: array
          items:
            $ref: '#/definitions/Turma'
    definitions:
      Turma:
        type: object
        properties:
          id:
            type: integer
            format: int32
            example: 1
          nome:
            type: string
            example: "Turma A"
          professor_id:
            type: integer
            format: int32
            nullable: true
            example: 5
      TurmaInput:
        type: object
        required:
          - nome
        properties:
          nome:
            type: string
            example: "Turma A"
          professor_id:
            type: integer
            format: int32
            example: 5
      TurmaUpdate:
        type: object
        properties:
          nome:
            type: string
            example: "Turma A"
          professor_id:
            type: integer
            format: int32
            example: 5
      Error:
        type: object
        properties:
          erro:
            type: string
            example: "Turma não encontrada"
      Message:
        type: object
        properties:
          mensagem:
            type: string
            example: "Turma 1 removida com sucesso"
    """
    turmas = Turma.query.all()
    return jsonify([t.to_dict() for t in turmas]), 200

# 🔹 Buscar turma por ID
@turma_bp.route("/<int:id>", methods=["GET"])
def obter_turma(id):
    """
    Buscar turma por ID
    ---
    tags:
      - Turmas
    summary: Obtém uma turma pelo ID
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID da turma
    responses:
      200:
        description: Turma encontrada
        schema:
          $ref: '#/definitions/Turma'
      404:
        description: Turma não encontrada
        schema:
          $ref: '#/definitions/Error'
    """
    turma = Turma.query.get(id)
    if not turma:
        return jsonify({"erro": "Turma não encontrada"}), 404
    return jsonify(turma.to_dict()), 200

# 🔹 Criar nova turma
@turma_bp.route("/", methods=["POST"])
def criar_turma():
    """
    Criar nova turma
    ---
    tags:
      - Turmas
    summary: Cria uma nova turma
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/TurmaInput'
    responses:
      201:
        description: Turma criada com sucesso
        schema:
          $ref: '#/definitions/Turma'
      400:
        description: Requisição inválida
        schema:
          $ref: '#/definitions/Error'
    """
    data = request.get_json()
    if not data or "nome" not in data:
        return jsonify({"erro": "Campo 'nome' é obrigatório"}), 400

    nova_turma = Turma(
        nome=data["nome"],
        professor_id=data.get("professor_id")
    )
    db.session.add(nova_turma)
    db.session.commit()
    return jsonify(nova_turma.to_dict()), 201

# 🔹 Atualizar turma existente
@turma_bp.route("/<int:id>", methods=["PUT"])
def atualizar_turma(id):
    """
    Atualizar turma existente
    ---
    tags:
      - Turmas
    summary: Atualiza os dados de uma turma
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID da turma
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/TurmaUpdate'
    responses:
      200:
        description: Turma atualizada com sucesso
        schema:
          $ref: '#/definitions/Turma'
      404:
        description: Turma não encontrada
        schema:
          $ref: '#/definitions/Error'
    """
    turma = Turma.query.get(id)
    if not turma:
        return jsonify({"erro": "Turma não encontrada"}), 404

    data = request.get_json()
    if "nome" in data:
        turma.nome = data["nome"]
    if "professor_id" in data:
        turma.professor_id = data["professor_id"]

    db.session.commit()
    return jsonify(turma.to_dict()), 200

# 🔹 Deletar turma
@turma_bp.route("/<int:id>", methods=["DELETE"])
def deletar_turma(id):
    """
    Deletar turma
    ---
    tags:
      - Turmas
    summary: Remove uma turma pelo ID
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID da turma
    responses:
      200:
        description: Turma removida com sucesso
        schema:
          $ref: '#/definitions/Message'
      404:
        description: Turma não encontrada
        schema:
          $ref: '#/definitions/Error'
    """
    turma = Turma.query.get(id)
    if not turma:
        return jsonify({"erro": "Turma não encontrada"}), 404

    db.session.delete(turma)
    db.session.commit()
    return jsonify({"mensagem": f"Turma {id} removida com sucesso"}), 200
