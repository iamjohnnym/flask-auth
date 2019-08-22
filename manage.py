import sys
import unittest

import operator
import coverage
from flask.cli import FlaskGroup

from service import create_app, db
from service.api.models import User


COV = coverage.coverage(
    branch=True,
    include='service/*',
    omit=[
        'service/tests/*',
        'service/config.py',
    ]
)
COV.start()

app = create_app()
cli = FlaskGroup(create_app=create_app)


@cli.command()
def routes():
    'Display registered routes'
    rules = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods))
        rules.append((rule.endpoint, methods, str(rule)))

    sort_by_rule = operator.itemgetter(2)
    for endpoint, methods, rule in sorted(rules, key=sort_by_rule):
        route = '{:50s} {:25s} {}'.format(endpoint, methods, rule)
        print(route)

@cli.command('recreate_db')
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command('seed_db')
def seed_db():
    """Seeds the database."""
    # Marked as nosec but should maybe be reviewed in the future
    db.session.add(User( # nosec
        username='admin',
        email='admin@example.com',
        password='BighandsLittl3feet#'
    ))
    db.session.commit()


@cli.command()
def test():
    """Runs the tests without code coverage"""
    tests = unittest.TestLoader().discover('service/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    sys.exit(result)

# wip
@cli.command('sentry_pr_release')
def sentry_pr_release():
    """Create a release for sentry.io"""
    import sentry_sdk
    print(sentry_sdk.init(
        dsn=f"{app.config['SENTRY_URL']}",
        release="flask-auth@0.1.0-alpha0"))


@cli.command()
def cov():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover('service/tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        COV.html_report()
        COV.xml_report()
        COV.erase()
        return 0
    sys.exit(result)


if __name__ == '__main__':
    cli()
