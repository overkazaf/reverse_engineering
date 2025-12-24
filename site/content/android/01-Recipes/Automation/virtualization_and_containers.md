---
title: "工程化：虚拟化与容器技术"
weight: 10
---

# 工程化：虚拟化与容器技术

> **前置知识**
>
> 本配方涉及以下核心技术，建议先阅读相关章节：
>
> - **[ADB 速查手册](../../02-Tools/Cheatsheets/adb_cheatsheet.md)** - 模拟器设备管理基础
> - **[Docker 部署](./docker_deployment.md)** - Docker 基础概念
> - **Linux 基础** - 理解进程隔离与资源限制

移动端虚拟化技术是在服务器端模拟出成百上千个 Android 设备环境的能力，它是所有大规模自动化测试、数据采集和安全分析任务的基石。这项技术的核心在于平衡性能、隔离性和真实性。

---

## 1. 技术架构总览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           云手机/自动化平台                               │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  任务调度器  │  │  设备管理器  │  │  脚本引擎   │  │  数据存储   │    │
│  │  (Celery)   │  │  (自研)     │  │  (Appium)  │  │  (MongoDB) │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│         │                │                │                │           │
│         └────────────────┴────────────────┴────────────────┘           │
│                                   │                                     │
├───────────────────────────────────┼─────────────────────────────────────┤
│                           容器编排层 (Kubernetes / Docker Swarm)         │
├───────────────────────────────────┼─────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    Android 虚拟化层                               │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐│  │
│  │  │Redroid-1│  │Redroid-2│  │Redroid-3│  │   ...   │  │Redroid-N││  │
│  │  │ :5555   │  │ :5556   │  │ :5557   │  │         │  │ :555N   ││  │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘│  │
│  └──────────────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────────┤
│                           宿主机 (Linux + Docker + GPU)                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Android 模拟器方案详解

### 2.1 方案对比矩阵

| 方案 | 类型 | 性能 | 隔离性 | 扩展性 | 成本 | 适用场景 |
|-----|-----|-----|-------|-------|-----|---------|
| **Android SDK Emulator** | 全系统模拟 (QEMU) | ★★☆ | ★★★★★ | ★★☆ | 免费 | 开发调试、小规模测试 |
| **Redroid** | Docker 容器 | ★★★★ | ★★★★ | ★★★★★ | 免费 | 大规模云手机、CI/CD |
| **Waydroid** | LXC 容器 | ★★★★★ | ★★★ | ★★★ | 免费 | 本地开发、单机测试 |
| **Genymotion Cloud** | 商业 PaaS | ★★★★ | ★★★★★ | ★★★★★ | 付费 | 企业级、合规要求高 |
| **AWS Device Farm** | 真机云服务 | ★★★★★ | ★★★★★ | ★★★★ | 按需付费 | 真机兼容性测试 |

### 2.2 Android SDK Emulator

官方模拟器，功能最完整，适合开发调试。

#### 安装与配置

```bash
# 安装 Android SDK 命令行工具
wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
unzip commandlinetools-linux-*.zip -d android-sdk
export ANDROID_HOME=$PWD/android-sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin

# 安装系统镜像和平台工具
sdkmanager "platform-tools" "emulator"
sdkmanager "system-images;android-33;google_apis;x86_64"

# 创建 AVD (Android Virtual Device)
avdmanager create avd -n test_device -k "system-images;android-33;google_apis;x86_64" \
    --device "pixel_4" \
    -c 2048M  # 2GB SD卡
```

#### 启动参数优化

```bash
# 无头模式启动 (服务器环境)
emulator -avd test_device \
    -no-window \
    -no-audio \
    -no-boot-anim \
    -gpu swiftshader_indirect \
    -memory 4096 \
    -cores 4 \
    -partition-size 8192 \
    -writable-system \
    -port 5554

# 常用参数说明
# -no-window        无界面模式
# -no-audio         禁用音频
# -no-boot-anim     跳过开机动画
# -gpu              GPU 渲染模式 (host/swiftshader_indirect/off)
# -memory           内存大小 (MB)
# -cores            CPU 核心数
# -writable-system  允许修改 /system 分区
```

#### 批量管理脚本

