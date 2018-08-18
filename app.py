import os, pickle
from flask import Flask, request, redirect, url_for, render_template
from werkzeug import secure_filename
import time
from threading import Thread

from bokeh.embed import autoload_server
from bokeh.models import GlyphRenderer
from bokeh.plotting import cursession, figure, output_server, push, VBox

#wykresy
from plot_stops1 import plot_bokeh
import plot_hexagonal_grid, plot_segments

UPLOAD_FOLDER = "/home/bartek/stops_web/bias_tmp"
ALLOWED_EXTENSIONS = set(['pckl'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    from os import listdir
    from os.path import isfile, join
    onlyfiles = [ f for f in listdir(app.config['UPLOAD_FOLDER']) if (isfile(join(app.config['UPLOAD_FOLDER'],f)) and f.split(".")[-1] in ALLOWED_EXTENSIONS )]
    html = render_template(
        'main.html',
        uploaded_files = onlyfiles
    )
    return html

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    #plik pickle
    try:
        plots_data = pickle.load(open(os.path.join(app.config['UPLOAD_FOLDER'], filename), "rb"))
    except:
        return render_template('error.html')

    stops1_tag = None
    stops2_tag = None
    stops3_tag = None

    #wykres stops1
    if 'stops1' in plots_data:
        stops1_plot, stops1_session = plot_bokeh(plots_data['stops1'],normalized_types=False,uniq_id=filename)
        stops1_tag = autoload_server(stops1_plot, stops1_session).replace("localhost","biquad.mimuw.edu.pl")

    #wykres stops2
    if 'stops2' in plots_data:

        start_pop = plots_data['stops2'][1][0]
        grid_shape = plots_data['stops2'][0]
        all_pop_mat = plots_data['stops2'][1][1:]
        color_dict = plots_data['stops2'][2]

        stops2_anim_plot, stops2_anim_session = plot_hexagonal_grid.draw_bokeh_plot(start_pop,grid_shape,color_dict,uniq_id=filename)
        stops2_tag = autoload_server(stops2_anim_plot, stops2_anim_session).replace("localhost","biquad.mimuw.edu.pl")
        thread = Thread(target=update_animation_stops2, args=(stops2_anim_plot, stops2_anim_session,all_pop_mat,color_dict))
        thread.start()

    if 'stops3' in plots_data:

        all_freqs_after_reception = plots_data['stops3'][0]
        all_segm_dict = plots_data['stops3'][1]

        stops3_anim_bar, stops3_anim_plot, stops3_anim_session, geny = plot_segments.draw_plot(all_freqs_after_reception,all_segm_dict,uniq_id=filename)
        stops3_tag = autoload_server(VBox(stops3_anim_bar,stops3_anim_plot), stops3_anim_session).replace("localhost","biquad.mimuw.edu.pl")
        thread = Thread(target=update_animation_stops3, args=(stops3_anim_bar,stops3_anim_plot, stops3_anim_session,all_freqs_after_reception,all_segm_dict, geny))
        thread.start()

    return render_template('plot.html', tag1=stops1_tag, tag2=stops2_tag, tag3=stops3_tag, filename=filename)

def update_animation_stops2(plot, session, all_pop_mat, color_dict):

    renderer = plot.select(dict(type=GlyphRenderer))
    ds = renderer[0].data_source

    #aktualizacja dla kazdego kroku symulacji
    for pop_mat in all_pop_mat:
        colors, wektor = plot_hexagonal_grid.value_color(pop_mat,color_dict)
        ds.data['wektor'] = wektor
        ds.data['colors'] = colors

        session.store_objects(ds)
        time.sleep(.10)

def update_animation_stops3(bar, plot, session, all_freqs,all_segm_dict, geny):
    genes=["Bcd","Cad","Gt","Hb","Kr","Kni","Nos"]
    renderer1 = bar.select(dict(type=GlyphRenderer))
    renderer2 = plot.select(dict(type=GlyphRenderer))
    ds = renderer1[0].data_source
    for i, values in enumerate(all_freqs[1:]):
        segm_1_sum = 0
        segm_2_sum = 0
        segm_3_sum = 0
        segm_4_sum = 0
        for gen in geny:
            if gen in values:
                segm_1 = values[gen][0]
                segm_2 = values[gen][1]
                segm_3 = values[gen][2]
                segm_4 = values[gen][3]
                index = geny.index(gen)
                ds.data['top'][index*4:index*4+4] = [segm_1_sum + segm_1, segm_2_sum + segm_2, segm_3_sum + segm_3, segm_4_sum + segm_4]
                ds.data['bottom'][index*4:index*4+4]=[segm_1_sum, segm_2_sum, segm_3_sum, segm_4_sum]
                segm_1_sum += segm_1
                segm_2_sum += segm_2
                segm_3_sum += segm_3
                segm_4_sum += segm_4
            else:
                index = geny.index(gen)
                ds.data['top'][index:index+4] = [0,0,0,0]
                ds.data['bottom'][index:index+4]=[0,0,0,0]
        rend = []
        for m,gen in enumerate(genes):
            for n in range(len(renderer2)):
                if 'name' in renderer2[n].data_source.data:
                    if renderer2[n].data_source.data['name'] == gen:
                        rend.append(renderer2[n].data_source)
                        actual_ys = all_segm_dict[i+1][m]
                        renderer2[n].data_source.data['ys'] = [actual_ys[0:2],actual_ys[2:4],actual_ys[4:6],actual_ys[6:8]]

        session.store_objects(ds, *rend)
        time.sleep(0.30)


if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0")
