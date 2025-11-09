from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models.professor import Professor

professor_bp = Blueprint("professores", __name__)

@professor_bp.route("/", methods=["GET"])
def listar_professores():
    """
    Listar todos os professores
    ---
    tags:
      - Professores
    summary: Lista todos os professores
    description: Retorna uma lista com todos os professores cadastrados.
    responses:
      200:
        description: Lista de professores
        schema:
          type: array
          items:
            $ref: '#/definitions/Professor'
    definitions:
      Professor:
        type: object
        properties:
          id:
            type: integer
            format: int32
            example: 1
          nome:
            type: string
            example: "João Pereira"
          materia:
            type: string
            example: "Matemática"
      ProfessorInput:
        type: object
        required:
          - nome
        properties:
          nome:
            type: string
            example: "João Pereira"
          materia:
            type: string
            example: "Matemática"
      ProfessorUpdate:
        type: object
        properties:
          nome:
            type: string
            example: "João Pereira"
          materia:
            type: string
            example: "Matemática"
      Error:
        type: object
        properties:
          erro:
            type: string
            example: "Professor não encontrado"
      Message:
        type: object
        properties:
          mensagem:
            type: string
            example: "Professor 1 removido com sucesso"
    """
    professores = Professor.query.all()
    return jsonify([p.to_dict() for p in professores])

@professor_bp.route("/<int:id>", methods=["GET"])
def obter_professor(id):
    """
    Buscar professor por ID
    ---
    tags:
      - Professores
    summary: Obtém um professor pelo ID
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID do professor
    responses:
      200:
        description: Professor encontrado
        schema:
          $ref: '#/definitions/Professor'
      404:
        description: Professor não encontrado
        schema:
          $ref: '#/definitions/Error'
    """
    professor = Professor.query.get(id)
    if not professor:
        return jsonify({"erro": "Professor não encontrado"}), 404
    return jsonify(professor.to_dict()), 200

@professor_bp.route("/", methods=["POST"])
def criar_professor():
    """
    Criar novo professor
    ---
    tags:
      - Professores
    summary: Cria um novo professor
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/ProfessorInput'
    responses:
      201:
        description: Professor criado com sucesso
        schema:
          $ref: '#/definitions/Professor'
      400:
        description: Requisição inválida
        schema:
          $ref: '#/definitions/Error'
    """
    data = request.get_json()
    if not data or "nome" not in data:
        return jsonify({"erro": "Campo 'nome' é obrigatório"}), 400
    novo = Professor(nome=data["nome"], materia=data.get("materia"))
    db.session.add(novo)
    db.session.commit()
    return jsonify(novo.to_dict()), 201

@professor_bp.route("/<int:id>", methods=["PUT"])
def atualizar_professor(id):
    """
    Atualizar professor existente
    ---
    tags:
      - Professores
    summary: Atualiza os dados de um professor
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID do professor
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/ProfessorUpdate'
    responses:
      200:
        description: Professor atualizado com sucesso
        schema:
          $ref: '#/definitions/Professor'
      404:
        description: Professor não encontrado
        schema:
          $ref: '#/definitions/Error'
    """
    professor = Professor.query.get(id)
    if not professor:
        return jsonify({"erro": "Professor não encontrado"}), 404

    data = request.get_json()
    if "nome" in data:
        professor.nome = data["nome"]
    if "materia" in data:
        professor.materia = data["materia"]

    db.session.commit()
    return jsonify(professor.to_dict()), 200

# 🔹 Deletar professor
@professor_bp.route("/<int:id>", methods=["DELETE"])
def deletar_professor(id):
    """
    Deletar professor
    ---
    tags:
      - Professores
    summary: Remove um professor pelo ID
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID do professor
    responses:
      200:
        description: Professor removido com sucesso
        schema:
          $ref: '#/definitions/Message'
      404:
        description: Professor não encontrado
        schema:
          $ref: '#/definitions/Error'
    """
    professor = Professor.query.get(id)
    if not professor:
        return jsonify({"erro": "Professor não encontrado"}), 404

    db.session.delete(professor)
    db.session.commit()
    return jsonify({"mensagem": f"Professor {id} removido com sucesso"}), 200
