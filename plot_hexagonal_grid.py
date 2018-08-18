import numpy, math, random
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.plotting import figure, output_server, cursession, push

def hexagon_points(center_x, center_y, alpha, beta):
    points_x = numpy.array([-beta,-beta,0,beta,beta,0])+center_x
    points_y = numpy.array([-alpha,alpha,2*alpha,alpha,-alpha,-2*alpha])+center_y
    return list(points_x), list(points_y)

def value_color(pop_mat,color_dict):
    #kolory i wektory aktywnosci dla aktualnego stanu pop_mat
    color_gen = lambda: random.randint(0,255)
    rcolors = []
    vector = []

    for i in range(len(pop_mat)):
        key = ' '.join(str(pop_mat[i].astype(int)))
        if key in color_dict:
            color = '#FF%02X%02X' % (color_dict[key][0]*255,color_dict[key][1]*255)
        else:
            color = '#FF%02X%02X' % (color_gen(),color_gen())
            color_dict[key] = color
        rcolors.append(color)
        vector.append(''.join(key[1:-1].split(" ")))

    return rcolors, vector

def draw_bokeh_plot(pop_mat, grid_shape, color_dict, width=800,uniq_id="no-id"):
    #wykres na siatce heksagonalnej
    output_server("stops2"+uniq_id)
    p = figure(plot_width=width, title="STOPS")

    p.ygrid.grid_line_color = "white"
    p.xgrid.grid_line_color = "white"

    m,n = grid_shape
    beta = 0.5
    alpha = beta/math.sqrt(3)
    h = beta/math.sqrt(3)

    points_x = []
    points_y = []
    y = 0
    for i in range(n):
        if i % 2 == 1:
            x = -0.5
        else:
            x = -1
        for j in range(m):
            if i % 2 == 1:
                x += 1
            else:
                x += 1
            points = hexagon_points(x,y, alpha, beta)
            points_x.append(points[0])
            points_y.append(points[1])
        y += 3*h

    colors, wektor = value_color(pop_mat,color_dict)

    source = ColumnDataSource(
        data=dict(
            points_x = points_x,
            points_y = points_y,
            wektor = wektor,
            colors=colors
        )
    )

    p.patches(xs="points_x", ys="points_y", source=source, line_color="blue", color="colors", line_width=2, fill_alpha=0.8)
    hover = HoverTool(plot=p, tooltips=dict(wektor="@wektor"))
    p.tools.append(hover)

    push()

    return p, cursession()
