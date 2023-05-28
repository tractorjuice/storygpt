from matplotlib.collections import LineCollection
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib
import re
import streamlit as st
   
# your WardleyMap class here...
class WardleyMap():

    # Developed using https://regex101.com/
    _coords_regexs = "\[\s*([\d\.-]+)\s*,\s*([\d\.-]+)\s*\]"
    _node_regex = re.compile(r"^(\w+) ([a-zA-Z0-9_.,/&' +)(?-]+)\s+{COORDS}(\s+label\s+{COORDS})*".format(COORDS=_coords_regexs))
    _evolve_regex = re.compile(r"^evolve ([\w \/',)(-]+)\s+([\d\.-]+)(\s+label\s+{COORDS})*".format(COORDS=_coords_regexs))
    _pipeline_regex = re.compile(r"^pipeline ([a-zA-Z0-9_.,/&' )(?-]+)\s+\[\s*([\d\.]+)\s*,\s*([\d\.]+)\s*\]$")
    _note_regex = re.compile(r"^(\w+) ([\S ]+)\s+{COORDS}\s*".format(COORDS=_coords_regexs))

    def __init__(self, owm):
        # Defaults:
        self.title = None
        self.nodes = {}
        self.edges = []
        self.bluelines = []
        self.evolutions = {}
        self.evolves = {}
        self.pipelines = {}
        self.annotations = []
        self.annotation = {}
        self.notes = []
        self.style = None
        self.warnings = []
   
        # And load:
        for cl in owm.splitlines():
            cl = cl.strip()
            if not cl:
                continue
                
            elif cl.startswith('#'):
                # Skip comments...
                continue
                
            elif cl.startswith('//'):
                # Skip comments...
                continue
                
            elif cl.startswith('annotation '):
                warning_message = "Displaying annotation not supported yet"
                if warning_message not in self.warnings:
                    self.warnings.append(warning_message)
                continue
                
            elif cl.startswith('annotations '):
                warning_message = "Displaying annotations not supported yet"
                if warning_message not in self.warnings:
                    self.warnings.append(warning_message)
                continue
                
            elif cl.startswith('market '):
                warning_message = "Displaying market not supported yet"
                if warning_message not in self.warnings:
                    self.warnings.append(warning_message)
                continue
  
            elif cl.startswith('pipeline '):
                match = self._pipeline_regex.search(cl)
                if match != None:
                    matches = match.groups()
                    pipeline = {
                        'title': matches[0],
                        'start_mat' : float(matches[1]),
                        'end_mat' : float(matches[2]),
                    }

                    # And store it:
                    self.pipelines[matches[0]] = pipeline
                    continue
                else:
                    self.warnings.append("Could not parse pipeline: %s" % cl)
                
            elif cl.startswith('evolution '):
                warning_message = "Displaying evolution not supported yet"
                if warning_message not in self.warnings:
                    self.warnings.append(warning_message)
                    continue
                    
            if cl.startswith('title '):
                self.title = cl.split(' ', maxsplit=1)[1]
                continue
                
            elif cl.startswith('style '):
                self.style = cl.split(' ', maxsplit=1)[1]
                continue
                
            elif cl.startswith('anchor ') or cl.startswith('component '):
                # Use RegEx to split into fields:
                match = self._node_regex.search(cl)
                if match != None:
                    matches = match.groups()
                    node = {
                        'type' : matches[0],
                        'title': matches[1],
                        'vis' : float(matches[2]),
                        'mat' : float(matches[3])
                    }
                    # Handle label position adjustments:
                    if matches[4]:
                        node['label_x'] = float(matches[5])
                        node['label_y'] = float(matches[6])
                    else:
                        # Default to a small additional offset:
                        node['label_x'] = 2
                        node['label_y'] = 2
                    # And store it:
                    self.nodes[node['title']] = node
                else:
                    self.warnings.append("Could not parse component line: %s" % cl)
            
            elif cl.startswith('evolve '):
                match = self._evolve_regex.search(cl)
                if match != None:
                    matches = match.groups()
                    evolve = {
                        'title': matches[0],
                        'mat' : float(matches[1])
                    }
                    # Handle label position adjustments:
                    if matches[3] is not None:
                        evolve['label_x'] = float(matches[3])
                    else:
                        evolve['label_x'] = 2
                        
                    if matches[4] is not None:
                        evolve['label_y'] = float(matches[4])
                    else:
                        evolve['label_y'] = 2

                    # And store it:
                    self.evolves[matches[0]] = evolve
                    continue
                else:
                    self.warnings.append("Could not parse evolve line: %s" % cl)
                    
            elif "->" in cl:
                edge_parts = cl.split('->')
                if len(edge_parts) != 2:
                    self.warnings.append(f"Unexpected format for edge definition: {cl}. Skipping this edge.")
                    continue
                n_from, n_to = edge_parts
                self.edges.append([n_from.strip(), n_to.strip()])
 
            elif "+<>" in cl:
                edge_parts = cl.split('+<>')
                if len(edge_parts) != 2:
                    self.warnings.append(f"Unexpected format for blueline definition: {cl}. Skipping this edge.")
                    continue
                n_from, n_to = edge_parts
                self.bluelines.append([n_from.strip(), n_to.strip()])
                continue

            elif cl.startswith('note'):
                match = self._note_regex.search(cl)
                if match != None:
                    matches = match.groups()
                    note = {
                        'text' : matches[1],
                    }
                    # Handle text position adjustments:
                    if matches[2]:
                        note['vis'] = float(matches[2])
                        note['mat'] = float(matches[3])
                    else:
                        # Default to a small additional offset:
                        note['vis'] = .2
                        note['mat'] = .2
                    # And store it:
                    self.notes.append( note)
                else:
                    self.warnings.append("Could not parse note line: %s" % cl)
            else:
                # Warn about lines we can't handle?
                self.warnings.append("Could not parse line: %s" % cl)

        self.warnings = list(set(self.warnings))
                
