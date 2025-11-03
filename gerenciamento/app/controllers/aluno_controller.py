from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models.aluno import Aluno

aluno_bp = Blueprint("alunos", __name__)

# 🔹 Listar todos os alunos
@aluno_bp.route("/", methods=["GET"])
def listar_alunos():
    alunos = Aluno.query.all()
    return jsonify([a.to_dict() for a in alunos]), 200

# 🔹 Buscar aluno por ID
@aluno_bp.route("/<int:id>", methods=["GET"])
def obter_aluno(id):
    aluno = Aluno.query.get(id)
    if not aluno:
        return jsonify({"erro": "Aluno não encontrado"}), 404
    return jsonify(aluno.to_dict()), 200

# 🔹 Criar novo aluno
@aluno_bp.route("/", methods=["POST"])
def criar_aluno():
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
    aluno = Aluno.query.get(id)
    if not aluno:
        return jsonify({"erro": "Aluno não encontrado"}), 404

    db.session.delete(aluno)
    db.session.commit()
    return jsonify({"mensagem": f"Aluno {id} removido com sucesso"}), 200
