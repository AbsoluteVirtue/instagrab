from controllers import home


def setup_routes(app):
    app.router.add_view(r'/', handler=home.Input, name='home')
    app.router.add_view(r'/{id:\S+}', handler=home.Single, name='single')
