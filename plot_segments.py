from bokeh.plotting import figure, output_server, cursession, VBox, push
import random
from bokeh.models import HoverTool, ColumnDataSource, Range1d, GlyphRenderer

def plot_segments(freqs_after_reception, col_dict):
    values = freqs_after_reception

    y_range = Range1d(start=0, end=99)
    x_range = Range1d(start=0.5, end=4.5)
    title = "Population structure"
    p = figure(width=600, height=400,y_range=y_range, x_range = x_range,title=title)

    geny = []
    wektory = []
    top = []
    bottom = []
    left = []
    right = []
    color = []
    segm_1_sum = 0
    segm_2_sum = 0
    segm_3_sum = 0
    segm_4_sum = 0
    for gen in values:
        segm_1 = values[gen][0]
        segm_2 = values[gen][1]
        segm_3 = values[gen][2]
        segm_4 = values[gen][3]
        top.extend([segm_1_sum + segm_1, segm_2_sum + segm_2, segm_3_sum + segm_3, segm_4_sum + segm_4])
        bottom.extend([segm_1_sum, segm_2_sum, segm_3_sum, segm_4_sum])
        left.extend([0.6, 1.6, 2.6, 3.6])
        right.extend([1.4, 2.4, 3.4, 4.4])
        color.extend([col_dict[gen]]*4)
        segm_1_sum += segm_1
        segm_2_sum += segm_2
        segm_3_sum += segm_3
        segm_4_sum += segm_4
        wektory.extend([gen]*4)
        geny.append(gen)

    source = ColumnDataSource(
        data=dict(
            top = top,
            bottom = bottom,
            left = left,
            right = right,
            wektor = wektory,
            colors=color
        )
    )

    p.quad(top = "top", bottom = "bottom", left="left", right="right", source=source, color = "colors",fill_alpha=0.8)
    hover = HoverTool(plot=p, tooltips=dict(wektor="@wektor"))
    p.tools.append(hover)

    return p, geny

def plot_environment(segm_dict):
    #segm_dict tablica postaci {gen: [occ] ...} dla pierwszego kroku symulacji

    colors = ["blue","green","red","cyan","#8B008B","#00FF7F","teal"]

    TOOLS = "resize,save,pan,box_zoom,wheel_zoom"

    title = "Environment"
    p = figure(title=title, plot_width=600, plot_height=400, x_range=[0, 4], y_range=[0, 4000],tools=TOOLS)
    p.ygrid.grid_line_color = "white"
    p.xgrid.grid_line_color = "white"

    genes=["Bcd","Cad","Gt","Hb","Kr","Kni","Nos"]
    for i in range(7):
        source = ColumnDataSource(
            data=dict(
                xs = [[0,1],[1,2],[2,3],[3,4]],
                ys = [segm_dict[i][0:2],segm_dict[i][2:4],segm_dict[i][4:6],segm_dict[i][6:8]],
                name = genes[i]
            )
        )
        p.multi_line(xs = "xs", ys = "ys",source=source, line_color = colors[i], line_width=3, legend=genes[i])

    p.line(x=[1,1],y=[0,4000],line_color="black",line_width=4,line_alpha=0.8)
    p.line(x=[2,2],y=[0,4000],line_color="black",line_width=4,line_alpha=0.8)
    p.line(x=[3,3],y=[0,4000],line_color="black",line_width=4,line_alpha=0.8)
    return p


def draw_plot(all_freqs, all_segm_dict,uniq_id="no-id"):
    #zbior nazw wszystkich komorek podczas symulacji
    cells_types = set()

    for i in range(len(all_freqs)):
        for e in all_freqs[i].keys():
            cells_types.add(e)

    #dla kazdego typu komorek przypisywany jest inny kolor
    col_dict = {}
    from bokeh.palettes import brewer
    colors_palette = brewer["Spectral"][11]
    color = lambda: random.randint(0,255)
    for i,element in enumerate(cells_types):
        if i < 11:
            col_dict[element] = colors_palette[i]
        else:
            #losowy kolor
            col_dict[element] = ('#%02X%02X%02X' % (color(),color(),color()))

    #dodanie klucza od wartosci ktorych nie ma po pierwszej iteracji
    for element in cells_types:
        for i in range(len(all_freqs)):
            if element not in all_freqs[i]:
                all_freqs[i][element] = [0,0,0,0]

    output_server("stops3"+uniq_id)

    bar, geny = plot_segments(all_freqs[0], col_dict)
    plot = plot_environment(all_segm_dict[0])

    push()

    return bar, plot, cursession(), geny
