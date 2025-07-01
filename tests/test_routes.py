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

    def test_import_data(self):
        # 先登录
        self.app.post("/login", data={"username": "test", "password": "password"})

        # 创建临时文件并写入测试数据
        import os
        import tempfile

        tmp = None
        try:
            tmp = tempfile.NamedTemporaryFile(mode="w+", suffix=".csv", delete=False)
            tmp.write(
                "id,region,address,ip\n1,区域1,地址1,1.1.1.1\n2,区域2,地址2,2.2.2.2\n3,区域3,地点3,3.3.3.3"
            )
            tmp.close()  # 显式关闭文件以确保可以重新打开

            # 测试导入数据
            with open(tmp.name, "rb") as f:
                response = self.app.post(
                    "/import",
                    data={"file": (f, "test_data.csv")},
                    content_type="multipart/form-data",
                    follow_redirects=True,
                )
            self.assertEqual(response.status_code, 200)
        finally:
            if tmp and os.path.exists(tmp.name):
                try:
                    os.unlink(tmp.name)
                except PermissionError:
                    pass  # 如果文件权限问题，忽略错误

    def test_export_data(self):
        # 先登录
        self.app.post("/login", data={"username": "test", "password": "password"})

        # 测试导出数据
        response = self.app.get("/export")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response.content_type)


if __name__ == "__main__":
    unittest.main()
