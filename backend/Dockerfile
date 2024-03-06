FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-devel

RUN apt-get update
RUN apt-get install -y apt-utils
# Install wget
RUN apt-get install -y git git-lfs wget curl postgresql-client net-tools iputils-ping vim


# micromamba
COPY ./dep/linux_mb.tar.bz2 /conf/linux_mb.tar.bz2
RUN mkdir /micromamba
RUN tar -xjf /conf/linux_mb.tar.bz2 -C /micromamba
RUN /micromamba/bin/micromamba shell init -s bash -p ~/micromamba
RUN echo "alias mb=micromamba" >> ~/.bashrc
RUN echo "alias conda=micromamba" >> ~/.bashrc
RUN rm /conf/linux_mb.tar.bz2

# Create the env for the backend
COPY ./requirements.txt /conf/requirements.txt
RUN /micromamba/bin/micromamba create -y -n backend -c conda-forge python=3.10
# Install packaging
RUN /micromamba/bin/micromamba run -n backend pip install packaging -i https://pypi.tuna.tsinghua.edu.cn/simple/

# Cache some very large packages
RUN /micromamba/bin/micromamba run -n backend pip install nvidia-cublas-cu12==12.1.3.1 -i https://pypi.tuna.tsinghua.edu.cn/simple/
RUN /micromamba/bin/micromamba run -n backend pip install torch==2.2.0 -i https://pypi.tuna.tsinghua.edu.cn/simple/
RUN /micromamba/bin/micromamba run -n backend pip install nvidia-cuda-cupti-cu12==12.1.105 -i https://pypi.tuna.tsinghua.edu.cn/simple/
RUN /micromamba/bin/micromamba run -n backend pip install nvidia-cuda-nvrtc-cu12==12.1.105 -i https://pypi.tuna.tsinghua.edu.cn/simple/
RUN /micromamba/bin/micromamba run -n backend pip install nvidia-cuda-runtime-cu12==12.1.105 -i https://pypi.tuna.tsinghua.edu.cn/simple/
RUN /micromamba/bin/micromamba run -n backend pip install scipy==1.11.4 -i https://pypi.tuna.tsinghua.edu.cn/simple/
RUN /micromamba/bin/micromamba run -n backend pip install mkl-service==2.4.0 -i https://pypi.tuna.tsinghua.edu.cn/simple/

RUN /micromamba/bin/micromamba run -n backend pip install -r /conf/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# Use the transformers from huggingface
RUN /micromamba/bin/micromamba run -n backend pip install git+https://github.com/huggingface/transformers
RUN /micromamba/bin/micromamba run -n backend pip install accelerate==0.27.2 -i https://pypi.tuna.tsinghua.edu.cn/simple/
RUN /micromamba/bin/micromamba run -n backend pip install deepspeed==0.13.4 -i https://pypi.tuna.tsinghua.edu.cn/simple/

# Copy the files
COPY . /backend

# Install the backend
WORKDIR /backend
RUN /micromamba/bin/micromamba run -n backend pip install -e .

CMD /micromamba/bin/micromamba run -n backend uvicorn backend.main:app --host 0.0.0.0 > ./logs/output.log 2>&1