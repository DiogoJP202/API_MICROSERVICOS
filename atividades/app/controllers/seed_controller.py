from flask import Blueprint, jsonify
from app.extensions import db
from app.models.atividade import Atividade
from app.models.nota import Nota

seed_bp = Blueprint("seed", __name__)

@seed_bp.route("/seed", methods=["POST"])
def seed_data():
    db.drop_all()
    db.create_all()

    atv1 = Atividade(titulo="Prova de Matemática", descricao="Geometria Espacial", nota=8.5, professor_id=1, turma_id=1)
    atv2 = Atividade(titulo="Redação", descricao="Tema: Meio Ambiente", nota=9.0, professor_id=2, turma_id=2)

    db.session.add_all([atv1, atv2])
    db.session.commit()

    notas = [
        Nota(valor=9.5, aluno_id=1, atividade_id=atv1.id),
        Nota(valor=8.0, aluno_id=2, atividade_id=atv1.id),
        Nota(valor=9.8, aluno_id=3, atividade_id=atv2.id),
    ]
    db.session.add_all(notas)
    db.session.commit()

    return jsonify({
        "message": "Banco de atividades e notas populado!",
        "atividades": [a.to_dict() for a in Atividade.query.all()],
        "notas": [n.to_dict() for n in Nota.query.all()]
    }), 201
