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
    notas = Nota.query.all()
    return jsonify([n.to_dict() for n in notas]), 200

# 🔹 Buscar nota por ID
@nota_bp.route("/<int:id>", methods=["GET"])
def obter_nota(id):
    nota = Nota.query.get(id)
    if not nota:
        return jsonify({"erro": "Nota não encontrada"}), 404
    return jsonify(nota.to_dict()), 200

@nota_bp.route("/", methods=["POST"])
def criar_nota():
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
    nota = Nota.query.get(id)
    if not nota:
        return jsonify({"erro": "Nota não encontrada"}), 404

    db.session.delete(nota)
    db.session.commit()
    return jsonify({"mensagem": f"Nota {id} removida com sucesso"}), 200