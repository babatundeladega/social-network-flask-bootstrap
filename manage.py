#! /usr/bin/env python
import os

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app import db
from app.models import (
    App,
    AppCategory,
    Currency,
    MemberCategory,
    Pricing,
    ProductCategory,
    Skill,
    Status,
    StoreCategory)
from modules.apps import AppsRoute
from wsgi import application


manager = Manager(application)


if os.environ['RUNNING_MODE'] == 'development':
    migrate = Migrate(application, db, directory='local_migrations')

else:
    migrate = Migrate(application, db, directory='remote_migrations')


manager.add_command('db', MigrateCommand)


@manager.command
def pump_app_categories_table():
    print('app categories')

    app_categories = ['Admin', 'App', 'Bot', 'Website', 'USSD']

    for category in app_categories:
        try:
            AppCategory(name=category).save()
        except:
            pass


@manager.command
def pump_currencies_table():
    print('currencies')

    currencies = [
        ('Nigerian Naira',          'NGN',      '0.0028'),
        ('United States Dollar',    'USD',      '1'),
        ('Pound Sterling',          'GBP',      '1.30'),
        ('South African Rand',      'ZAR',      '0.07')
    ]

    for name, short_code, usd_equivalent in currencies:
        if Currency.get_active(name=name):
            continue

        Currency(
            name=name,
            short_code=short_code,
            usd_equivalent=usd_equivalent).save()

    return


@manager.command
def pump_member_categories_table():
    print('member categories')

    member_categories = ['Artisan', 'Merchant']

    for category in member_categories:
        try:
            MemberCategory(name=category).save()
        except:
            pass


@manager.command
def pump_skills_table():
    print('skills')

    skills = [
        'Plumber', 'Carpenter', 'Mechanic', 'Interior Decorator', 'Caterer']

    for skill in skills:
        try:
            Skill(name=skill).save()
        except:
            pass


@manager.command
def pump_statuses_table():
    print('statuses')

    status_modes_and_ids = {
        'Active': 1,
        'Pending': 2,
        'Disabled': 3,
        'Paid': 8,
        'Failed': 4,
        'Blocked': 13,
        'Fulfilled': 20,
        'Shipped': 25,
        'Delivered': 30,
        'Deleted': 99
    }

    for status, id_ in status_modes_and_ids.items():
        if Status.get_active(name=status) is not None:
            continue

        status = Status(name=status)
        status.save()

        try:
            status.update(id=id_)
        except:
            pass


@manager.command
def pump_store_categories_table():
    print('store categories')

    store_categories = ['Pharmacy', 'Restaurant', 'Boutique']

    for category in store_categories:
        try:
            StoreCategory(name=category).save()
        except:
            pass


@manager.command
def pump_apps_table():
    print('apps')

    apps = [
        ('ORDERING SRVC ADMIN',          1)
    ]

    for app, category_id in apps:
        try:
            app = App(name=app, app_category_id=category_id)
            AppsRoute.after_app_creation(app)
        except:
            pass


@manager.command
def pump_product_categories_table():
    print('product categories')

    categories = []

    for category in categories:
        try:
            ProductCategory(name=category).save()
        except:
            pass


@manager.command
def pump_pricings_table():
    print('pricing table')

    all_pricings = [
        {
            'name': 'Basic',
            'token_equivalent': '180',
            'request_cost': '1',
            'sms_cost': '2.3',
            'email_cost': '0.045',
            'buy_in': '1'
        },
        {
            'name': 'Advanced',
            'token_equivalent': '240',
            'request_cost': '1',
            'sms_cost': '2',
            'email_cost': '0.02',
            'buy_in': '48000'
        },
        {
            'name': 'Deluxe',
            'token_equivalent': '300',
            'request_cost': '.75',
            'sms_cost': '1.8',
            'email_cost': '0.01',
            'buy_in': '120000'
        }
    ]

    for pricing in all_pricings:
        Pricing(**pricing).save()


@manager.command
def run_all_commands():
    pump_statuses_table()
    pump_app_categories_table()
    pump_currencies_table()
    pump_member_categories_table()
    pump_skills_table()
    pump_store_categories_table()
    pump_product_categories_table()


if __name__ == "__main__":
    manager.run()
