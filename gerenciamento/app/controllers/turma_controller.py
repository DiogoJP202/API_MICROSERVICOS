from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models.turma import Turma

turma_bp = Blueprint("turmas", __name__)

# 🔹 Listar todas as turmas
@turma_bp.route("/", methods=["GET"])
def listar_turmas():
    turmas = Turma.query.all()
    return jsonify([t.to_dict() for t in turmas]), 200

# 🔹 Buscar turma por ID
@turma_bp.route("/<int:id>", methods=["GET"])
def obter_turma(id):
    turma = Turma.query.get(id)
    if not turma:
        return jsonify({"erro": "Turma não encontrada"}), 404
    return jsonify(turma.to_dict()), 200

# 🔹 Criar nova turma
@turma_bp.route("/", methods=["POST"])
def criar_turma():
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
    turma = Turma.query.get(id)
    if not turma:
        return jsonify({"erro": "Turma não encontrada"}), 404

    db.session.delete(turma)
    db.session.commit()
    return jsonify({"mensagem": f"Turma {id} removida com sucesso"}), 200