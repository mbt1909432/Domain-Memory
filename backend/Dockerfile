# 使用官方 Python 3.11 作为基础镜像
FROM python:3.11-slim-bookworm AS build

# 设置工作目录
WORKDIR /backend

# 复制 requirements.txt 文件到容器中
COPY requirements.txt .

# 打印 requirements.txt 的内容


#查看requirements.txt类型 二进制的话有问题
# 安装 file 命令
#RUN apt-get update && apt-get install -y file && rm -rf /var/lib/apt/lists/*
#RUN file requirements.txt

#更新
# 从 requirements.txt 中排除 mysqlclient   解决2进制文本问题？？
#RUN strings requirements.txt | grep -v "mysqlclient==2.2.7" > temp_requirements.txt
#RUN grep -v -e "mysqlclient==2.2.7" -e "aiohttp==3.9.3" requirements.txt > temp_requirements.txt
#忽略二进制警告-av 强制视为文本文件
#RUN grep -av "mysqlclient==2.2.7" requirements.txt > temp_requirements.txt
RUN grep -v "mysqlclient==2.2.7" requirements.txt > temp_requirements.txt
RUN echo "Contents of requirements.txt:" && cat requirements.txt
RUN echo "Contents of temp_requirements.txt:" && cat temp_requirements.txt

# 安装系统依赖（关键更新）
# 安装系统依赖 解决编译问题
# MySQL
# 这里可以添加其他系统依赖的安装命令，例如：
# RUN apt-get update && apt-get install -y <your-system-dependencies>

# 更新 pip 并安装依赖
# 安装依赖，包括 uvicorn
# 升级 pips
RUN python3.11 -m pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple --upgrade pip

# 安装 requirements.txt 中的依赖
RUN pip install -r temp_requirements.txt --no-cache-dir  -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple --upgrade pip
#镜像

#aiohttp==3.9.3版本找不到？？
#RUN pip install aiohttp  -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple --upgrade pip


# 清理临时文件
RUN rm temp_requirements.txt

# 复制开发依赖文件到容器中
COPY requirements_dev.txt .

# 打印 requirements_dev.txt 的内容
RUN echo "Contents of requirements_dev.txt:" && cat requirements_dev.txt

# 安装开发依赖
RUN pip install -r requirements_dev.txt --no-cache-dir  -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple --upgrade pip

RUN pip install psycopg2-binary
RUN pip install redis


# 复制应用程序代码
COPY . .

# 暴露应用程序端口
EXPOSE 8111

# 启动 Uvicorn 服务器
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8111"]
