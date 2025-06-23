# FTTB

本项目用于 FTTB IP 管理。

## 功能特性

- 基于 `Flask` 框架开发
- 实现 IP 地址的增删改查（CRUD）管理
- 支持按区域、地址和 IP 进行搜索过滤
- 响应式设计，适配不同设备

## 安装依赖

```bash
uv sync
```

## 运行项目

```bash
uv run main.py
```

## 项目结构

```
fttb/
├── main.py            # 主程序入口
├── pyproject.toml     # 项目配置
├── templates/         # 模板目录
│   └── index.html     # 首页模板
│   └── login.html     # 登录模板
├── instance/          # 数据库目录
│   └── fttb.db        # 数据库文件
└── README.md          # 项目文档
```

## 许可证

MIT License