from py2neo import Graph, Node, Relationship

import igraph as ig
import visJS2jupyter.visJS_module

from IPython.display import display
import ipywidgets as widgets

import pandas as  pd
import re
import matplotlib.pyplot as plt
import numpy as np
import matplotlib


def __load_vertices(graph, entities_file, periodic=1000, Key_Name='vertex_key_file.tsv'):
    progress = widgets.IntText(value=0, disabled=True, 
                               description = 'Number vertices loaded (in increments of %i): '%periodic,
                               style={'description_width':'initial'})
    progress.layout.width = 'initial'
    display(progress)
    
    
    tx = graph.begin()
    
    Key = open(Key_Name, 'a') 
    
    with open(entities_file, 'r') as f:

        for i, line in enumerate(f):
            line = re.sub(r'\<i\>|\<\/i\>', '', line)
            xid, xtype, name, other = re.match('^N\s.node\s(.*);type:\"(.*)\",name:\"(.*?)\",?(.*)?$', line).groups()
            D = {"id":xid, 'name':name}

            xtype = re.sub(r'-', '_', xtype)

            if other != '':
                 for attribute, value in [av.split(':', 1) for av in re.split(''',(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', other)]:
                        attribute = re.sub(r'-', '_', attribute.lower())
                        D[attribute] = "%s"%value
            
            q = '''MERGE (node:%s {%s}) RETURN ID(node)'''%(xtype, ','.join(['%s:"%s"'%(key, D[key].strip('"')) for key in D]))

            
            #node_id = tx.run(q).evaluate()
            Key.write('%s\t%s\n'%(xid, tx.run(q).evaluate()))
            

            if i%periodic == 0:
                tx.commit()
                tx = graph.begin()
                progress.value = i

    if not tx.finished():
        tx.commit()
        progress.value = i
    
    progress.close()    
    Key.close()

def __load_edges(graph, relationships_file, periodic=1000, Key_Name='vertex_key_file.tsv'):
    
    progress = widgets.IntText(value=0, disabled=True, 
                               description = 'Number edges loaded (in increments of %i): '%periodic,
                               style={'description_width':'initial'})
    progress.layout.width = 'initial'
    display(progress)
    
    tx = graph.begin()

    Key_Dict = {}               
    with open(Key_Name, 'r') as k:
        for line in k:
            key, value = line.rstrip().split('\t')
            Key_Dict[key] = int(value)
                          
    with open(relationships_file, 'r') as f:
        for i, line in enumerate(f):
            source, xtype, other, target = re.match('^R\s(.*);(.*?)(?:,(.*))?;(.*)$', line).groups()
            D = {}

            if other != '' and other != None:
                    for attribute, value in [av.split(':') for av in re.split(''',(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', other)]:
                        attribute = re.sub(r'-', '_', attribute.lower())
                        D[attribute] = "%s"%value
            
            try:
                source_node = graph.node(Key_Dict[source])
                target_node = graph.node(Key_Dict[target])
            except KeyError as e:
                print('Missing vertex:', e)
                continue
            
            rel = Relationship(source_node, xtype, target_node, **D)
            
            tx.create(rel)
        
            if i%periodic == 0:
                tx.commit()
                tx = graph.begin() 
                progress.value = i
    
    if not tx.finished():
        tx.commit()    
        progress.value = i
    
    progress.close()    


def load_ecocyc(graph, entities_file, relationships_file, Key_Name='vertex_key_file.tsv'):
    __load_vertices(graph, entities_file, Key_Name=Key_Name)
    __load_edges(graph, relationships_file, Key_Name=Key_Name)
    
    
def query_graph(graph, source='', target='', edge=''):
    
    if not source == '':
            source = ':' + source
    if not target == '':
            target = ':' + target
    if not edge == '':
            edge = ':' + edge
            
    query = """
    MATCH (s%s)-[r%s]->(t%s)
    RETURN s.name AS source, t.name AS target, TYPE(r) AS type
    """%(source, edge, target)

    cursor = graph.run(query)
 
    return  pd.DataFrame(cursor.data())


def prepare_plot_igraph(sub_igraph, 
                        layout='fruchterman_reingold', 
                        positions=None, 
                        scale=10, 
                        edge_cmap=plt.cm.tab20c, 
                        vertex_cmap=plt.cm.tab20):

    # calculate layout if needed
    if positions is None: 
        positions=sub_igraph.layout(layout)

    # color edges
    d_edge = {}
    uniq_edge_att = set(g.es['type'])
    edge_cmap_values = edge_cmap(np.arange(len(uniq_edge_att))/len(uniq_edge_att), alpha=1)
    for att, row in zip(uniq_edge_att, edge_cmap_values):
        d_edge[att] = matplotlib.colors.rgb2hex(row)
    
    # color vertices
    d_vertex = {}
    uniq_vertex_att = set(g.vs['type'])
    vertex_cmap_values = vertex_cmap(np.arange(len(uniq_vertex_att))/len(uniq_vertex_att), alpha=1)
    for att, row in zip(uniq_vertex_att, vertex_cmap_values):
        d_vertex[att] = matplotlib.colors.rgb2hex(row)
      
    nodes_dict = [{"id":n.attributes()['name'],
                   "x":positions[n.index][0]*scale,
                   "y":positions[n.index][1]*scale,  
                   "degree":sub_igraph.degree(n), 
                   "color":d_vertex[n.attributes()["type"]]
                  } for n in sub_igraph.vs()]
   
    edges_dict = [{"source":n.source, 
                   "target":n.target,
                   "type":n.attributes()["type"],
                   "color":d_edge[n.attributes()["type"]]
                  } for n in sub_igraph.es()]

    return nodes_dict, edges_dict

