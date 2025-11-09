from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models.aluno import Aluno

aluno_bp = Blueprint("alunos", __name__)

# 🔹 Listar todos os alunos
@aluno_bp.route("/", methods=["GET"])
def listar_alunos():
    """
    Listar todos os alunos
    ---
    tags:
      - Alunos
    summary: Lista todos os alunos
    description: Retorna uma lista com todos os alunos cadastrados.
    responses:
      200:
        description: Lista de alunos
        schema:
          type: array
          items:
            $ref: '#/definitions/Aluno'
    definitions:
      Aluno:
        type: object
        properties:
          id:
            type: integer
            format: int32
            example: 1
          nome:
            type: string
            example: "Maria Silva"
          turma_id:
            type: integer
            format: int32
            nullable: true
            example: 10
      AlunoInput:
        type: object
        required:
          - nome
        properties:
          nome:
            type: string
            example: "Maria Silva"
          turma_id:
            type: integer
            format: int32
            example: 10
      AlunoUpdate:
        type: object
        properties:
          nome:
            type: string
            example: "Maria Silva"
          turma_id:
            type: integer
            format: int32
            example: 10
      Error:
        type: object
        properties:
          erro:
            type: string
            example: "Aluno não encontrado"
      Message:
        type: object
        properties:
          mensagem:
            type: string
            example: "Aluno 1 removido com sucesso"
    """
    alunos = Aluno.query.all()
    return jsonify([a.to_dict() for a in alunos]), 200

# 🔹 Buscar aluno por ID
@aluno_bp.route("/<int:id>", methods=["GET"])
def obter_aluno(id):
    """
    Buscar aluno por ID
    ---
    tags:
      - Alunos
    summary: Obtém um aluno pelo ID
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID do aluno
    responses:
      200:
        description: Aluno encontrado
        schema:
          $ref: '#/definitions/Aluno'
      404:
        description: Aluno não encontrado
        schema:
          $ref: '#/definitions/Error'
    """
    aluno = Aluno.query.get(id)
    if not aluno:
        return jsonify({"erro": "Aluno não encontrado"}), 404
    return jsonify(aluno.to_dict()), 200

# 🔹 Criar novo aluno
@aluno_bp.route("/", methods=["POST"])
def criar_aluno():
    """
    Criar novo aluno
    ---
    tags:
      - Alunos
    summary: Cria um novo aluno
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/AlunoInput'
    responses:
      201:
        description: Aluno criado com sucesso
        schema:
          $ref: '#/definitions/Aluno'
      400:
        description: Requisição inválida
        schema:
          $ref: '#/definitions/Error'
    """
    data = request.get_json()
    if not data or "nome" not in data:
        return jsonify({"erro": "Campo 'nome' é obrigatório"}), 400

    novo_aluno = Aluno(
        nome=data["nome"],
        turma_id=data.get("turma_id")
    )
    db.session.add(novo_aluno)
    db.session.commit()
    return jsonify(novo_aluno.to_dict()), 201

# 🔹 Atualizar aluno existente
@aluno_bp.route("/<int:id>", methods=["PUT"])
def atualizar_aluno(id):
    """
    Atualizar aluno existente
    ---
    tags:
      - Alunos
    summary: Atualiza os dados de um aluno
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID do aluno
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/AlunoUpdate'
    responses:
      200:
        description: Aluno atualizado com sucesso
        schema:
          $ref: '#/definitions/Aluno'
      404:
        description: Aluno não encontrado
        schema:
          $ref: '#/definitions/Error'
    """
    aluno = Aluno.query.get(id)
    if not aluno:
        return jsonify({"erro": "Aluno não encontrado"}), 404

    data = request.get_json()
    if "nome" in data:
        aluno.nome = data["nome"]
    if "turma_id" in data:
        aluno.turma_id = data["turma_id"]

    db.session.commit()
    return jsonify(aluno.to_dict()), 200

# 🔹 Deletar aluno
@aluno_bp.route("/<int:id>", methods=["DELETE"])
def deletar_aluno(id):
    """
    Deletar aluno
    ---
    tags:
      - Alunos
    summary: Remove um aluno pelo ID
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID do aluno
    responses:
      200:
        description: Aluno removido com sucesso
        schema:
          $ref: '#/definitions/Message'
      404:
        description: Aluno não encontrado
        schema:
          $ref: '#/definitions/Error'
    """
    aluno = Aluno.query.get(id)
    if not aluno:
        return jsonify({"erro": "Aluno não encontrado"}), 404

    db.session.delete(aluno)
    db.session.commit()
    return jsonify({"mensagem": f"Aluno {id} removido com sucesso"}), 200
