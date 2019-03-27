FROM jupyter/scipy-notebook

USER $NB_USER

# Python packages from conda
RUN conda config --add channels conda-forge
RUN conda install --quiet --yes \
    py2neo \
    python-igraph \
    networkx \
    plotly && \
    conda clean -tipsy && \
    fix-permissions $CONDA_DIR

# fix ggplot bug
RUN pip install --quiet --no-cache-dir git+https://github.com/sushinoya/ggpy 

# Python packages from pip
RUN pip install --quiet --no-cache-dir\
    py2cytoscape \
    visJS2jupyter && \
    fix-permissions $CONDA_DIR

