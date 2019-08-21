import flask_praetorian
from sqlalchemy import exc
from flask_restplus import Resource, fields
from service import db, rp_api
from service.api.models import User as UserModel

ns = rp_api.namespace('users', path='/users')

user_input_fields = rp_api.model('UserInput', {
    'username': fields.String(required=True, description='username'),
    'password': fields.String(required=True, description='password'),
    'email': fields.String(required=True, description='email'),
    })

user_fields = rp_api.model('User', {
    'id': fields.Integer(readOnly=True, description='User Id'),
    'username': fields.String(required=True, description='username'),
    'email': fields.String(required=True, description='email'),
    'admin': fields.Boolean(description='admin'),
    'is_active': fields.Boolean(description='is_active'),
    })


@ns.route('/ping')
class Ping(Resource):
    """Return a Pong"""
    def get(self):
        return {
            'status': 'success',
            'message': 'pong!'
            }


@ns.route('/<string:user_id>')
@ns.doc(responses={404: 'User not found'}, params={'user_id': 'The User ID'})
class User(Resource):
    """Return a single user by User id

    Params:
      user_id :: User.id of a user to look up
    Returns:
    - 200 success
    - 404 not found
    """
    @ns.doc(body=user_fields)
    @ns.marshal_with(user_fields)
    @flask_praetorian.auth_required
    def get(self, user_id):
        """Get single user details"""
        try:
            user = UserModel.get_by_id(record_id=user_id)
            if not user:
                rp_api.abort(404, f"User Not Found by Id {user_id}")
            return user, 200
        except (exc.IntegrityError, ValueError):
            rp_api.abort(400)


@ns.route('/')
class List(Resource):
    """List's all Users"""
    @ns.doc(body=user_fields)
    @ns.marshal_list_with(user_fields)
    @flask_praetorian.auth_required
    def get(self):
        """Get all users"""
        return UserModel.query.all()

    @ns.expect(user_input_fields, validate=True)
    @rp_api.doc(body=user_fields, responses={409: 'Email address in use'})
    @ns.marshal_with(user_fields, code=201)
    @flask_praetorian.auth_required
    def post(self):
        try:
            username = UserModel.query.filter_by(
                username=rp_api.payload['username']).first()
            email = UserModel.query.filter_by(
                email=rp_api.payload['email']).first()
            if not (username or email):
                user = UserModel.create(**rp_api.payload)
                return user, 201
            if email:
                rp_api.abort(
                    409, f"Email already in use: {rp_api.payload['email']}")
            if username:
                rp_api.abort(
                    409,
                    f"Username already in use: {rp_api.payload['username']}"
                    )
            rp_api.abort(409, "Invalid fields")
        except (exc.IntegrityError, ValueError) as e:
            db.session.rollback()
            rp_api.abort(400, e)
