FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-devel

RUN apt-get update
RUN apt-get install -y apt-utils
# Install wget
RUN apt-get install -y wget curl postgresql-client net-tools iputils-ping vim

# micromamba
COPY ./dep/linux_mb.tar.bz2 /conf/linux_mb.tar.bz2
RUN mkdir /micromamba
RUN tar -xjf /conf/linux_mb.tar.bz2 -C /micromamba
RUN /micromamba/bin/micromamba shell init -s bash -p ~/micromamba
RUN echo "alias mb=micromamba" >> ~/.bashrc
RUN echo "alias conda=micromamba" >> ~/.bashrc
RUN rm /conf/linux_mb.tar.bz2

# # Create the env for the backend
COPY ./requirements.txt /conf/requirements.txt
RUN /micromamba/bin/micromamba create -n backend -c conda-forge python=3.10
RUN /micromamba/bin/micromamba run -n backend pip install -r /conf/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN /micromamba/bin/micromamba run -n backend pip install "bitsandbytes==0.41.2.post2" -i https://pypi.tuna.tsinghua.edu.cn/simple

# Copy the files
COPY . /backend

# Install the backend
WORKDIR /backend
RUN /micromamba/bin/micromamba run -n backend pip install -e .

CMD /micromamba/bin/micromamba run -n backend uvicorn backend.main:app --host 0.0.0.0
