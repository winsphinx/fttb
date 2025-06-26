import unittest

from main import User, app, db


class TestRoutes(unittest.TestCase):
    def setUp(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            # 添加测试用户
            test_user = User(username="test", password="password")
            db.session.add(test_user)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.drop_all()

    def test_login(self):
        # 测试成功登录
        response = self.app.post(
            "/login",
            data={"username": "test", "password": "password"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)

        # 测试错误密码
        response = self.app.post(
            "/login", data={"username": "test", "password": "wrong"}
        )
        self.assertEqual(response.status_code, 200)

    def test_user_management(self):
        # 先登录
        self.app.post("/login", data={"username": "test", "password": "password"})

        # 测试用户列表
        response = self.app.get("/users")
        self.assertEqual(response.status_code, 200)

    def test_add_user(self):
        # 先登录
        self.app.post("/login", data={"username": "test", "password": "password"})

        # 测试添加用户
        response = self.app.post(
            "/add_user",
            data={"username": "newuser", "password": "newpass"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)

    def test_database_crud(self):
        # 先登录
        self.app.post("/login", data={"username": "test", "password": "password"})

        # 测试添加数据
        response = self.app.post(
            "/",
            data={
                "form_action": "add",
                "region": "test",
                "address": "addr",
                "ip": "1.1.1.1",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)

        # 测试查询数据
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
