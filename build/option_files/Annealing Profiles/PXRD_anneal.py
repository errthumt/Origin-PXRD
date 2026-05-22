import warnings

# Axes3D is not included with Origin's native matplotlib, but it is not necessary for this package
warnings.filterwarnings(
    "ignore",
    message="Unable to import Axes3D",
    category=UserWarning,
    module="matplotlib.projections"
)
import matplotlib.pyplot as plt
import originpro as op #type: ignore
from itertools import zip_longest
import sys
from matplotlib.transforms import ScaledTranslation
from pathlib import Path

from cif2xrd.paramUtils import clean_parameters, parse_params, default_params #type:ignore

from cif2xrd.furnace import Profile, RAMP


def crop_axes_to_content(ax, l_marg=0, r_marg=0, t_marg=0, b_marg=0, pad=2):
    """
    Remove whitespace by shrinking axis limits to tightly wrap
    all lines, text, and annotations on the Axes.
    pad is in display (pixel) units.
    """
    fig = ax.figure
    fig.canvas.draw()  # ensure all artists have valid extents

    # Collect all bounding boxes in display coords
    bboxes = []

    # Lines, markers, etc.
    for line in ax.lines:
        bboxes.append(line.get_window_extent())

    # Text objects (labels, annotations, etc.)
    for txt in ax.texts:
        bboxes.append(txt.get_window_extent(renderer=fig.canvas.get_renderer()))

    # Collections (e.g., patches, arrows)
    for coll in ax.collections:
        try:
            bboxes.append(coll.get_window_extent(fig.canvas.get_renderer()))
        except Exception:
            pass

    # Merge into a single bounding box
    if not bboxes:
        return  # nothing to crop

    from matplotlib.transforms import Bbox
    full = Bbox.union(bboxes)

    # Add padding in display units
    full = full.expanded((full.width + 2*pad)/full.width,
                         (full.height + 2*pad)/full.height)

    # Convert display → data coordinates
    inv = ax.transData.inverted()
    x0, y0 = inv.transform((full.x0, full.y0))
    x1, y1 = inv.transform((full.x1, full.y1))

    # Apply new limits
    ax.set_xlim(x0-l_marg, x1+r_marg)
    ax.set_ylim(y0-b_marg, y1+t_marg)

from cif2xrd.furnace import Profile

class OriginProfile(Profile):
    def __init__(self, **kwargs):
        if "add_temps" in kwargs:
            try:
                kwargs["add_temps"] = [int(float(x)) for x in str(kwargs["add_temps"]).split(";") if str(kwargs["add_temps"]).strip() != ""]
            except Exception as e:
                popup = f"Your 'Add Temps' values could not be read correctly: '{kwargs['add_temps']}'. Exception:\n{e}"
                op.set_lt_str("popupmsg$", popup)
                op.lt_exec(fr'type -b popupmsg$;') 
                kwargs["add_temps"] = []

        super().__init__(**kwargs)


    def plot_to_origin(self):
        fig = self.plot()

        save_file = op.get_lt_str('fname$')

        save_path = Path(save_file)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        plt.savefig(save_file, bbox_inches='tight', pad_inches=0)


def make_anneal_template():
    wbook = op.load_book('PXRD_anneal_template.ogwu')
    wks = wbook[0]
    op.lt_exec("wks.labels(-O)")

default_params["anneal"] = {
    "start_temp":      25,   # int
    "min_height":      6.0,   # float
    "add_temps":       "",   # comma‑separated string of numbers, e.g. "500,600,700"
    "ramp_width":      4.0,   # float
    "dwell_width":     6.0,   # float
    "font_size":       30.0,   # float
    "font_family":     "Arial",   # int (0=Arial, 1=Times New Roman, etc.)
    "text_offset":     0.6,   # float
    "line_width":      3.0,   # float
    "l_marg":          1.0,   # float
    "r_marg":          1.0,   # float
    "t_marg":          1.0,   # float
    "b_marg":          1.0    # float
}


def make_anneal_plot(cleaned_params=default_params["anneal"]):
    wb = op.find_book()
    wks = wb[0]

    try:
        types = wks.to_list('Type')
        temps = wks.to_list('Temperature')
        notes = wks.to_list('Time/Comment')

        #keys = wks.to_list('Variable')
        #values = wks.to_list('Value')
    except:
        op.lt_exec('type -b "At least one required column not found. It is recommended to use the provided template worksheet.')
        return



    commands = list(zip_longest(types,temps,notes))
    myProf = OriginProfile(**cleaned_params)
    for type, temp, note in commands:
        method = getattr(myProf,type,None)
        if method is not None:
            if type.lower() == RAMP:
                method(temp,note)
            else:
                method(note)
    
    myProf.plot()
    wks = wb[1]
    wks.activate()
    comment = f'Image Saved to:\n{op.get_lt_str("fname$")}'
    lt_cmd = f'''
        insertimg resize:=1 orng:=col(1)[1];
        col(1)[C]$ = "{comment}";
    '''
    op.lt_exec(lt_cmd)

if __name__ == "__main__":
    # sys.argv[0] = script name
    # sys.argv[1] = first argument from LabTalk
    template_mode = sys.argv[1]=="template" if len(sys.argv)>1 else False

    if template_mode:
        make_anneal_template()
    else:
        param_string = sys.argv[2] if len(sys.argv)>2 else ""
        params = parse_params(param_string)
        cleaned_params = clean_parameters(params, defaults=default_params["anneal"])
        make_anneal_plot(cleaned_params)
