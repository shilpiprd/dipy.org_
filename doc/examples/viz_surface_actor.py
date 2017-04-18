"""
==================================
Visualization of 3D Surface Rendered ROI with Streamlines
==================================

Here is a simple tutorial following the probabilistic CSA Tracking Example in
which we generate a dataset of streamlines from a corpus callosum ROI, and
then display them with the seed ROI rendered in 3D with 50% transparency.

"""

from dipy.data import read_stanford_labels
from dipy.reconst.shm import CsaOdfModel
from dipy.data import default_sphere
from dipy.direction import peaks_from_model
from dipy.tracking.local import ThresholdTissueClassifier
from dipy.tracking import utils
from dipy.tracking.local import LocalTracking
from dipy.viz import fvtk
from dipy.viz.colormap import line_colors

"""
First, we need to generate some streamlines. For a more complete description of
these steps, please refer to the CSA Probabilistic Tracking Tutorial.
"""

hardi_img, gtab, labels_img = read_stanford_labels()
data = hardi_img.get_data()
labels = labels_img.get_data()
affine = hardi_img.get_affine()

white_matter = (labels == 1) | (labels == 2)

csa_model = CsaOdfModel(gtab, sh_order=6)
csa_peaks = peaks_from_model(csa_model, data, default_sphere,
                                 relative_peak_threshold=.8,
                                 min_separation_angle=45,
                                 mask=white_matter)

classifier = ThresholdTissueClassifier(csa_peaks.gfa, .25)

seed_mask = labels == 2
seeds = utils.seeds_from_mask(seed_mask, density=[1, 1, 1], affine=affine)

# Initialization of LocalTracking. The computation happens in the next step.
streamlines = LocalTracking(csa_peaks, classifier, seeds, affine,
                                step_size=2)

# Compute streamlines and store as a list.
streamlines = list(streamlines)

"""
We will create a streamline actor from the streamlines
"""

streamlines_actor = fvtk.line(streamlines, line_colors(streamlines))

"""
Next, we create a surface actor from the corpus callosum seed ROI. We
provide the ROI data, the affine, the color in [R,G,B], and the opacity as
a decimal between zero and one. Here, we set the color as blue/green with
50% opacity.
"""
surface_opacity = 0.5
surface_color = [0,1,1]

seedroi_actor = fvtk.actor.surface_actor(seed_mask, affine,
                                         surface_color, surface_opacity)

"""
Next, we initialize a ''Renderer'' object and add both of the actors
to the rendering.
"""

ren = fvtk.ren()
fvtk.add(ren, streamlines_actor)
fvtk.add(ren, seedroi_actor)

"""
If you uncomment the following line, the rendering will pop up in an interactive
window.
"""

#fvtk.show(ren)

ren.zoom(1.5)
ren.reset_clipping_range()

window.record(ren, out_path='surface_actor_tutorial.png', size=(1200, 900),
              reset_camera=False)

"""
.. figure:: surface_actor_tutorial.png
   :align: center

   **A top view of corpus callosum streamlines with the blue transparent
   seed ROI in the center**.
"""
