import flask_praetorian
from sqlalchemy import exc
from flask_restplus import Resource, fields
from service import rp_api
from service.api.extensions import guard, db
from service.api.models import User as UserModel
from service.api.users import user_fields, user_input_fields


ns = rp_api.namespace('auth', path='/auth')

user_login_fields = rp_api.model('UserLogin', {
    'email': fields.String(required=True, description='email'),
    'password': fields.String(required=True, description='password'),
    })

user_register_fields = rp_api.model('UserRegister', {
    'id': fields.Integer(readOnly=True, description='User Id'),
    'username': fields.String(required=True, description='username'),
    'email': fields.String(required=True, description='email'),
    'auth_token': fields.String(description='auth token'),
    'admin': fields.Boolean(description='admin'),
    'is_active': fields.Boolean(description='is_active'),
    })


@ns.route('/register')
class Register(Resource):
    """ Register a new user

    Registration of new users.  User input is validated.  Email and Usernames
    are unique.

    Returns:
    - 201 status code for successful create
    - 400 status code for invalid input
    - 409 status code for existing entities
    """
    # Validate user input fields are sane
    @ns.expect(user_input_fields, validate=True)
    # Populate the swagger document with the fields model and return codes
    @rp_api.doc(
        body=user_fields,
        responses={
            409: 'Entity Already Exists',
            201: 'User Registered',
            400: 'Invalid Input'
            }
        )
    # Return the registration model to the user
    @ns.marshal_with(user_register_fields, code=201)
    def post(self):  # On a Post Request
        try:
            # We need these to return None to ensure entries are unique
            username = UserModel.query.filter_by(
                username=rp_api.payload['username']).first()
            email = UserModel.query.filter_by(
                email=rp_api.payload['email']).first()
            if not (username or email):
                user = UserModel.create(**rp_api.payload)
                # If we want to override the access key or refresh key lifespan
                access_lifespan = rp_api.payload.get('access_lifespan', None)
                refresh_lifespan = rp_api.payload.get('refresh_lifespan', None)
                auth_token = guard.encode_jwt_token(
                    user,
                    override_access_lifespan=access_lifespan,
                    override_refresh_lifespan=refresh_lifespan,
                    email=user.email,
                    username=user.username,
                    )
                user.auth_token = auth_token
                return user, 201
            if email:
                rp_api.abort(
                    409, f"Email already exists: {email.email}"
                    )
            if username:
                rp_api.abort(
                    409, f"Username already exists: {username.username}"
                    )
        except (exc.IntegrityError, ValueError) as e:
            db.session.rollback()
            rp_api.abort(400, e)


@ns.route('/login')
class Login(Resource):
    """ Login a valid user

    Authenticate users with email and password.

    Returns:
    - 200 status code for valid login
    - 400 status code for invalid input
    - 401 status code for invalid login
    """
    # Validate email and password were provided
    @ns.expect(user_login_fields, validate=True)
    @ns.doc(
        body=user_login_fields,
        responses={401: 'Invalid Authentication', 200: 'Successful Login'}
        )
    # Return with the user model
    @ns.marshal_with(user_register_fields, code=200)
    def post(self):  # On a Post Request
        try:
            email = rp_api.payload['email']
            password = rp_api.payload['password']
            access_lifespan = rp_api.payload.get('access_lifespan', None)
            refresh_lifespan = rp_api.payload.get('refresh_lifespan', None)
            # Return User model if valid
            user = guard.authenticate(email, password)
            # If this user is valid, generate a new jwt token.
            if user:
                auth_token = guard.encode_jwt_token(
                    user,
                    override_access_lifespan=access_lifespan,
                    override_refresh_lifespan=refresh_lifespan,
                    email=user.email,
                    username=user.username,
                    )
                user.auth_token = auth_token
                if auth_token:
                    return user, 200
        except (exc.IntegrityError, ValueError) as e:
            rp_api.abort(400, e)


@ns.route('/refresh')
class Refresh(Resource):
    """ Refresh a token

    Refresh a users token's expiry before it expires.

    Returns:
    - 200 status code for successful refresh
    """
    @ns.doc(
        responses={200: 'Successful Refresh'}
        )
    def get(self):  # On a Get Request
        old_token = guard.read_token_from_header()
        new_token = guard.refresh_jwt_token(old_token)
        token = {'auth_token': new_token}
        return token, 200


@ns.route('/logout')
class Logout(Resource):
    """ Log out as the currently authenticated user

    Returns:
    - 200 status code for successful logout
    """
    @flask_praetorian.auth_required
    @ns.doc(
        responses={200: 'Successfully Logged Out'}
        )
    def get(self):  # On a Get Request
        try:
            response_object = {'message': 'Successfully logged out.'}
            return response_object, 200
        except Exception as e:
            rp_api.abort(400, e)


@ns.route('/disable')
class Disable(Resource):
    """ Disable a user

    With elevated priviledges, the user is disabled and restricted from logging
    in.

    Returns:
    - 201 status code for successfully disabled
    - 401 for invalid authentication
    """
    @flask_praetorian.roles_required('admin')
    @flask_praetorian.auth_required
    @ns.doc(
        responses={
            201: 'Successfully Disabled User',
            401: 'Invalid Authentication'
            }
        )
    def patch(self):  # On a Patch Request
        user = UserModel.query.filter_by(
            email=rp_api.payload['email']).one()
        user.update(is_active=False)
        return {f'message': 'disabled user {user.username}'}


@ns.route('/status')
class Status(Resource):
    """ Status of the user

    Get the status of self, the currently authenticated user.  I think this may
    be poorly worded.

    Returns:
    - 200 status code with user model
    """
    @flask_praetorian.auth_required
    @ns.doc(
        responses={200: 'Pong'}
        )
    @ns.marshal_with(user_fields, code=200)
    def get(self):  # On a Get Request
        try:
            user = UserModel.get_by_id(
                record_id=flask_praetorian.current_user().id)
            return user, 200
        except Exception as e:
            rp_api.abort(400, e)
