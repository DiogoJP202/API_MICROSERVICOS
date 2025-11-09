from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models.nota import Nota
from app.models.atividade import Atividade
import requests
import os

nota_bp = Blueprint("notas", __name__)

GERENCIAMENTO_URL = os.getenv("GERENCIAMENTO_URL", "http://localhost:8001/api")

# 🔹 Listar todas as notas
@nota_bp.route("/", methods=["GET"])
def listar_notas():
    """
    Listar todas as notas
    ---
    tags:
      - Notas
    summary: Lista todas as notas
    description: Retorna uma lista com todas as notas cadastradas.
    responses:
      200:
        description: Lista de notas
        schema:
          type: array
          items:
            $ref: '#/definitions/Nota'
    definitions:
      Nota:
        type: object
        properties:
          id:
            type: integer
            example: 1
          valor:
            type: number
            format: float
            example: 8.5
          aluno_id:
            type: integer
            example: 3
          atividade_id:
            type: integer
            example: 10
      NotaInput:
        type: object
        required:
          - valor
          - aluno_id
          - atividade_id
        properties:
          valor:
            type: number
            format: float
            example: 8.5
          aluno_id:
            type: integer
            example: 3
          atividade_id:
            type: integer
            example: 10
      NotaUpdate:
        type: object
        properties:
          valor:
            type: number
            format: float
            example: 9.0
      Error:
        type: object
        properties:
          erro:
            type: string
            example: Nota não encontrada
      Message:
        type: object
        properties:
          mensagem:
            type: string
            example: Nota 1 removida com sucesso
    """
    notas = Nota.query.all()
    return jsonify([n.to_dict() for n in notas]), 200

# 🔹 Buscar nota por ID
@nota_bp.route("/<int:id>", methods=["GET"])
def obter_nota(id):
    """
    Buscar nota por ID
    ---
    tags:
      - Notas
    summary: Obtém uma nota pelo ID
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID da nota
    responses:
      200:
        description: Nota encontrada
        schema:
          $ref: '#/definitions/Nota'
      404:
        description: Nota não encontrada
        schema:
          $ref: '#/definitions/Error'
    """
    nota = Nota.query.get(id)
    if not nota:
        return jsonify({"erro": "Nota não encontrada"}), 404
    return jsonify(nota.to_dict()), 200

@nota_bp.route("/", methods=["POST"])
def criar_nota():
    """
    Criar nova nota
    ---
    tags:
      - Notas
    summary: Cria uma nova nota
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/NotaInput'
    responses:
      201:
        description: Nota criada com sucesso
        schema:
          $ref: '#/definitions/Nota'
      400:
        description: Validação falhou (campos obrigatórios/IDs inválidos)
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Erro ao contatar serviço de gerenciamento
        schema:
          $ref: '#/definitions/Error'
    """
    data = request.get_json()
    campos = ["valor", "aluno_id", "atividade_id"]

    if not data or not all(c in data for c in campos):
        return jsonify({"erro": f"Campos obrigatórios: {', '.join(campos)}"}), 400

    aluno_id = data["aluno_id"]
    atividade_id = data["atividade_id"]

    # valida aluno (no Gerenciamento)
    try:
        r_aluno = requests.get(f"{GERENCIAMENTO_URL}/alunos/{aluno_id}")
        if r_aluno.status_code != 200:
            return jsonify({"erro": f"Aluno {aluno_id} não encontrado."}), 400
    except requests.exceptions.RequestException:
        return jsonify({"erro": "Falha ao conectar ao serviço de gerenciamento (alunos)."}), 500

    # ✅ valida atividade localmente (sem HTTP)
    atividade = Atividade.query.get(atividade_id)
    if not atividade:
        return jsonify({"erro": f"Atividade {atividade_id} não encontrada."}), 400

    nova = Nota(
        valor=data["valor"],
        aluno_id=aluno_id,
        atividade_id=atividade_id
    )
    db.session.add(nova)
    db.session.commit()
    return jsonify(nova.to_dict()), 201

# 🔹 Atualizar nota
@nota_bp.route("/<int:id>", methods=["PUT"])
def atualizar_nota(id):
    """
    Atualizar nota existente
    ---
    tags:
      - Notas
    summary: Atualiza os dados de uma nota
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID da nota
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/NotaUpdate'
    responses:
      200:
        description: Nota atualizada com sucesso
        schema:
          $ref: '#/definitions/Nota'
      404:
        description: Nota não encontrada
        schema:
          $ref: '#/definitions/Error'
    """
    nota = Nota.query.get(id)
    if not nota:
        return jsonify({"erro": "Nota não encontrada"}), 404

    data = request.get_json()
    if "valor" in data:
        nota.valor = data["valor"]

    db.session.commit()
    return jsonify(nota.to_dict()), 200

# 🔹 Deletar nota
@nota_bp.route("/<int:id>", methods=["DELETE"])
def deletar_nota(id):
    """
    Deletar nota
    ---
    tags:
      - Notas
    summary: Remove uma nota pelo ID
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID da nota
    responses:
      200:
        description: Nota removida com sucesso
        schema:
          $ref: '#/definitions/Message'
      404:
        description: Nota não encontrada
        schema:
          $ref: '#/definitions/Error'
    """
    nota = Nota.query.get(id)
    if not nota:
        return jsonify({"erro": "Nota não encontrada"}), 404

    db.session.delete(nota)
    db.session.commit()
    return jsonify({"mensagem": f"Nota {id} removida com sucesso"}), 200