```bash
#!/bin/bash
# start_emulators.sh - 批量启动模拟器

NUM_EMULATORS=${1:-5}
BASE_PORT=5554

for i in $(seq 1 $NUM_EMULATORS); do
    PORT=$((BASE_PORT + (i-1) * 2))
    AVD_NAME="device_$i"

    echo "Starting $AVD_NAME on port $PORT..."

    emulator -avd $AVD_NAME \
        -no-window \
        -no-audio \
        -port $PORT \
        -read-only &

    sleep 5
done

# 等待所有设备启动完成
echo "Waiting for devices to boot..."
for i in $(seq 1 $NUM_EMULATORS); do
    PORT=$((BASE_PORT + (i-1) * 2))
    adb -s emulator-$PORT wait-for-device
    adb -s emulator-$PORT shell 'while [[ -z $(getprop sys.boot_completed) ]]; do sleep 1; done'
    echo "Device emulator-$PORT is ready"
done

echo "All $NUM_EMULATORS emulators are running"
```

### 2.3 Redroid (Remote Android)

Redroid 是基于 Docker 的 Android 容器化方案，性能优秀，适合大规模部署。

#### 系统要求

```bash
# 检查内核模块
lsmod | grep -E "binder|ashmem"

# 如果没有，需要加载或安装
# Ubuntu 20.04+
sudo apt install linux-modules-extra-$(uname -r)
sudo modprobe binder_linux devices="binder,hwbinder,vndbinder"
sudo modprobe ashmem_linux

# 持久化加载
echo "binder_linux" | sudo tee /etc/modules-load.d/binder.conf
echo "ashmem_linux" | sudo tee /etc/modules-load.d/ashmem.conf
echo "options binder_linux devices=binder,hwbinder,vndbinder" | sudo tee /etc/modprobe.d/binder.conf
```

#### Docker 部署

```bash
# 单实例启动
docker run -d --name redroid \
    --privileged \
    --memory 4g \
    --cpus 4 \
    -v ~/redroid-data:/data \
    -p 5555:5555 \
    redroid/redroid:12.0.0-latest \
    androidboot.redroid_width=1080 \
    androidboot.redroid_height=1920 \
    androidboot.redroid_dpi=440 \
    androidboot.redroid_fps=60

# 连接设备
adb connect localhost:5555
adb devices
```

#### docker-compose 多实例部署

```yaml
# docker-compose.yml
version: "3.8"

x-redroid-common: &redroid-common
  image: redroid/redroid:12.0.0-latest
  privileged: true
  mem_limit: 4g
  cpus: 2
  command:
    - androidboot.redroid_width=1080
    - androidboot.redroid_height=1920
    - androidboot.redroid_dpi=440
    - androidboot.redroid_fps=30
    - androidboot.redroid_gpu_mode=guest

services:
  # Android 实例
  redroid-1:
    <<: *redroid-common
    container_name: redroid-1
    ports:
      - "5555:5555"
    volumes:
      - ./data/device-1:/data

  redroid-2:
    <<: *redroid-common
    container_name: redroid-2
    ports:
      - "5556:5555"
    volumes:
      - ./data/device-2:/data

  redroid-3:
    <<: *redroid-common
    container_name: redroid-3
    ports:
      - "5557:5555"
    volumes:
      - ./data/device-3:/data

  # 支撑服务
  redis:
    image: redis:7-alpine
    container_name: redis
    ports:
      - "6379:6379"
    volumes:
      - ./data/redis:/data

  mitmproxy:
    image: mitmproxy/mitmproxy:latest
    container_name: mitmproxy
    ports:
      - "8080:8080"
      - "8081:8081"
    command: mitmweb --web-host 0.0.0.0
    volumes:
      - ./data/mitmproxy:/home/mitmproxy/.mitmproxy

  mongodb:
    image: mongo:6
    container_name: mongodb
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password
    volumes:
      - ./data/mongodb:/data/db

networks:
  default:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16
```

#### 启动与管理

```bash
# 启动所有服务
docker-compose up -d

# 批量连接设备
for port in 5555 5556 5557; do
    adb connect localhost:$port
done

# 查看设备状态
adb devices

# 批量安装 APK
APK_PATH="./target.apk"
for device in $(adb devices | grep -v "List" | awk '{print $1}'); do
    echo "Installing on $device..."
    adb -s $device install -r $APK_PATH &
done
wait

# 停止所有服务
docker-compose down
```

### 2.4 Waydroid

Waydroid 基于 LXC 容器，性能接近原生，适合本地开发。

```bash
# Ubuntu 安装
sudo apt install curl ca-certificates -y
curl https://repo.waydro.id | sudo bash
sudo apt install waydroid -y

# 初始化 (选择 GAPPS 版本包含 Google 服务)
sudo waydroid init -s GAPPS

# 启动 Waydroid 容器
sudo systemctl start waydroid-container

# 启动 Waydroid 会话 (需要图形界面)
waydroid session start

# 安装应用
waydroid app install ./app.apk

# ADB 连接
adb connect 192.168.240.112:5555
```

