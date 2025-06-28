# FTTB

本项目用于 FTTB IP 管理。

## 功能特性

- 基于 `Flask` 框架开发
- 使用 `sqlite` 集成数据库
- 使用 `uvicorn` 运行服务，也可以使用 `Docker` 部署
- 使用 `uv` 管理项目依赖
- 实现 IP 地址的增删改查（CRUD）管理
- 支持按区域、地址和 IP 进行搜索过滤
- 用户认证和管理
- 响应式设计，适配不同设备

## 项目结构

```
fttb/
├── main.py            # 主程序入口
├── pyproject.toml     # 项目配置
├── templates/         # 模板目录
│   ├── index.html     # 主页模板
│   ├── login.html     # 系统登录
│   └── users.html     # 用户管理
├── instance/          # 数据库目录
│   └── fttb.db        # 数据库文件
├── README.md          # 项目文档
├── Dockerfile         # Docker 部署配置
└── uv.lock            # 依赖锁定文件
```

## 运行项目

### Python

```bash
# 安装
pip install uv
uv sync
# 运行
uv run main.py
```

### Docker

```bash
docker run -d -p 5000:5000 -v ./data:/app/instance --name=fttb ghcr.io/winsphinx/fttb:latest
```

## 许可证

MIT License