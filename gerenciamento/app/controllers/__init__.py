def register_controllers(app):
    from .professor_controller import professor_bp
    from .turma_controller import turma_bp
    from .aluno_controller import aluno_bp
    from .seed_controller import seed_bp

    # registra cada módulo com seu prefixo de URL
    app.register_blueprint(professor_bp, url_prefix="/api/professores")
    app.register_blueprint(turma_bp, url_prefix="/api/turmas")
    app.register_blueprint(aluno_bp, url_prefix="/api/alunos")
    app.register_blueprint(seed_bp, url_prefix="/api")
