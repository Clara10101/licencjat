import random

def plot_bokeh(symulacja, normalized_types = False, types_to_plot = None, type_labels = None, ligand_labels = None,uniq_id="no-id"):
    from bokeh.plotting import figure, VBox, output_server, cursession, push, Session
    from bokeh.models import Range1d
    from bokeh.document import Document

    pops = symulacja[0]
    ligands = symulacja[1]
    types = symulacja[2]

    if types_to_plot == None:
        types_to_plot = types.keys()

    if type_labels == None:
        type_labels = dict([])
        for k in types.keys():
           type_labels[k] = k

    if ligand_labels == None:
        ligand_labels = dict([])
        for k in ligands.keys():
            ligand_labels[k] = k

    output_server("stops1"+uniq_id)

    len_pops = len(pops)
    step_axis = range(len_pops)

    TOOLS="resize,pan,wheel_zoom,box_zoom,reset,previewsave,poly_select"

    xrange1 = Range1d(start=0, end=len_pops-1)

    if normalized_types:
        #dwa wykresy - rozmiar populacji i procent komorek
        fig1 = figure(title="Population size",width=800, height=332,tools=TOOLS,x_range=xrange1)
        fig1.line(step_axis,pops,line_color = "blue",line_width=2,line_alpha=0.9)

        fig2 = figure(title="% of cells of specific types in the population",width=724,height=300,tools=TOOLS,x_range=xrange1)

        for k, v in types.items():
            if k in types_to_plot:
                norm_sizes = [(float(v[i]) / pops[i] * 100) for i in range(len(pops))]
                color = lambda: random.randint(0,255)
                rcolor = ('#%02X%02X%02X' % (color(),color(),color()))
                fig2.line(step_axis, norm_sizes, line_width=2, line_color = rcolor, legend=type_labels[k])

        fig2.legend.orientation = "top_right"
    else:
        fig1 = figure(title="Population / type size",width=724,height=300,tools=TOOLS,x_range=xrange1)

        for k, v in types.items():
            if k in types_to_plot:
                color = lambda: random.randint(0,255)
                rcolor = ('#%02X%02X%02X' % (color(),color(),color()))
                fig1.line(step_axis, v, line_width = 2, line_color=rcolor, legend = type_labels[k])

        fig1.legend.orientation = "top_right"

        fig1.line(step_axis, pops, line_width = 2.0, line_color = "blue", legend = "population size")

    fig3 = figure(title="Ligands",width=724,height=300,tools=TOOLS,x_range=xrange1)

    for k, v in ligands.items():
        color = lambda: random.randint(0,255)
        rcolor = ('#%02X%02X%02X' % (color(),color(),color()))
        fig3.line(step_axis, v, line_width = 3, line_color = rcolor, legend = ligand_labels[k])

    fig3.legend.orientation = "top_right"

    push()

    if normalized_types:
        p = VBox(fig1,fig2,fig3)
    else:
        p = VBox(fig1,fig3)

    session=cursession()
    return p,session
