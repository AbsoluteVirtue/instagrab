from controllers import home


def setup_routes(app):
    app.router.add_view(r'/', handler=home.Main, name='home')
    app.router.add_view(r'/{name:^[A-Za-z0-9-_]+$}', handler=home.Main, name='main')
    app.router.add_view(r'/p/{id:\S+}', handler=home.SinglePost, name='single')
