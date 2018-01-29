FROM jupyter/scipy-notebook
USER jovyan

# Python packages from conda
RUN conda config --add channels conda-forge
RUN conda install -y \
    py2neo \
    python-igraph \
    networkx && conda clean --all


# Python packages from pip
RUN pip install \
    py2cytoscape \
    visJS2jupyter 
