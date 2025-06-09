import ctypes
import numpy as np
import serial
import time
from get_path import get_actual_path


dll_path = get_actual_path('./ForPy/EEGSENSOR.dll')
# 加载一个DLL文件
eegs_dll = ctypes.CDLL(dll_path)  # Replace with the actual path to your DLL

#这两个函数在代码的前半部分只是进行了定义，还没有实际调用

# 用于解析EEG数据帧
eegs_dll.ThreeLead_EEGSensor_DataFrameParse.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_double)]
eegs_dll.ThreeLead_EEGSensor_DataFrameParse.restype = ctypes.POINTER(ctypes.c_double)

#用于去除EEG数据中的噪声
eegs_dll.ThreeLead_EEGSensor_DataDSP.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)]
eegs_dll.ThreeLead_EEGSensor_DataDSP.restype = ctypes.POINTER(ctypes.c_double)

#存储原始字节数据
rawbyte = (ctypes.c_ubyte * 37)()
#存储解析后的电压数据
series_port_leads_datas = (ctypes.c_double * 3)()


#通过指定的端口和波特率 与设备进行通信,如果1秒内没有读取到任何数据，读操作将会超时并返回
port = 'COM9'
baudrate = 115200
#这个串口对象用于 数据读取 和 写入操作。
ser = serial.Serial(port, baudrate, timeout=1)


#处理每个数据帧并去除噪声。
def process_received_data(data, accumulated_voltage):
    # 填充 rawbyte 数组
    for i in range(min(len(data), 37)):
        rawbyte[i] = data[i]

    # 调用解析函数
    real_voltage_value = eegs_dll.ThreeLead_EEGSensor_DataFrameParse(rawbyte, series_port_leads_datas)

    # 将解析出的电压值添加到 accumulated_voltage 列表中
    accumulated_voltage.append(real_voltage_value[0])
    accumulated_voltage.append(real_voltage_value[1])
    accumulated_voltage.append(real_voltage_value[2])

    # 如果累积的电压值足够多
    if len(accumulated_voltage) >= 250 * 3:
        raw_eeg_data_fp1_fp2 = (ctypes.c_double * (250 * 3))(*accumulated_voltage[:250 * 3])
        dsp_eeg_data_fp1_fp2_fpz = (ctypes.c_double * (250 * 3))()

        # 调用去噪函数
        eeg_data_without_noise = eegs_dll.ThreeLead_EEGSensor_DataDSP(raw_eeg_data_fp1_fp2, dsp_eeg_data_fp1_fp2_fpz)

        # 将去噪后的数据转换为 NumPy 数组
        eeg_data_without_noise_array = np.ctypeslib.as_array(ctypes.cast(eeg_data_without_noise, ctypes.POINTER(ctypes.c_double * (250 * 3))).contents)

        # 将数据重塑为3通道格式 (Fp1, Fp2, Fpz)
        eeg_data_without_noise_array = eeg_data_without_noise_array.reshape((250, 3))

        # 移除已使用的数据
        accumulated_voltage = accumulated_voltage[250 * 3:]

        return eeg_data_without_noise_array, accumulated_voltage

    return None, accumulated_voltage

def read_frame():
    # 函数用于从串口读取数据帧。它不断读取串口数据，直到找到一个完整的数据帧（包括帧头和帧尾），然后返回该数据帧。
    while True:
        # 读取一个字节
        byte1 = ser.read(1)

        # 如果这个字节是帧头的第一个字节 0xA0
        if byte1[0] == 0XA0:

            # 再读取一个字节
            byte2 = ser.read(1)

            # 如果这个字节是帧头的第二个字节 0x10
            if byte2[0] == 0X10:

                # 读取其余的35个字节，形成一个完整的37字节帧
                frame = byte1 + byte2 + ser.read(35)

                # 检查帧的最后一个字节是否是帧尾 0xC0
                if frame[-1] == 0xC0:

                    # 返回完整的37字节帧
                    return frame

def eeg_main():
     # 整个程序的目的是通过串口从EEG传感器读取数据，解析并处理这些数据，去除噪声，然后保存处理后的数据到CSV文件中。
    try:
        #在主程序中，首先通过串口发送初始化命令，然后开始读取数据帧并处理接收的数据。累积到足够多的数据后，将其保存到CSV文件中。

        # 发送初始命令到设备（如果需要）
        print("Sending 'a'...")
        # 发送'uaisa'字符串以启动通信
        ser.write(b'uaisa')
        ser.flush()
        # 等待5秒以确保设备准备好
        time.sleep(5)

        # 开始从串口读取数据
        print("Starting to read data...")

        # 初始化一个空数组以累积数据  即 0 行 3 列的二维数组。
        accumulated_data = np.empty((0, 3))
        # 初始化一个列表以累积电压值
        accumulated_voltage = []

        while True:
            # 读取一个数据帧
            frame = read_frame()
            if frame:
                #eeg_data_without_noise_array:去除噪声后的EEG数据
                #accumulated_voltage:累积电压值列表
                eeg_data_without_noise_array, accumulated_voltage = process_received_data(frame, accumulated_voltage)
                if eeg_data_without_noise_array is not None:
                    #将去噪后的EEG数据添加到累积的数据中
                    column1, column2, column3 = eeg_data_without_noise_array.transpose().tolist()
                    print(column1, column2, column3)

                    accumulated_data = np.vstack((accumulated_data, eeg_data_without_noise_array))  # Append new data

                #array([[  1.0,   2.0,   3.0],[  4.0,   5.0,   6.0], ...[250.0, 251.0, 252.0]])
                # 如果累积数据的行数达到18000
                if accumulated_data.shape[0] >= 18000:
                    break

        # 输出累积数据的形状和内容
        print("Accumulated Data Shape:", accumulated_data.shape)
        print("Accumulated Data:", accumulated_data)

        # 将累积数据保存到CSV文件
        import pandas as pd
        df = pd.DataFrame(data=accumulated_data)
        df.to_csv('eegData2.csv', index=False, header=False)

    except Exception as e:
        print("Error:", e)

    finally:
        # 关闭串口
        ser.close()

if __name__ == '__main__':
    eeg_main()

