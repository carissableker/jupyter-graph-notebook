FROM jupyter/scipy-notebook
USER jovyan

# Python packages from conda
RUN conda config --add channels conda-forge
RUN conda install -y \
    py2neo \
    igraph \
    networkx \

# Python packages from pip and conda 
RUN pip install \
    py2cytoscape \
    visJS2jupyter 
