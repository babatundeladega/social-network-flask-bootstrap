from app import create_app, db


application = create_app()

with application.app_context():
    db.init_app(application)
    db.Model.metadata.reflect(db.engine)  # load existing DB schema
    db.create_all()


if __name__ == '__main__':
    application.run()