---

## 3. 容器化工程实践

### 3.1 自动化测试环境容器

```dockerfile
# Dockerfile.automation
FROM python:3.11-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    android-tools-adb \
    android-tools-fastboot \
    openjdk-17-jdk-headless \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# 安装 Node.js (Appium 依赖)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# 安装 Appium
RUN npm install -g appium@2.0.0 \
    && appium driver install uiautomator2

# 安装 Python 依赖
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制测试脚本
COPY scripts/ ./scripts/
COPY configs/ ./configs/

# 启动入口
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
```

**requirements.txt**:

```text
frida-tools==12.3.0
objection==1.11.0
Appium-Python-Client==3.0.0
uiautomator2==3.0.0
adbutils==2.0.0
pymongo==4.6.0
redis==5.0.0
celery==5.3.0
requests==2.31.0
```

**entrypoint.sh**:

```bash
#!/bin/bash
set -e

# 启动 ADB 服务
adb start-server

# 等待设备连接
echo "Waiting for devices..."
DEVICES=${ANDROID_DEVICES:-"localhost:5555"}
for device in ${DEVICES//,/ }; do
    echo "Connecting to $device..."
    adb connect $device
    adb -s $device wait-for-device
done

# 启动 Appium 服务 (后台)
if [ "$START_APPIUM" = "true" ]; then
    appium --address 0.0.0.0 --port 4723 &
    sleep 5
fi

# 执行传入的命令
exec "$@"
```

### 3.2 完整的 CI/CD 集成

```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - deploy

variables:
  DOCKER_HOST: tcp://docker:2375
  ANDROID_DEVICES: "redroid-1:5555,redroid-2:5555,redroid-3:5555"

# 构建测试镜像
build-test-image:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  script:
    - docker build -t automation:$CI_COMMIT_SHA -f Dockerfile.automation .
    - docker push $CI_REGISTRY_IMAGE/automation:$CI_COMMIT_SHA

# 运行自动化测试
run-android-tests:
  stage: test
  image: docker:24
  services:
    - docker:24-dind
    - name: redroid/redroid:12.0.0-latest
      alias: redroid-1
      command: ["androidboot.redroid_width=1080", "androidboot.redroid_height=1920"]
    - name: redroid/redroid:12.0.0-latest
      alias: redroid-2
      command: ["androidboot.redroid_width=1080", "androidboot.redroid_height=1920"]
  script:
    - docker run --rm
        -e ANDROID_DEVICES=$ANDROID_DEVICES
        -e START_APPIUM=true
        -v $PWD/reports:/app/reports
        $CI_REGISTRY_IMAGE/automation:$CI_COMMIT_SHA
        pytest scripts/tests/ --junitxml=/app/reports/results.xml
  artifacts:
    reports:
      junit: reports/results.xml
    paths:
      - reports/
    when: always
```

### 3.3 设备池管理服务

