FROM quay.io/pypa/manylinux2014_x86_64

ENV MMG_ROOT=/external_libraries/mmg/mmg_5_8_0
ENV LD_LIBRARY_PATH ${LD_LIBRARY_PATH}:{MMG_ROOT}/lib

# Prepare package dependencies
RUN yum install -y git wget zip

# Prepare Shared Volumes
RUN mkdir -p /data_swap_guest

# Prepare File System
RUN mkdir -p /workspace/scripts; \
	mkdir -p /workspace/kratos; \
    mkdir -p /workspace/boost

# Install Boost (from source)
# RUN git clone -b 'boost-1.74.0' --depth 1 --recurse-submodules -j24 https://github.com/boostorg/boost.git /workspace/boost/boost_1_74_0

# Install Boost (form zip)
RUN wget -P /workspace/boost https://archives.boost.io/release/1.74.0/source/boost_1_74_0.tar.gz; \
	tar -C /workspace/boost -xzf /workspace/boost/boost_1_74_0.tar.gz; \
	rm /workspace/boost/boost_1_74_0.tar.gz

# Install MMG 5.8.0
# Note ( upgraded from 5.4.1 because of https://github.com/MmgTools/mmg/issues/85)
RUN mkdir -p /workspace/mmg_5_8_0
RUN git clone -b 'v5.8.0' --depth 1 https://github.com/MmgTools/mmg /workspace/mmg_5_8_0 && \
    mkdir /workspace/mmg_5_8_0/build && \
    mkdir -p /workspace/external_libraries/mmg/mmg_5_8_0 && \
    cd /workspace/mmg_5_8_0/build && \
    cmake .. -DCMAKE_RULE_MESSAGES=OFF -DCMAKE_C_FLAGS="-w" -DCMAKE_CXX_FLAGS="-w" -DCMAKE_INSTALL_PREFIX="/workspace/external_libraries/mmg/mmg_5_8_0" -DLIBMMG3D_SHARED=ON -DLIBMMG2D_SHARED=ON -DLIBMMGS_SHARED=ON -DLIBMMG_SHARED=ON && \
    make -j2 install && \
    rm -r /workspace/mmg_5_8_0 && \
    cd /

RUN git clone --depth 1 -b geo/stem_branch https://github.com/KratosMultiphysics/Kratos.git /workspace/kratos/Kratos

# overwrite the default configuration
COPY build.sh /workspace/kratos/Kratos/scripts/wheels/linux
COPY configure.sh /workspace/kratos/Kratos/scripts/wheels/linux

RUN chmod +x /workspace/kratos/Kratos/scripts/wheels/linux/build.sh

ENTRYPOINT ["/bin/bash", "/workspace/kratos/Kratos/scripts/wheels/linux/build.sh"]
