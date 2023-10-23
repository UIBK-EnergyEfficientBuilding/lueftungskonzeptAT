from lueftungstool.api import blueprint as api

from flask_openapi3 import OpenAPI, Info

def create_app():
    info = Info(
        title='Lüftungskonzept REST api',
        version='0.1-dev',
        description='Lüftungskonzept REST api',
    )
    app = OpenAPI(__name__, info=info)
    app.register_api(api)
    print(app.url_map)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run()