def wardley(map):
    
    # Parse the OWM syntax:
    wm = WardleyMap(map)
    
    # Now plot, with styles:
    fig = None
    figsize = (8,5)
    matplotlib.rcParams.update(matplotlib.rcParamsDefault)
    
    if wm.style is None:
        wm.style = 'wardley'
        
    if wm.style == 'wardley':
        # Use a monospaced font:
        matplotlib.rcParams['font.family'] = 'monospace'
        matplotlib.rcParams['font.size'] = 4
        # Set up the default plot:
        fig, ax = plt.subplots(figsize=figsize)
        # Add the gradient background
        norm = matplotlib.colors.Normalize(0,1)
        colors = [[norm(0.0), "white"], [norm(0.5), "white"], [norm(1.0), "#f6f6f6"]]
        cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", colors)
        plotlim = plt.xlim() + plt.ylim()
        ax.imshow([[1,0,1],[1,0,1]], cmap=cmap, interpolation='bicubic', extent=plotlim, aspect='auto')
        # And plot as normal:
        generate_wardley_plot(ax, wm)
    elif wm.style in ['handwritten']:
        matplotlib.rcParams['font.family'] = 'Gloria Hallelujah'
        fig, ax = plt.subplots(figsize=figsize)
        generate_wardley_plot(ax, wm)
    elif wm.style in ['default', 'plain']:
        fig, ax = plt.subplots(figsize=figsize)
        generate_wardley_plot(ax, wm)
    elif wm.style in plt.style.available:
        with plt.style.context(wm.style):
            fig, ax = plt.subplots(figsize=figsize)
            generate_wardley_plot(ax, wm)
    elif wm.style != None:
        wm.warnings.append("Map style '%s' not recognised or supported." % wm.style)

    wm.warnings = list(set(wm.warnings))
    return wm, fig
                              
