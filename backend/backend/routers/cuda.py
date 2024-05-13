from fastapi import APIRouter
from pynvml import *

cuda_router = APIRouter()


@cuda_router.get("/{device_id}")
async def device_info(device_id: int):
    # 获取设备
    handle = nvmlDeviceGetHandleByIndex(device_id)
    # 获取设备的利用率
    utilization = nvmlDeviceGetUtilizationRates(handle)
    # 获取设备的显存信息
    memory_info = nvmlDeviceGetMemoryInfo(handle)
    # 将设备信息添加到列表中
    ret = {
        "device_id": device_id,
        "gpu_utilization": utilization.gpu,
        "memory_utilization": 100 * memory_info.used / memory_info.total,
    }

    return ret


@cuda_router.get("")
async def avaliable_device():
    device_count = nvmlDeviceGetCount()
    device_info = []

    for i in range(device_count):
        # 获取设备
        handle = nvmlDeviceGetHandleByIndex(i)

        # 获取设备的利用率
        utilization = nvmlDeviceGetUtilizationRates(handle)

        # 获取设备的显存信息
        memory_info = nvmlDeviceGetMemoryInfo(handle)

        # 将设备信息添加到列表中
        device_info.append(
            {
                "device_id": i,
                "gpu_utilization": utilization.gpu,
                "memory_utilization": 100 * memory_info.used / memory_info.total,
            }
        )

    return device_info
