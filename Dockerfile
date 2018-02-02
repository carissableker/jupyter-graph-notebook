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


# Python packages from pip
RUN pip install --quiet --no-cache-dir\
    py2cytoscape \
    visJS2jupyter && \
    fix-permissions $CONDA_DIR

COPY bnv_tools /opt/bnv_tools/
COPY bnv_tools.pth "$CONDA_DIR"/lib/python3.6/site-packages/


