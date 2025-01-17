import os
import requests
from Crypto.Cipher import AES
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

base_url = "" # 目标网址

# 配置请求头(防止拦截)
headers = {
    "User-Agent": "",   # 浏览器代理
    "Referer": base_url,
    "Origin": base_url,
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Cache-Control": "no-cache",
    "Accept": "*/*",
}

# 下载单个 TS 文件，无限重试
def download_ts_file(task, retry_delay=5):
    url, output_path, decryptor = task
    while True:
        try:
            response = requests.get(url, stream=True, headers=headers)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                if decryptor:
                    # 如果需要解密
                    encrypted_data = response.content
                    decrypted_data = decryptor.decrypt(encrypted_data)
                    f.write(decrypted_data)
                else:
                    # 如果不需要解密，直接保存
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            print(f"下载成功: {output_path}")
            return  # 成功后退出函数
        except Exception as e:
            print(f"下载失败 {url}，正在重试: {e}")
            time.sleep(retry_delay)  # 等待后重试

# 下载所有 TS 文件
def download_ts_files(m3u8_url, output_dir, max_threads=4, retry_delay=5):
    try:
        # 步骤 1：获取 M3U8 文件内容
        response = requests.get(m3u8_url)
        response.raise_for_status()
        m3u8_content = response.text.splitlines()
        
        # 步骤 2：解析 M3U8 文件
        decryptor = None
        tasks = []
        for line in m3u8_content:
            if line.startswith("#EXT-X-KEY"):  # 处理加密密钥
                # 提取密钥 URI 和 IV
                key_uri = base_url + line.split("URI=")[1].split(",")[0].strip('"')
                iv = line.split("IV=")[1].strip()
                
                # 下载密钥
                key_response = requests.get(key_uri)
                key_response.raise_for_status()
                key = key_response.content
                
                # 初始化解密器(根据需要调整)
                decryptor = AES.new(key, AES.MODE_CBC, bytes.fromhex(iv[2:]))
            elif line and not line.startswith("#"):  # 收集 TS 文件下载任务
                ts_url = line.strip()
                ts_filename = os.path.basename(ts_url)
                output_path = os.path.join(output_dir, ts_filename)
                tasks.append((ts_url, output_path, decryptor))
        
        # 步骤 3：使用线程池下载 TS 文件
        with ThreadPoolExecutor(max_threads) as executor:
            futures = {executor.submit(download_ts_file, task, retry_delay): task for task in tasks}
            for future in as_completed(futures):
                task = futures[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"任务失败: {task[0]}, 错误: {e}")
        
        print("所有 TS 文件下载完成！")
    except Exception as e:
        print(f"处理 M3U8 文件时出错: {e}")

# 主程序
if __name__ == "__main__":
    # M3U8 文件的 URL（替换为你的实际 M3U8 链接）
    m3u8_url = ""

    # 输出目录
    output_dir = "ts_files"
    os.makedirs(output_dir, exist_ok=True)
    
    # 开始下载 TS 文件，设置最大线程数
    max_threads = os.cpu_count() or 4  # 使用系统 CPU 核心数，默认至少 4 个线程
    download_ts_files(m3u8_url, output_dir, max_threads=max_threads)
