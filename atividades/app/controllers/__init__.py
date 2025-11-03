def register_controllers(app):
    from .atividade_controller import atividade_bp
    from .nota_controller import nota_bp
    from .seed_controller import seed_bp

    app.register_blueprint(atividade_bp, url_prefix="/api/atividades")
    app.register_blueprint(nota_bp, url_prefix="/api/notas")
    app.register_blueprint(seed_bp, url_prefix="/api")
