FROM jupyter/scipy-notebook
USER jovyan

# Python packages from conda
RUN conda install -y \
    py2neo \
    igraph \
    visJS2jupyter