```python
# device_pool.py
import redis
import adbutils
from dataclasses import dataclass
from typing import Optional, List
import threading
import time

@dataclass
class Device:
    serial: str
    status: str  # available, busy, offline
    android_version: str
    assigned_to: Optional[str] = None

class DevicePool:
    """设备池管理器"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url)
        self.adb = adbutils.AdbClient()
        self.lock = threading.Lock()
        self._refresh_interval = 30
        self._running = False

    def discover_devices(self) -> List[Device]:
        """发现所有已连接设备"""
        devices = []
        for d in self.adb.device_list():
            try:
                version = d.shell("getprop ro.build.version.release").strip()
                devices.append(Device(
                    serial=d.serial,
                    status="available",
                    android_version=version
                ))
            except Exception as e:
                print(f"Error discovering {d.serial}: {e}")
        return devices

    def register_devices(self, devices: List[Device]):
        """注册设备到 Redis"""
        pipe = self.redis.pipeline()
        for device in devices:
            key = f"device:{device.serial}"
            pipe.hset(key, mapping={
                "serial": device.serial,
                "status": device.status,
                "android_version": device.android_version,
                "assigned_to": device.assigned_to or ""
            })
            pipe.sadd("devices:all", device.serial)
            if device.status == "available":
                pipe.sadd("devices:available", device.serial)
        pipe.execute()

    def acquire_device(self, task_id: str,
                       min_version: str = None) -> Optional[Device]:
        """获取一个可用设备"""
        with self.lock:
            # 从可用设备集合中获取
            serial = self.redis.spop("devices:available")
            if not serial:
                return None

            serial = serial.decode() if isinstance(serial, bytes) else serial
            key = f"device:{serial}"

            # 检查版本要求
            if min_version:
                version = self.redis.hget(key, "android_version")
                version = version.decode() if version else "0"
                if version < min_version:
                    # 放回并继续找
                    self.redis.sadd("devices:available", serial)
                    return self.acquire_device(task_id, min_version)

            # 标记为占用
            self.redis.hset(key, mapping={
                "status": "busy",
                "assigned_to": task_id
            })

            data = self.redis.hgetall(key)
            return Device(
                serial=serial,
                status="busy",
                android_version=data.get(b"android_version", b"").decode(),
                assigned_to=task_id
            )

    def release_device(self, serial: str):
        """释放设备"""
        key = f"device:{serial}"
        self.redis.hset(key, mapping={
            "status": "available",
            "assigned_to": ""
        })
        self.redis.sadd("devices:available", serial)

    def get_stats(self) -> dict:
        """获取设备池统计"""
        total = self.redis.scard("devices:all")
        available = self.redis.scard("devices:available")
        return {
            "total": total,
            "available": available,
            "busy": total - available
        }

    def start_health_check(self):
        """启动健康检查线程"""
        self._running = True

        def check_loop():
            while self._running:
                try:
                    self._check_device_health()
                except Exception as e:
                    print(f"Health check error: {e}")
                time.sleep(self._refresh_interval)

        thread = threading.Thread(target=check_loop, daemon=True)
        thread.start()

    def _check_device_health(self):
        """检查设备健康状态"""
        all_serials = self.redis.smembers("devices:all")
        connected = {d.serial for d in self.adb.device_list()}

        for serial in all_serials:
            serial = serial.decode() if isinstance(serial, bytes) else serial
            key = f"device:{serial}"

            if serial not in connected:
                # 设备离线
                self.redis.hset(key, "status", "offline")
                self.redis.srem("devices:available", serial)
            else:
                # 检查是否需要恢复
                status = self.redis.hget(key, "status")
                if status == b"offline":
                    self.redis.hset(key, "status", "available")
                    self.redis.sadd("devices:available", serial)


# 使用示例
if __name__ == "__main__":
    pool = DevicePool()

    # 发现并注册设备
    devices = pool.discover_devices()
    pool.register_devices(devices)
    print(f"Registered {len(devices)} devices")

    # 启动健康检查
    pool.start_health_check()

    # 获取设备执行任务
    device = pool.acquire_device("task-001", min_version="11")
    if device:
        print(f"Acquired device: {device.serial}")
        try:
            # 执行任务...
            adb = adbutils.AdbClient()
            d = adb.device(device.serial)
            d.shell("pm list packages")
        finally:
            pool.release_device(device.serial)

    print(pool.get_stats())
```

---

## 4. GPU 虚拟化与渲染

### 4.1 GPU 透传配置

对于需要图形渲染的场景（游戏测试、UI 自动化），GPU 加速至关重要。

```bash
# 检查 GPU 驱动
nvidia-smi

# Docker GPU 支持
# 安装 NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# 验证 GPU 访问
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

```yaml
# docker-compose with GPU
services:
  redroid-gpu:
    image: redroid/redroid:12.0.0-latest
    privileged: true
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    command:
      - androidboot.redroid_gpu_mode=host
      - androidboot.redroid_gpu_node=/dev/dri/renderD128
```

### 4.2 VirGL 软件渲染

无 GPU 服务器可使用 VirGL 软件渲染：

```bash
# 安装 virglrenderer
sudo apt install virglrenderer-dev libvirglrenderer1

# Redroid 使用 guest GPU 模式
docker run -d --name redroid \
    --privileged \
    redroid/redroid:12.0.0-latest \
    androidboot.redroid_gpu_mode=guest
```

---

## 5. 网络隔离与代理

### 5.1 每设备独立网络

```yaml
# docker-compose with isolated networks
version: "3.8"

services:
  redroid-1:
    image: redroid/redroid:12.0.0-latest
    privileged: true
    networks:
      device-net-1:
        ipv4_address: 172.20.1.2
    dns:
      - 8.8.8.8

  proxy-1:
    image: mitmproxy/mitmproxy
    networks:
      device-net-1:
        ipv4_address: 172.20.1.1
    command: mitmdump --mode transparent --showhost

  redroid-2:
    image: redroid/redroid:12.0.0-latest
    privileged: true
    networks:
      device-net-2:
        ipv4_address: 172.20.2.2

networks:
  device-net-1:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.1.0/24
  device-net-2:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.2.0/24
