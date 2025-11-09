from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models.atividade import Atividade
import requests
import os

atividade_bp = Blueprint("atividades", __name__)

# variáveis de ambiente definidas no docker-compose
GERENCIAMENTO_URL = os.getenv("GERENCIAMENTO_URL", "http://localhost:8001/api")

@atividade_bp.route("/", methods=["GET"])
def listar_atividades():
    """
    Listar todas as atividades
    ---
    tags:
      - Atividades
    summary: Lista todas as atividades
    description: Retorna uma lista com todas as atividades cadastradas.
    responses:
      200:
        description: Lista de atividades
        schema:
          type: array
          items:
            $ref: '#/definitions/Atividade'
    definitions:
      Atividade:
        type: object
        properties:
          id:
            type: integer
            example: 1
          titulo:
            type: string
            example: Trabalho 1
          descricao:
            type: string
            example: Entregar até sexta
          nota:
            type: number
            format: float
            example: 9.5
          professor_id:
            type: integer
            example: 2
          turma_id:
            type: integer
            example: 1
      AtividadeInput:
        type: object
        required:
          - titulo
          - professor_id
          - turma_id
        properties:
          titulo:
            type: string
            example: Trabalho 1
          descricao:
            type: string
            example: Entregar até sexta
          nota:
            type: number
            format: float
            example: 9.5
          professor_id:
            type: integer
            example: 2
          turma_id:
            type: integer
            example: 1
      AtividadeUpdate:
        type: object
        properties:
          titulo:
            type: string
            example: Trabalho 1 (revisto)
          descricao:
            type: string
            example: Nova descrição
          nota:
            type: number
            format: float
            example: 8.0
      Error:
        type: object
        properties:
          erro:
            type: string
            example: Atividade não encontrada
      Message:
        type: object
        properties:
          mensagem:
            type: string
            example: Atividade 1 removida com sucesso
    """
    atividades = Atividade.query.all()
    return jsonify([a.to_dict() for a in atividades])

@atividade_bp.route("/<int:id>", methods=["GET"])
def obter_atividade(id):
    """
    Buscar atividade por ID
    ---
    tags:
      - Atividades
    summary: Obtém uma atividade pelo ID
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID da atividade
    responses:
      200:
        description: Atividade encontrada
        schema:
          $ref: '#/definitions/Atividade'
      404:
        description: Atividade não encontrada
        schema:
          $ref: '#/definitions/Error'
    """
    atividade = Atividade.query.get(id)
    if not atividade:
        return jsonify({"erro": "Atividade não encontrada"}), 404
    return jsonify(atividade.to_dict()), 200

@atividade_bp.route("/", methods=["POST"])
def criar_atividade():
    """
    Criar nova atividade
    ---
    tags:
      - Atividades
    summary: Cria uma nova atividade
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/AtividadeInput'
    responses:
      201:
        description: Atividade criada com sucesso
        schema:
          $ref: '#/definitions/Atividade'
      400:
        description: Validação falhou (campos obrigatórios ou IDs não encontrados)
        schema:
          $ref: '#/definitions/Error'
      500:
        description: Erro ao contatar serviço de gerenciamento
        schema:
          $ref: '#/definitions/Error'
    """
    data = request.get_json()
    campos = ["titulo", "professor_id", "turma_id"]
    if not data or not all(c in data for c in campos):
        return jsonify({"erro": f"Campos obrigatórios: {', '.join(campos)}"}), 400

    professor_id = data["professor_id"]
    turma_id = data["turma_id"]

    # valida professor
    try:
        r_prof = requests.get(f"{GERENCIAMENTO_URL}/professores/{professor_id}")
        if r_prof.status_code != 200:
            return jsonify({"erro": f"Professor {professor_id} não encontrado."}), 400
    except requests.exceptions.RequestException:
        return jsonify({"erro": "Falha ao conectar ao serviço de gerenciamento (professores)."}), 500

    # valida turma
    try:
        r_turma = requests.get(f"{GERENCIAMENTO_URL}/turmas/{turma_id}")
        if r_turma.status_code != 200:
            return jsonify({"erro": f"Turma {turma_id} não encontrada."}), 400
    except requests.exceptions.RequestException:
        return jsonify({"erro": "Falha ao conectar ao serviço de gerenciamento (turmas)."}), 500

    nova = Atividade(
        titulo=data["titulo"],
        descricao=data.get("descricao"),
        nota=data.get("nota"),
        professor_id=professor_id,
        turma_id=turma_id
    )

    db.session.add(nova)
    db.session.commit()
    return jsonify(nova.to_dict()), 201

@atividade_bp.route("/<int:id>", methods=["PUT"])
def atualizar_atividade(id):
    """
    Atualizar atividade existente
    ---
    tags:
      - Atividades
    summary: Atualiza os dados de uma atividade
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID da atividade
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/AtividadeUpdate'
    responses:
      200:
        description: Atividade atualizada com sucesso
        schema:
          $ref: '#/definitions/Atividade'
      404:
        description: Atividade não encontrada
        schema:
          $ref: '#/definitions/Error'
    """
    atividade = Atividade.query.get(id)
    if not atividade:
        return jsonify({"erro": "Atividade não encontrada"}), 404

    data = request.get_json()
    if "titulo" in data:
        atividade.titulo = data["titulo"]
    if "descricao" in data:
        atividade.descricao = data["descricao"]
    if "nota" in data:
        atividade.nota = data["nota"]

    db.session.commit()
    return jsonify(atividade.to_dict()), 200

@atividade_bp.route("/<int:id>", methods=["DELETE"])
def deletar_atividade(id):
    """
    Deletar atividade
    ---
    tags:
      - Atividades
    summary: Remove uma atividade pelo ID
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID da atividade
    responses:
      200:
        description: Atividade removida com sucesso
        schema:
          $ref: '#/definitions/Message'
      404:
        description: Atividade não encontrada
        schema:
          $ref: '#/definitions/Error'
    """
    atividade = Atividade.query.get(id)
    if not atividade:
        return jsonify({"erro": "Atividade não encontrada"}), 404

    db.session.delete(atividade)
    db.session.commit()
    return jsonify({"mensagem": f"Atividade {id} removida com sucesso"}), 200
