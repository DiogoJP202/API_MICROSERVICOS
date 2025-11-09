from flask import Blueprint, jsonify
from app.extensions import db
from app.models.professor import Professor
from app.models.turma import Turma
from app.models.aluno import Aluno

seed_bp = Blueprint("seed", __name__)

@seed_bp.route("/seed", methods=["POST"])
def seed_data():
    """
    Popular banco com dados de exemplo
    ---
    tags:
      - Seed
    summary: Reinicia o banco e insere dados iniciais
    description: |
      DERRUBA e recria todas as tabelas e, em seguida,
      insere dados de exemplo para Professores, Turmas e Alunos.
      Útil para desenvolvimento.
    responses:
      201:
        description: Banco populado com sucesso
        schema:
          type: object
          properties:
            message:
              type: string
              example: Banco populado com sucesso!
            professores:
              type: array
              items:
                $ref: '#/definitions/Professor'
            turmas:
              type: array
              items:
                $ref: '#/definitions/Turma'
            alunos:
              type: array
              items:
                $ref: '#/definitions/Aluno'
    definitions:
      Professor:
        type: object
        properties:
          id:
            type: integer
            example: 1
          nome:
            type: string
            example: Marcos Paulo
          materia:
            type: string
            example: Matemática
      Turma:
        type: object
        properties:
          id:
            type: integer
            example: 1
          nome:
            type: string
            example: 1A
          professor_id:
            type: integer
            example: 1
      Aluno:
        type: object
        properties:
          id:
            type: integer
            example: 1
          nome:
            type: string
            example: Carlos
          turma_id:
            type: integer
            example: 1
    """
    db.drop_all()
    db.create_all()

    prof1 = Professor(nome="Marcos Paulo", materia="Matemática")
    prof2 = Professor(nome="Ana Beatriz", materia="Português")

    db.session.add_all([prof1, prof2])
    db.session.commit()

    turma1 = Turma(nome="1A", professor_id=prof1.id)
    turma2 = Turma(nome="2B", professor_id=prof2.id)
    db.session.add_all([turma1, turma2])
    db.session.commit()

    alunos = [
        Aluno(nome="Carlos", turma_id=turma1.id),
        Aluno(nome="Fernanda", turma_id=turma1.id),
        Aluno(nome="Rafaela", turma_id=turma2.id),
    ]
    db.session.add_all(alunos)
    db.session.commit()

    return jsonify({
        "message": "Banco populado com sucesso!",
        "professores": [p.to_dict() for p in Professor.query.all()],
        "turmas": [t.to_dict() for t in Turma.query.all()],
        "alunos": [a.to_dict() for a in Aluno.query.all()]
    }), 201