# Actually plot:
def generate_wardley_plot(ax, wm):
    # Set up basic properties:
    if wm.title:
        plt.title(wm.title)
    plt.xlim(0, 1)
    plt.ylim(0, 1.1)

    # Plot the lines
    l = []
    for edge in wm.edges:
        if edge[0] in wm.nodes and edge[1] in wm.nodes:
            n_from = wm.nodes[edge[0]]
            n_to = wm.nodes[edge[1]]
            l.append([ (n_from['mat'],n_from['vis']), (n_to['mat'],n_to['vis']) ])
        else:
            for n in edge:
                if n not in wm.nodes:
                    wm.warnings.append(f"Could not find component called {n}!")
    if len(l) > 0:
        lc = LineCollection(l, color=matplotlib.rcParams['axes.edgecolor'], lw=0.5)
        ax.add_collection(lc)
        
    # Plot blue lines
    b = []
    for blueline in wm.bluelines:
        if blueline[0] in wm.nodes and blueline[1] in wm.nodes:
            n_from = wm.nodes[blueline[0]]
            n_to = wm.nodes[blueline[1]]
            b.append([ (n_from['mat'],n_from['vis']), (n_to['mat'],n_to['vis']) ])
        else:
            for n in blueline:
                if n not in wm.nodes:
                    wm.warnings.append(f"Could not find blueline component called {n}!")
    if len(b) > 0:
        lc = LineCollection(b, color='blue', lw=1)
        ax.add_collection(lc)
                                     
    # Plot Evolve
    e = []
    for evolve_title, evolve in wm.evolves.items():
        if evolve_title in wm.nodes:
            n_from = wm.nodes[evolve_title]
            e.append([ (n_from['mat'],n_from['vis']), (evolve['mat'], n_from['vis']) ])
        else:
            wm.warnings.append(f"Could not find evolve component called {evolve_title}!")
    if len(e) > 0:
        lc = LineCollection(e, color='red', lw=.5, linestyles='dotted')
        ax.add_collection(lc)

    # Add the nodes:
    for node_title in wm.nodes:
        n = wm.nodes[node_title]
        if n['type'] == 'component':
            plt.plot(n['mat'], n['vis'], marker='o', color=matplotlib.rcParams['axes.facecolor'], 
                markeredgecolor=matplotlib.rcParams['axes.edgecolor'], markersize=3, lw=1)
            ax.annotate(node_title, fontsize=matplotlib.rcParams['font.size'], fontfamily=matplotlib.rcParams['font.family'],
                xy=(n['mat'], n['vis']), xycoords='data',
                xytext=(n['label_x'], n['label_y']), textcoords='offset pixels',
                horizontalalignment='left', verticalalignment='bottom')
        
    # Add the evolve nodes:
    for evolve_title, evolve in wm.evolves.items():
        if evolve_title in wm.nodes:
            n = wm.nodes[evolve_title]
            plt.plot(evolve['mat'], n['vis'], marker='o', color=matplotlib.rcParams['axes.facecolor'], markeredgecolor='red', markersize=3, lw=1)
            ax.annotate(evolve_title, fontsize=matplotlib.rcParams['font.size'], fontfamily=matplotlib.rcParams['font.family'],
                xy=(evolve['mat'], n['vis']), xycoords='data',
                xytext=(n['label_x'], n['label_y']), textcoords='offset pixels',
                horizontalalignment='left', verticalalignment='bottom')
        else:
            wm.warnings.append(f"Node '{evolve_title}' does not exist in the map.")
            
    # Add the pipeline nodes:
    for pipeline_title, pipeline in wm.pipelines.items():
        if pipeline_title in wm.nodes:
            n = wm.nodes[pipeline_title]
            plt.plot(n['mat'], n['vis'], marker='s', color=matplotlib.rcParams['axes.facecolor'], markersize=3, lw=.5)  
        else:
            wm.warnings.append(f"Node '{pipeline_title}' does not exist in the map.")
            
    # Plot Pipelines
    for pipeline_title, pipeline in wm.pipelines.items():
        if pipeline_title in wm.nodes:
            n_from = wm.nodes[pipeline_title]
            rectangle = patches.Rectangle((pipeline['start_mat'], n_from['vis']-0.01), pipeline['end_mat']-pipeline['start_mat'], 0.01, fill=False, lw=0.5)
            ax.add_patch(rectangle)
        else:
            wm.warnings.append(f"Could not find pipeline component called {pipeline_title}!")
               
    # Add the notes:
    for note in wm.notes:
        plt.text(note['mat'], note['vis'], note['text'], fontsize=matplotlib.rcParams['font.size'], fontfamily=matplotlib.rcParams['font.family'])

    plt.yticks([0.0,0.925], ['Invisible', 'Visible'], rotation=90, verticalalignment='bottom')
    plt.ylabel('Visibility', fontweight='bold')
    plt.xticks([0.0, 0.17,0.4, 0.70], ['Genesis', 'Custom-Built', 'Product\n(+rental)', 'Commodity\n(+utility)'], ha='left')
    plt.xlabel('Evolution', fontweight='bold')

    plt.tick_params(axis='x', direction='in', top=True, bottom=True, grid_linewidth=1)
    plt.grid(visible=True, axis='x', linestyle='--')
    plt.tick_params(axis='y', length=0)
    
