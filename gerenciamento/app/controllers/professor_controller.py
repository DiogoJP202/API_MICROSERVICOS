from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models.professor import Professor

professor_bp = Blueprint("professores", __name__)

@professor_bp.route("/", methods=["GET"])
def listar_professores():
    professores = Professor.query.all()
    return jsonify([p.to_dict() for p in professores])

@professor_bp.route("/<int:id>", methods=["GET"])
def obter_professor(id):
    professor = Professor.query.get(id)
    if not professor:
        return jsonify({"erro": "Professor não encontrado"}), 404
    return jsonify(professor.to_dict()), 200

@professor_bp.route("/", methods=["POST"])
def criar_professor():
    data = request.get_json()
    if not data or "nome" not in data:
        return jsonify({"erro": "Campo 'nome' é obrigatório"}), 400
    novo = Professor(nome=data["nome"], materia=data.get("materia"))
    db.session.add(novo)
    db.session.commit()
    return jsonify(novo.to_dict()), 201

@professor_bp.route("/<int:id>", methods=["PUT"])
def atualizar_professor(id):
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
    professor = Professor.query.get(id)
    if not professor:
        return jsonify({"erro": "Professor não encontrado"}), 404

    db.session.delete(professor)
    db.session.commit()
    return jsonify({"mensagem": f"Professor {id} removido com sucesso"}), 200