```

### 5.2 透明代理配置

```bash
#!/bin/bash
# setup_transparent_proxy.sh

PROXY_IP="172.20.1.1"
PROXY_PORT="8080"
DEVICE_SUBNET="172.20.1.0/24"

# 启用 IP 转发
sysctl -w net.ipv4.ip_forward=1

# 配置 iptables 透明代理
iptables -t nat -A PREROUTING -s $DEVICE_SUBNET -p tcp --dport 80 \
    -j REDIRECT --to-port $PROXY_PORT
iptables -t nat -A PREROUTING -s $DEVICE_SUBNET -p tcp --dport 443 \
    -j REDIRECT --to-port $PROXY_PORT

echo "Transparent proxy configured for $DEVICE_SUBNET -> $PROXY_IP:$PROXY_PORT"
```

---

## 6. 性能优化

### 6.1 资源限制最佳实践

| 场景 | CPU | 内存 | 存储 |
|-----|-----|-----|-----|
| 轻量级任务 (爬虫) | 1-2 核 | 2GB | 8GB |
| 常规测试 | 2-4 核 | 4GB | 16GB |
| 游戏/重度 UI | 4-8 核 | 6-8GB | 32GB |

### 6.2 I/O 优化

```yaml
# 使用 tmpfs 提升 I/O 性能
services:
  redroid:
    image: redroid/redroid:12.0.0-latest
    privileged: true
    tmpfs:
      - /data/dalvik-cache:size=512m
      - /data/local/tmp:size=256m
    volumes:
      - type: tmpfs
        target: /dev/shm
        tmpfs:
          size: 268435456  # 256MB
```

### 6.3 批量操作优化脚本

```python
# parallel_operations.py
import asyncio
import adbutils
from concurrent.futures import ThreadPoolExecutor

async def install_apk_parallel(devices: list, apk_path: str, max_workers: int = 10):
    """并行安装 APK 到多个设备"""

    def install_on_device(serial: str):
        try:
            adb = adbutils.AdbClient()
            device = adb.device(serial)
            device.install(apk_path, reinstall=True)
            return serial, True, None
        except Exception as e:
            return serial, False, str(e)

    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        tasks = [
            loop.run_in_executor(executor, install_on_device, d)
            for d in devices
        ]
        results = await asyncio.gather(*tasks)

    success = [r[0] for r in results if r[1]]
    failed = [(r[0], r[2]) for r in results if not r[1]]

    print(f"Success: {len(success)}, Failed: {len(failed)}")
    for serial, error in failed:
        print(f"  {serial}: {error}")

    return success, failed

# 使用
if __name__ == "__main__":
    devices = ["localhost:5555", "localhost:5556", "localhost:5557"]
    asyncio.run(install_apk_parallel(devices, "./app.apk"))
```

---

## 7. 常见问题排查

### 7.1 Redroid 启动失败

```bash
# 问题: binder 驱动未加载
dmesg | grep -i binder
# 解决: 加载内核模块
sudo modprobe binder_linux devices="binder,hwbinder,vndbinder"

# 问题: 权限不足
# 解决: 确保使用 --privileged 或正确的 capabilities
docker run --privileged ...

# 问题: SELinux 阻止
# 解决: 临时禁用或配置策略
sudo setenforce 0
```

### 7.2 ADB 连接问题

```bash
# 检查设备状态
adb devices -l

# 重置 ADB 服务
adb kill-server && adb start-server

# 指定端口连接
adb connect 192.168.1.100:5555

# 检查网络连通性
docker exec redroid-1 ping -c 3 host.docker.internal
```

### 7.3 性能问题诊断

```bash
# 检查容器资源使用
docker stats redroid-1 redroid-2 redroid-3

# 检查 Android 系统负载
adb shell top -n 1

# 检查内存使用
adb shell cat /proc/meminfo

# 检查存储空间
adb shell df -h
```

---

## 8. 总结

虚拟化和容器化是从"手工作坊"迈向"工业化生产"的第一步。

| 技术 | 解决的问题 | 关键优势 |
|-----|-----------|---------|
| **Android 模拟器** | 设备从哪里来 | 可大规模复制的隔离环境 |
| **Docker 容器** | 依赖如何管理 | 标准化、可移植的交付物 |
| **设备池管理** | 资源如何调度 | 动态分配、高效利用 |
| **网络隔离** | 流量如何控制 | 独立代理、精确监控 |

二者结合，为上层的自动化和群控系统提供了坚实、可靠、可扩展的基础设施。

**推荐下一步**：[自动化设备农场](./automation_and_device_farming.md)
