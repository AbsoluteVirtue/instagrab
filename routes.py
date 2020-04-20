from controllers import home


def setup_routes(app):
    app.router.add_view(r'/', handler=home.Main, name='home')
    app.router.add_view(r'/{name:\S+}', handler=home.Main, name='main')
    app.router.add_view(r'/{id:\S+}', handler=home.SinglePost, name='single')
