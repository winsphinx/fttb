import unittest
from typing import cast

from main import DatabaseModel, User, app, db


class TestModels(unittest.TestCase):
    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["TESTING"] = True
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.drop_all()

    def test_user_model(self):
        with app.app_context():
            user = User(username="test", password="password")
            db.session.add(user)
            db.session.commit()

            fetched = cast(User, User.query.first())
            self.assertEqual(fetched.username, "test")
            self.assertGreater(len(fetched.password), 10)  # 改为检查密码哈希长度

    def test_database_model(self):
        with app.app_context():
            entry = DatabaseModel(region="test", address="addr", ip="1.1.1.1")
            db.session.add(entry)
            db.session.commit()

            fetched = cast(DatabaseModel, DatabaseModel.query.first())
            self.assertEqual(fetched.region, "test")
            self.assertEqual(fetched.address, "addr")
            self.assertEqual(fetched.ip, "1.1.1.1")


if __name__ == "__main__":
    unittest.main()
