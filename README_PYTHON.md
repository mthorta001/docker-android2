# Docker Android Builder (Python Version)

这是 `app.sh` 的 Python 重写版本，提供更好的可读性和可维护性。

## 功能特性

- ✅ **更好的可读性**: 使用 Python 类和方法组织代码
- ✅ **类型提示**: 完整的类型注解，提高代码质量
- ✅ **错误处理**: 更好的异常处理和错误信息
- ✅ **交互式界面**: 友好的用户交互体验
- ✅ **命令行参数**: 支持完整的命令行参数
- ✅ **进度显示**: 清晰的执行进度和状态显示

## 使用方法

### 1. 命令行方式 (推荐)

```bash
# 构建基础镜像
./app.py build base v2.0-p6

# 构建模拟器镜像
./app.py build emulator v2.0-p6 11.0

# 运行测试
./app.py test emulator v2.0-p6 11.0

# 推送到 Docker Hub
./app.py push emulator v2.0-p6 11.0
```

### 2. 交互式方式

```bash
./app.py
# 脚本会提示你选择：
# Task (test|build|push): build
# Project (base|emulator|genymotion|pro-emulator|pro-emulator_headless): emulator
# Release Version (v2.0.0-p0|v2.0.0-p1|etc): v2.0-p6
# Android Version (9.0|10.0|11.0|12.0|13.0|14.0|15.0|16.0): 11.0
```

### 3. 帮助信息

```bash
./app.py --help
```

## 支持的参数

- **任务类型**: `test`, `build`, `push`
- **项目类型**: `base`, `emulator`, `genymotion`, `pro-emulator`, `pro-emulator_headless`
- **Android 版本**: `9.0`, `10.0`, `11.0`, `12.0`, `13.0`, `14.0`, `15.0`, `16.0`
- **发布版本**: 任意字符串，建议使用 `v2.0-p6` 格式

## 与原版 app.sh 的对比

| 特性 | app.sh | app.py |
|------|--------|--------|
| 可读性 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 错误处理 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 类型安全 | ❌ | ✅ |
| 代码组织 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 测试友好 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 文档 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 维护性 | ⭐⭐ | ⭐⭐⭐⭐⭐ |

## 代码结构

```python
DockerAndroidBuilder
├── 配置常量 (TASKS, PROJECTS, API_LEVELS, etc.)
├── 参数解析 (parse_arguments)
├── 构建配置 (setup_build_configuration)
├── 核心功能
│   ├── build_image()    # 构建镜像
│   ├── run_tests()      # 运行测试
│   └── push_images()    # 推送镜像
└── 工具方法
    ├── validate_choice()  # 参数验证
    ├── get_user_input()   # 用户输入
    └── run_command()      # 命令执行
```

## 示例输出

```
Docker Android Builder
==================================================
Building: rcswain/docker-android:emulator_11.0_v2.0-p6 or rcswain/docker-android:emulator_11.0

==================================================
Building Docker Image
==================================================
Running: Building Docker image
Command: docker build -t rcswain/docker-android:emulator_11.0_v2.0-p6 --build-arg DOCKER_ANDROID_VERSION=v2.0-p6 --build-arg EMULATOR_ANDROID_VERSION=11.0 --build-arg EMULATOR_API_LEVEL=30 -f docker/emulator .

==================================================
✅ Task completed successfully!
```

## 依赖要求

- Python 3.6+
- Docker
- 系统支持的 subprocess 模块

## 迁移指南

如果你想从 `app.sh` 迁移到 `app.py`：

1. **保持相同的命令行参数顺序**
2. **所有功能完全兼容**
3. **可以逐步替换 CI/CD 脚本中的调用**

```bash
# 原来的调用
./app.sh build emulator v2.0-p6 11.0

# 新的调用 (完全相同)
./app.py build emulator v2.0-p6 11.0
``` 