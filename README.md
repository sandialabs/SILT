# Sandia Image Labeling Tool

Python UI tool for viewing, labeling, and annotating imagery for data analytics 
machine learning projects.  SILT has a simple, semi-customizable interface and 
outputs files that are human-readable and ingestible by database applications.

Bear with us - this tool is a constant work in progress.


![Screencap of SILT](/preview/silt_aerial_sample_2.png "SILT Screencap")*Screencap of SILT for image annotation.  Image source: [Harris Geospatial](https://www.harrisgeospatial.com/Data-Imagery/Aerial-Imagery).*

<!-- blank line -->
<br>
<!-- blank line -->

*Sample SILT JSON file output* | *Sample SILT segmentation mask output*
:-----------------------------:|:-------------------------------------:
![Sample SILT output file](/preview/HG_Aerial_ThumbPic1_siltlabels_screencap_small.png "SILT output file") | ![Sample SILT segmentation mask output](/preview/silt_aerial_sample_mask_small.png "Segmentation Mask Output")

<br>

**So who should use SILT? SILT was designed for:**
- **Handling dimensionally humungous images** - we're talking >30,000 pixels per side.  Turns out there is (or at least used to be) a hard limit set in Qt on the number of pixels allowed per axis of an image; normally this limit is set to avoid issues due to integer overflow.  But Qt also happens to be the backbone to many a UI, meaning that those UIs cannot handle large images!  SILT bypasses backend overflow problems by tiling large images.
- **Deeper investigation of higher bit-depth data.**  Typical labeling programs will compress imagery to 8-bit for display, but what if you have high dynamic range, 32-bit data and the objects you want to label are _very_ dim?  Will your objects of interest still be visible in 8 bits?  I know what you're thinking.  Yes, most displays are 8-bit, so yes, SILT does compress down for display, but it also keeps the original, higher bit-depth data around for processing.  Then when you adjust things like clipping and contrast, those adjustments are applied directly to the higher bit-depth data and the display is updated, allowing you to utilize the entire avilable dynamic range and see fine details that might otherwise be lost.

However, SILT is considered a work in progress, put together by only a few Sandians who ran into the above problems.  It's far from perfect.  Though I hope it helps others, SILT may not be for you, and that's ok! Here are some 3rd-party tools for image 
curation tasks:
- [labelme](https://github.com/wkentaro/labelme) (open source)
- [superannotate](https://www.superannotate.com/) (web-based or desktop app)
- [labelbox](https://labelbox.com/) (web-based, government experience)

---

<!-- blank line -->
<br>
<!-- blank line -->

## POC

If you or your team used SILT, or if you have comments or feedback, please drop
me a note!  
Email: kmlarso@sandia.gov

<!-- blank line -->
<br>
<!-- blank line -->

# Package Installation

To access the most recent release, see "Releases" on the sidebar. Download the appropriate installer for your operating system.

## Windows Instructions through File Explorer:

- Extract the folder:  
  - Navigate to the `silt-pkg.tar.gz` file. Right Click it and select `Extract All` and choose where to unzip too (default is fine)
- Run the installer:
  - Enter the folder and execute (double click) the installation file. It should should look something like this:  
  (e.g) `silt-2.2.0-Windows-x86_64.exe` (starts with "silt" and ends in ".exe")
- Follow the prompts (defaults are fine) and take note of the installation path you chose. Wait for the installation to complete
- Once done, open the installation folder in the File Explorer.
  - The default installation directory is usually something like `C:\Users\<user>\AppData\Local\silt`
- Find and run the silt program: Execute (double click) the `launch_silt.bat` file in the folder

### Notes to keep in mind
- Please do not move `launch_silt.bat` or `run_tests.bat` to a different location (moving the entire folder as a whole is okay).

- (optionally) You may run the tests any time to make sure the program works properly. If you encounter errors, please try runing these tests: Execute `run_tests.bat` in the installation folder (done automatically on installation).


## Unix (Linux) instructions through Command Line:
Note: this assumes conda is already installed on your system before hand

- Untar the zip and run the installer (this command runs `make untar` under the hood):  
  `make install`


- Activate the new conda environment that was just installed
  Example using default config:
  - `conda activate silt`
<!-- - Windows: `conda activate ~\AppData\Local\silt` -->
  - Debugging:
    - Note: If that didn't work, run the following command and locate the path of the installed conda environment (It should have "silt" at the end of the path):  
    `conda env list`
    - Activate the conda environment you just found:
    - `conda activate <env_path_from_above>`

- Run the program to open the GUI: Simply run the new command `silt`


# Repository Installation
## Prerequisites

- python >= 3.6 and < 3.9
- numpy >= 1.15
- pyqt5
- h5py >= 2.8
- shapely >= 1.6.4
- pytest >= 8.2.0
- pytest-qt
- pytest-xvfb
- pytest-cov
- pytest-mock
- scipy

*Note: the SILT package is set up to be installed with pip, therefore pip is 
also a requirement; however, pip is included within Python installations for 
Python versions >= 3.4.*

*Note: the versions of the prerequisites listed here are based on what I've 
personally tested.  SILT may still function with other versions... but I haven't
tested it.*

My recommendation is to use Anaconda environments.  See [https://docs.anaconda.com/anaconda/install/](https://docs.anaconda.com/anaconda/install/).

I've had reports of issues installing PyQt5 outside of Anaconda environments.  If you choose not to use Anaconda, then 
for Ubuntu, try:
```bash
sudo apt-get install python3-pyqt5
```

or for RHEL:
```bash
yum install PyQt5
```

on Windows with Python >= 3.6, I *think* you should be able to:
```python
pip install pyqt5
```

## Installation

0. Install prerequisites

If you're using Anaconda environments for Python, that's just:
```bash
conda install pyqt numpy h5py shapely pytest pytest-qt pytest-xvfb pytest-cov pytest-mock scipy
```
Otherwise use the installer of your choice.

1. Clone the repo

```bash
git clone git@github.com:sandialabs/SILT.git SILT
```

2. Change to top-level directory

```bash
cd SILT
```

The directory structure should look like:

```bash
SILT
├── preview/
├── README.md
├── sample_images/
├── sample_templates/
├── scripts/
├── silt/
...
```

3. Install silt

This package is set up to be installed via pip:

``` bash
pip install ./silt
```

4. To run SILT, simply call 'silt' from the command line

``` bash
silt
```

---

## Recent Updates

#### 2.2.0
- Images can be loaded as an image pyramid, saving memory.

#### 2.1.0
- Polygon lines no longer scale with the scene when zooming.
- Required packages are automatically downloaded via pip/pypi if available.

#### 2.0.0
- New option to load and display overlays.
- New automatic translation of pixel coordinates to geo-coordinates.  Must 
  include a 3x3 transform matrix in the HDF5 input file and specify HDF5
  path in the template using the *image_info: geo_transform:* key.
- Default labels extension changed to be ".json."  To set the default back
  to ".siltlabels.json", set the *outputs_options: default_labels_extension:*
  key in the template file to ".siltlabels.json".
- **Warning**: default output keys have been changed from "overlay_item_*" to 
  "label_item_*".  SILT v2 will read labels files with old-style keys, but will 
  attempt to update those keys to match the new style.  This may interfere with 
  any applications that ingest labels files.


---

## Quick Start

1. Run silt by calling 'silt' from the command line.
2. Open a template (**File > Open template**)  
    You can use one of the sample templates included in the "sample_templates" 
    directory. Template files tell SILT how to read your images and how to 
    collect inputs from a user.
    
3. Open an image (**File > Open image**)  
    If you're using a sample template, choose the sample image that corresponds 
    to it. Sample images are in the "sample_images" directory and they already
    have some labels.

    When you open an image, you will be prompted on whether or not you would like
    to load the image as a pyramid. The pyramid will only be generated once, and is simply
    a collection of the image at different resolutions. When using the pyramid, the different
    resolutions will be loaded in at corresponding zoom levels.
    
4. Start adding polygons.
   You can use the **Edit > add > polygon** menu or the 'add_polygon' button 
   on the toolbar.  
    A. To delete a polygon, select the polygon and press the 'delete' key (or 'Fn + delete' on Mac).  
    B. To add a vertex to a polygon, first make sure that polygon is 
    selected, then hold the 'shift' key and click the left mouse button near
    a polygon line.  The vertex should appear.  
    C. To delete a vertex from a polygon, first make sure the polygon is
    selected, then hold the 'ctrl' key and click the left mouse button over
    the vertex (or 'cmd' key and left click on Mac).
    
5. Save your progress (**File > Save** OR **File > Save as**)  
    If **File > Save as** was never used, then
    **File > Save** will automatically save a [imagename].siltlabels.json file
    to the same folder that contains the image.
    If **File > Save as** was used, then **File > Save** will continue to save to 
    the specified location.
    I recommend using **File > Save** as this will allow SILT to automatically
    open the siltlabels.json file the next time you open the image.  If you use
    **File > Save as** then you will need to manually open the siltlabels.json
    file using **File > Open Saved Labels** the next time you open the image.

6. Save an image mask (**File > Save mask**)  
    This will automatically save a [imagename].siltmask.csv file to the
    same folder that contains the image.

---

## Usage Guide

### Image files

An image file contains the data (and metadata) to display in the SILT UI.

Due to a combination of legacy requirements and formatting issues, the only 
currently-supported file format is HDF5 (I won't complain if someone else 
wants to integrate support for other formats :D but for now it's easy enough 
to stuff images into HDF5). Check the "scripts" directory for the 
convert_to_h5.py script, which provides an example of converting a PIL-readable 
image to grayscale and writing to HDF5.

Images must be either single-channel (i.e. grayscale) or 
3-channel RGB and contained in a properly-shaped numpy array. 
The H5 dataset containing the image data can be put anywhere in the H5 file 
structure - so long as it is specified in the *image_info* dictionary in 
the template file (discussed in the next section)! The image dataset in the 
HDF5 file should also contain an attribute for *color_mode*, which is a string 
("RGB" for rgb images and "L" for greyscale - these are consistent with the 
PIL.Image.Image.mode modes). SILT will guess what type of image you're loading 
if this attribute isn't included.

### Template files

The template is a json-formatted file with style information in it.
It controls which inputs to collect from the user for each labeled item,
it lets the program know where the image data is within the image files,
and it controls some overlay styles (e.g. the line width and color of a 
polygon).  It uses the extension ".silttemplate.json."

You are required to open a template before you can open any images or series.
The required and optional entries of the template file are described below,
but it is best to start with one of the sample templates in the 
sample_templates directory and modify it to fit your data and requirements.

At the top level, the template file contains a dictionary with the following
keys:
```json
{
    "image_info": {
        ...
    },
    "template_info": [
        ...
    ],
    "outputs_options": {
        ...
    },
    "label_item_options": {
        ...
    }
}
```

*image_info* contains a dictionary. It describes the structure of the HDF5
image file.  It is mandatory.

*template_info* contains a list of dictionaries. It defines the input
fields which users will interact with during labeling.  It is mandatory.

*outputs_options* contains a dictionary. It holds options for the various
output files which SILT creates when a user Saves labels.  It is mandatory.

*label_item_options* contains a dictionary.  It holds style options for the
label items, such as linewidth and color.  It is optional.

#### image_info

The *image_info* dictionary currently has two entries: "data_path" (required)
and "geo_transform" (optional).  "data_path" is the path to where the image
data is located within the HDF5 image file.  "geo_transform" is the path to
where the geo-transform matrix is located within the HDF5 image file.
The geo-transform matrix is a 3x3 transformation matrix that converts pixel
coordinates to geo coordinates in decimal degrees.  It is optional, but if
included then SILT will output geo-coordinates as well as pixel coordinates
in the outputted labels files.
```json
    "image_info": {
        "data_path": "path/to/image_data",
        "geo_transform": "path/to/geotransform_matrix"
    }
```

#### template_info

The *template_info* list of dictionaries define the types of the
input fields that appear in the left side panel of SILT.  Each dictionary in
the list describes one input field.  There are currently three types of 
supported input fields: a combobox (drop-down menu), a checklist 
(a drop-down with checkboxes), and a lineedit (a text input field).

```json
    "template_info": [
        {
            "type": "combobox",
            "label": "Class",
            "options": [
                "Building",
                "Park",
                "Road"
            ],
            "tooltip": "The major category."
        },
        {
            "type": "checklist",
            "label": "Subclass",
            "options": [
                "Residential",
                "Commercial",
                "Public",
                "Private"
            ],
            "tooltip": "Select all that apply."
        },
        {
            "type": "lineedit",
            "label": "Notes",
            "tooltip": "Any extra noteworthy details about this object."
        }
    ]
```

The example above demonstrates the template file definitions of the three types
of input fields.  Shown below is the associated left side panel of SILT.

![Screencap of sidepanel](/preview/silt_sidepanel_sample_1.PNG "SILT Sidepanel Screencap")*Screencap of sidepanel using the above "template_info" options.*

Every dictionary in the template_info list contains the keys "type" and "label".
The "type" defines the type of input field and the "label" defines the title 
shown above that input field in the side panel.  The "type" value is a string
and must be one of "combobox," "checklist," or "lineedit."  The "label" value
is a custom string, but it is a good idea to keep it short (one or two words).

The "combobox" and "checklist" types require another key-value pair in the 
template_info list: the "options" list.  The "options" is a list of strings 
which populate the drop-down menu in either case.

Note that the key "tooltip" is also included in each dictionary.  The "tooltip"
is a string which appears when the user hovers their mouse over the 
respective input field in the side panel.  This is a good place to include hints
about what a user should input.  It is completely optional.

*Combobox field* | *Checklist field* | *Lineedit field*
:-----------------------------:|:-------------------------------------:|:-------------------------------------:
![template combobox](/preview/silt_template_info_sample_class.PNG "SILT template combobox") | ![template checklist](/preview/silt_template_info_sample_subclass.PNG "SILT template checklist") | ![template lineedit](/preview/silt_template_info_sample_notes.PNG "SILT template lineedit")
![SILT combobox](/preview/silt_sidepanel_sample_class.PNG "SILT combobox") | ![SILT checklist](/preview/silt_sidepanel_sample_subclass.png "SILT checklist") | ![SILT lineedit](/preview/silt_sidepanel_sample_notes.png "SILT lineedit")

#### outputs_options

The *outputs_options* dictionary controls some key-naming conventions in the
siltlabels files as well as the output of some extra information fields for the
label items.

```json
    "outputs_options": {
        "mask_label": "Class",
        "include_mask": "false",
        "include_bounding_rect": "false",
        "default_labels_extension": ".siltlabels.json",
        "default_output_keys": {
            "label_item_vertices": "polygon",
            "label_item_uuid": "featureID",
            "image_filename": "imageID",
            "geo_transform": "geoTransform",
            "geo_vertices": "polygonGeo"
        }
    }
```

The "mask_label" should be filled in with the "label" of the input field you'd
like to use to assign values to the segmentation mask if you decide to save one.
The "mask_label" value is a string and must match one of the labels in the 
*template_info* list of dictionaries.  The label that you choose for 
"mask_label" must correspond to a combobox input field. In this example, the 
"mask_label" is "Class," which refers to the category of object we labeled and
is also a combobox input field.  When we save a segmentation mask using this
option, each labeled object in the segmentation mask will have pixel values 
based on whether that object is a "Building," "Park," or "Road."

The "include_mask" option controls whether the siltlabels file contains a list
of mask pixels for each overlay item.  Mask pixels are the pixels that the 
labeled object covers in the image.  This is separate from the segmentation mask 
file.  The "include_mask" value is a string and must be either "true" or
"false."  If "include_mask" is not in the *outputs_options* dictionary, SILT 
assumes it to be "false."

The "include_bounding_rect" option controls whether the siltlabels file contains
a list of vertices to describe the bounding rectangle for each overlay item.
If the overlay item is a polygon, the bounding rectangle is simply the smallest 
upright bounding box which contains all of the polygon vertices (its sides are
parallel to the x and y axes; it is not rotated).  The "include_bounding_rect" 
value is a string and must be either "true" or "false."  If
"include_bounding_rect" is not in the *outputs_options* dictionary, SILT assumes
it to be "false."

The "default_labels_extension" option controls the default extension SILT uses 
when saving the siltlabels files.  A typical extension starts with a "." but 
this is generally not required.  If "default_labels_extension" is not in the
*outputs_options* dictionary, SILT uses the default extension of ".json".

The "default_output_keys" option controls the keywords for five default 
siltlabels outputs: "label_item_vertices," "label_item_uuid," "image_filename," 
"geo_transform", and "geo_vertices."  If you need to ingest the siltlabels files 
into a database with a particular schema - for example, you need the keyword
"polygon" instead of "label_item_vertices" - you can tell SILT to save the
keywords particular to your schema instead of the defaults.  These five default
siltlabels keys ("label_item_vertices," "label_item_uuid," "image_filename," 
"geo_transform", and "geo_vertices") are the only keys available to be
overwritten at this time.

#### label_item_options

The *label_item_options* entry is optional and controls the style of the
label items overlayed on the image (polygons, etc.).  It is a dictionary
structured as follows:

```json
    "label_item_options": {
        "line_width": 5.0,
        "line_color": [
            0,
            255,
            255,
            150
        ],
        "vertex_diameter": 7.0,
        "vertex_color": [
            0,
            0,
            255,
            255
        ]
    }
```

There are various options to control the style of the label items:
- "line_width" is a float or integer specifying label item line
width in pixels.
- "line_color" is a list of 4 integers between 0 and 255 specifying rgba 
(red, green, blue, alpha) values for the label item line color.
- "vertex_diameter" is a float or integer specifying the size (diameter) of the
label item vertices in pixels.
- "vertex_color" is a list of 4 integers between 0 and 255 specifying rgba 
(red, green, blue, alpha) values for the label item vertex color.

*Default label item style* | *Above sample label item style*
:-----------------------------:|:-------------------------------------:
![Default item style](/preview/silt_overlay_item_default_style.PNG "Default item style") | ![Template item style](/preview/silt_overlay_item_template_style.PNG "Custom item style")

### Overlay files [NEW]

Overlay files are json-formatted files that contain line segments 
and/or polygons and style information to be displayed over the top of an 
image in SILT.  An overlay segment or polygon is displayed over the image
and under any label polygons and the user cannot interact with them. 
Example use cases for overlays include displaying ground truth or prior 
knowledge over an image to help a user annotate.

Overlay files must have the ".json" extension.  They contain a list of
dictionaries, one dictionary per overlay line segment or polygon.  Each 
dictionary contains keys for the segment or polygon vertices, the line
color, the line style, and the line width:
```json
[
    {
        "vertices": [
            [262, 93], [247, 122], [211, 106]
        ],
        "color": [255, 255, 0, 170],
        "style": "dotted",
        "line_width": 5
    },
    {
        "vertices": [
            [176.64, 64.64], [169.6, 80.0], [157.44, 73.6], [176.64, 64.64]
        ],
        "color": [255, 0, 255, 170],
        "style": "dashed",
        "line_width": 3
    }
]
```
The above overlay file sample contains two overlay items.  Each overlay item is 
defined by four fields: "vertices," "color," "style," and "line_width."

"vertices" contains a list of points in pixel coordinates.  If the last 
vertex in the list equals the first (i.e. it is a closed polygon), then 
SILT will display the item as a polygon.  The second overlay item in the 
above example is a polygon.  If the last vertex in the list does not 
equal the first, then SILT will display the item as a line segment.  The 
first overlay item in the above example is a line segment.

"color" contains a list of four integers between 0 and 255 specifying rgba 
(red, green, blue, alpha) values for the overlay item line color.  If none
is specified, SILT will use a default magenta color (255, 0, 255, 255).

"style" contains a string to define the line style.  Valid options are one 
of "dotted," "dashed," or "solid."  If none is specified, SILT will use 
"solid" by default.

"line_width" contains a float or integer specifying overlay item line
width in pixels.

There are sample overlay files included in the sample_images/aerial_homes/
and the sample_images/aerial_homes_with-checklist/ directories.

### Using SILT

Before running SILT, ensure the following:
1. You have the prerequisites.
2. You've properly installed SILT using pip.  You can use the following pip
    command to ensure that it is installed and show version information:
```bash
pip show silt
```
3. Your template file and image files meet the requirements outlined above.


#### Starting the program

If you've completed at least 1. and 2. then you can run SILT with a simple call 
in a terminal:

``` bash
silt
```

After a moment, the SILT program window should appear.

#### Loading a template

The first thing you must do is load a template file.  Select 
**File > Open template** and navigate to your template file. Click **Open**. 
If the template is successfully loaded, the filename of that template 
should appear at the top of the left side panel in SILT.

You can also set up SILT to automatically load a specified template on
opening the program.  See the section on _Configuration Files_, below.

#### Loading an image or series

Next you may load an image or series.  An image is just that - a single image.  
A series refers to a collection of similar images, like frames of a video.  
Opening an image will load just that image into SILT; opening a series will 
load any HDF5 file matching your template into a list in the right side panel 
in SILT, and you can navigate among those files using the right side panel.

To open an image, select **File > Open image** and navigate to your image file.  
Click **Open**. The image should appear in the SILT tool. Large images may 
take a moment to load.

To open a series, select **File > Open series** and navigate to the directory 
containing your series.  Click **Open**.  SILT will automatically load any 
HDF5 files in that directory AND in any subdirectories that match your 
template.  A new side panel should appear on the right side of SILT containing 
an interactive list showing the paths to all of the images in the series you 
loaded.  Clicking on one of the paths in the list will open and display that 
image in SILT.

When you open images, you will be prompted on whether you would like to generate an image
pyramid or not. Opting not to will load the entire image, in full resolution, 
into the SILT UI. Generating a pyramid will only occur once, after which the pyramid, 
containing different resolutions of the image, will be saved to the same H5 file.
SILT will then load these different resolutions at different zoom levels, saving memory. 
This option is recommended for very large images, on low memory systems.

#### Interacting with images in SILT

Whether you work with a single image or with a series of images, interacting 
with imagery in SILT is largely the same - and it's a lot easier if you have a 
mouse!

To zoom in and out on the image, use the scroll-wheel on your mouse or the 
scroll gesture on your trackpad. To pan, position the mouse pointer anywhere 
over the image, then hold down the left mouse button and move the mouse. You 
may also use the scroll bars on the right and bottom edges to pan.

To add overlay items to the image, you may use the **Add** menu in the menu bar 
or click an icon in the toolbar. SILT currently only supports polygon overlay 
items.

When you add an overlay item to the image, that item should appear over your 
image and some input fields (if you added them to your template file) should 
appear in the left side panel. The input fields correspond to the overlay 
item. If you use the overlay item to label or segment an object in the image, 
then the corresponding input fields may be used to describe that object. Of 
course, you can use the input options however you see fit.

#### Saving

To save your work, use either the **File > Save** or the 
**File > Save As** option in the menu bar.  

**File > Save** (if you haven't used **File > Save as** yet) will use the 
default filename, which is the same as the HDF5 filename with the extension 
specified in the template file or the SILT default extension ".json" if none 
is specified, to save your file into the same location as the HDF5 file. 
If you re-open the HDF5 image file later, SILT will automatically load the 
default labels file.

Don't worry if you don't want to use the default - just use **File > Save as** 
instead, and you may choose where to save and what to name your labels file. 
If you use **File > Save as** and then continue to work, you may use 
**File > Save** to continue to save your work to the file you specified. If 
you close and re-open the HDF5 image file later, SILT will not be able to 
automatically load the labels file, but you can load a non-default-named 
labels file by using **File > Open template** in the menu bar and navigating to 
the appropriate labels file.

#### Configuration Files

The configuration file can be used to have SILT automatically load a particular
template file on opening the program, making the **File > Open template** step
unnecessary each time you run SILT.  This is useful if you are working on one
large set of images which all use the same template file.  The configuration
file has a specific name and must be copied to a specific location.

The configuration file must be called `siltconfig.json` and contains a
dictionary.  That dictionary currently has only one key-value pair:  
`"default_template_file": "/absolute/path/to/yourtemplate.silttemplate.json"`  
where you will fill in the absolute path to your desired
template file.  There are sample `[sample]_siltconfig.json` files included in this
repo in the `silt/` directory which you can use as a starting point.

Once edited and named appropriately, the configuration file must be copied to
the location next to your SILT installation on your filesystem.  If you used pip 
to install SILT, you can use `pip show silt` to determine where it was installed 
to.  Usually it is located in a `site-packages` directory under the current
Python installation.  Just copy your `siltconfig.json` file to wherever SILT is
installed (it should go NEXT TO the `silt` directory, NOT inside the `silt` 
directory).

---

## Running tests

Unit tests can be found in the [test](./silt/test/) folder. To run all tests:

``` bash
pytest
```

If installed, and given your machine has Xvfb installed, the pytest-xvfb plugin will run tests with Xvfb by default, stopping windows from popping up while testing GUI components.

