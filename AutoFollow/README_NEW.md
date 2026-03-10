# AutoFollow2-2 小车项目（增强版 README）

这是一个基于 Python 的智能小车控制项目，使用 UWB 定位与传感器数据，实现自动跟随与运动控制。

---

## 🚗 项目简介

本项目通过串口读取 UWB 定位数据，并结合 PWM 电机与舵机驱动，控制小车进行自动跟随和运动控制。

- **UWB 定位**：通过 `ReadUWB.py` 读取 UWB 数据，算出目标距离与角度。
- **控制算法**：`Analyse.py` / `main.py` 对目标信息进行分析，输出控制指令。
- **电机驱动**：`CarControl.py` / `PCA9685.py` 控制 PWM 电机与舵机输出。
- **线程模型**：使用多线程读取与写入共享列表数据，充分利用 Python 容器的“线程安全”特性（list/dict/tuple）。

---

## 📂 目录说明

- `main.py`：项目主入口。
  - 先通过 `CarControl.setForward()`/`setTurn()` 使电调进入可接收状态。
  - 调用 `ReadUWB.setup()` 和 `ReadUWB.start()` 启动两个串口的 UWB 读取线程。
  - 循环从 `ReadUWB.getData()` 获取一对 UWB 字符串，交给 `Decode.decode()` 做均值过滤与数据提取。
  - 从 `Decode.getData()` 取出距离数据并调用 `Analyse.cal()` 计算姿态、距离、朝向、追踪距离/角度；再用 `CarControl.carMove()` 执行运动控制。

- `ReadUWB.py`：UWB 串口读取模块。
  - 使用 `PortSearch.getPort()` 查找可用串口并以 921600 波特率初始化两个串口（`ser0`/`ser1`）。
  - 通过 `ReadUWB.start()` 创建两个线程分别调用 `ReadUWB.read()`，循环读取 159 字节块并转换为 hex 字符串。
  - 只保留以 `5504` 开头的数据串，并在串口数据对齐不足时做偏移补救，最终将有效串保存到 `effectiveData0/1` 列表。
  - `ReadUWB.getData()` 返回一对同步的字符串（来自两个串口）供上层解码使用。

- `Decode.py`：UWB 数据解析与滤波模块。
  - 负责从长度为 318 的 hex 数据串中提取出需要的节点距离（L02/L12/L03/L13），并对每条边做周期性均值过滤。
  - 维护原始累加区（`L02_Origin/L12_Origin/L03_Origin/L13_Origin`）和有效数据区（`L02/L12/L03/L13`）。
  - `decode()` 根据数据包类型（data_str[11]）分流到不同计算路径，并将平均值放入有效数据区。
  - `getData()` 读取并清空已准备好的平均值列表，返回当前的距离数组。

- `Analyse.py`：几何计算模块（位置/角度/引导方向）。
  - 以前车/后车四个节点的距离为输入（L02、L12、L03、L13），利用余弦定理计算：姿态角（Attitude）、目标距离（Distance）、朝向角（Orientation）、追踪距离（ChasingDis）和追踪角（ChasingAngle）。
  - 关键变量包括：L01/L23/L46（默认 95cm，用于描述车体尺寸与目标关系）。
  - `cal()` 计算并将结果追加到 `Analyse.data`；`getData()` 取出并清空缓存。

- `CarControl.py`：运动控制与 PID 调速模块。
  - 通过 `PCA9685.PWM` 驱动板控制前进（`setForward()`）和转向（`setTurn()`）的 PWM 输出。
  - `AdaptiveShift()` 基于追踪距离（ChasingDis）进行 PID 风格速度调节；`AdaptiveTurn()` 根据姿态/偏航角计算舵机转向值。
  - `carMove()` 由 `main.py` 调用：当距离小于最小安全距离时停车，否则更新历史数据并调用转向/油门子模块。

- `PCA9685.py`：PCA9685 PWM 驱动封装。
  - 提供对 I2C 设备的初始化与 `setDuty()` 控制函数，用于生成对应 PWM 占空比信号。

- `PortSearch.py`：串口搜索工具。
  - 扫描系统可用串口并返回可用于连接 UWB 模块的端口列表。

---

## ✅ 快速开始

> 请确认硬件已连接：UWB 模块、PCA9685 驱动板、电机、舵机等，并且串口已正确配置。

1. 确认项目目录中有 Python 环境 (建议 3.8+)。
2. 安装依赖（如果有第三方依赖，可自行补充）：

```bash
pip install pyserial
```

3. 运行主程序：

```bash
python main.py
```

---

## 🧠 线程安全说明

项目中部分数据由多个线程共享并更新，例如：

- `ReadUWB.py` 读取的数据写入共享列表
- 其它线程读取该列表用于计算与控制

本项目依赖 Python 内置容器（`list`/`dict`/`tuple`）的“线程安全性”，因此 **不使用显式锁机制**（如 `threading.Lock`）。这降低了锁竞争成本，但请注意并发场景下的读写顺序可能会出现短暂不一致（这是 Python 线程模型的正常表现）。

---

## 🔧 参数配置

- `MinDistance`：默认 95cm（参见旧版 `ReadMe.md` 中的说明）。
- 串口波特率与端口：请在 `ReadUWB.py` 或 `PortSearch.py` 中调整为你的硬件环境。

---

## 📝 常见问题

- **无法读取串口**：请确认串口已正确连接，且其他程序未占用。
- **控制指令无效**：检查 PCA9685 供电与 PWM 输出信号是否正常。

---

## 📌 版权与许可

本项目为个人/教育用途，未附带特定许可。如需用于商业项目，请遵循原作者授权。

---

如需进一步帮助，请查看源码里各模块的注释或联系项目维护者。
