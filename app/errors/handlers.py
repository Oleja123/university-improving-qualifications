from flask import current_app, render_template

from app.errors import bp


@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(403)
def forbidden_error(error):
    current_app.logger.info('Я был тут')
    return render_template('errors/403.html'), 403


@bp.app_errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500
