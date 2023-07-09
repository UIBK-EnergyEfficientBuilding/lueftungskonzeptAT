from flask import Blueprint
from flask_restx import Api
from lueftungstool.api.calculate import namespace as calculate_ns

blueprint = Blueprint('api', __name__, url_prefix='/api')

api_extension = Api(
    blueprint,
    title='Lüftungskonzept REST api',
    version='0.1-dev',
    description='Lüftungskonzept REST api',
    doc='/doc'
)

api_extension.add_namespace(calculate_ns)
