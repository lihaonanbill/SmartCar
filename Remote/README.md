# RemoteCar (WAN) 项目说明

本项目用于通过公网远程控制树莓派小车，整体为三端通信架构：

- `steering_wheel_client.py`：PC 客户端，读取方向盘/手柄输入并发送控制数据
- `server.py`：中继服务器，转发客户端与树莓派之间的 TCP 消息
- `steering_wheel_rasp.py`：树莓派端，接收控制数据并通过 PCA9685 驱动舵机/电机

## 1. 项目结构

```text
.
├── server.py                   # 公网中继服务端（双线程转发）
├── steering_wheel_client.py    # 方向盘/手柄客户端
├── steering_wheel_rasp.py      # 树莓派控制端
├── clientdemo.py               # 简化客户端通信测试
├── raspdemo.py                 # 简化树莓派通信测试
└── operation introduction.md   # 原始操作说明
```

## 2. 通信流程

1. 客户端连接中继服务器 `IP:7000`
2. 树莓派连接同一中继服务器 `IP:7000`
3. `server.py` 接收两个连接后开始双向转发
4. 客户端发送的方向轴数据被树莓派解析并映射为 PWM 占空比
5. 客户端退出时发送断开信号，树莓派将舵机/电机回到初始值

## 3. 环境依赖

### 客户端（Windows/Linux 均可）

- Python 3.7+
- `pygame`

安装示例：

```bash
pip install pygame
```

### 树莓派端

- Python 3.7+
- `smbus` / `smbus2`（按系统版本选择）
- PCA9685 驱动模块（代码中通过 `from PCA9685 import PWM` 导入）
- I2C 已启用，硬件连接正确

## 4. 运行前配置

请先统一修改三个脚本中的服务器 IP 地址为你自己的公网服务器地址：

- `server.py` 中 `server.bind(("172.26.33.67", 7000))`
- `steering_wheel_client.py` 中 `IP = '120.25.163.59'`
- `steering_wheel_rasp.py` 中 `IP = '120.25.163.59'`

建议统一为同一个可访问地址，并确保云服务器安全组/防火墙已放行 `7000/TCP`。

## 5. 启动步骤

严格按顺序启动：

1. 启动中继服务器

```bash
python server.py
```

2. 启动客户端（连接方向盘/手柄）

```bash
python steering_wheel_client.py
```

3. 启动树莓派端

```bash
python steering_wheel_rasp.py
```

## 6. 退出与安全

- 在客户端输入 `e` 可触发退出流程
- 树莓派端收到退出信号后会执行：
  - 舵机回中（`Gear.setTurn(7.5)`）
  - 电机回初始占空比（`Gear.setForwad(8)`）

## 7. 调参说明

核心映射位于 `steering_wheel_rasp.py`：

- 舵机转向：`7.5 + 2.4 * axis0`
- 电机前进：`8 - 2 * axis1`
- 电机后退：`8 - 1.5 * axis1`

请根据你的电调/电机/舵机实际情况调整占空比范围，首次调试建议抬起驱动轮并限制油门幅度。

## 8. 常见问题

- 连接不上服务器
  - 检查三端 IP 是否一致
  - 检查 `7000` 端口是否开放
  - 检查服务器是否先启动
- 客户端报手柄错误
  - 确认系统已识别到 `Joystick(0)`
  - `pygame` 版本与系统驱动兼容
- 树莓派端找不到 `PCA9685`
  - 将对应驱动文件放到同目录，或正确安装到 Python 环境

## 9. Demo 脚本用途

- `clientdemo.py` 与 `raspdemo.py` 用于只验证“链路是否畅通”，不包含小车控制逻辑。

