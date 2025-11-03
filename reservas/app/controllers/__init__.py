def register_controllers(app):
    from .reserva_controller import reserva_bp
    from .seed_controller import seed_bp

    app.register_blueprint(reserva_bp, url_prefix="/api/reservas")
    app.register_blueprint(seed_bp, url_prefix="/api")