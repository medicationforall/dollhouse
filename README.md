# Dollhouse

![](doc_image/35.png)<br />

![](doc_image/36.png)<br />

## Description

First large project I've attempted using CadQuery. <br />
Goal was to make a modular dollhouse for my kids.

![](doc_image/33.png)<br />


It's a tudor style house with inspiration drawn from google image searches.<br />
The central idea is that it would be printed in roughly nine sections. With the floors and roof divided into three sections each.

I opted for the main rooms to be 175mm x 175mm x 175mm or roughly 7" x 7" x 7".<br />
Which is just about the limits of my print bed.

---
## Code

### Dependencies
* [CadQuery](https://cadquery.readthedocs.io/en/latest/) - Python Cad Libary
* [CQ-Editor](https://github.com/CadQuery/CQ-editor) - GUI to see model changes
* [cadqueryhelper](https://github.com/medicationforall/cadqueryhelper) - Shape primitives libraries, used for object repetition. (I wrote this)
* [cqterrain](https://github.com/medicationforall/cqterrain) - Primary library used to build the house (I authored this as well)

I opted for python code to make the cad model because I like making 3d models with code.<br />I've used [OpenSCAD](https://openscad.org/) in the past, but it has limitations for large projects.

### Pros
* Python has a large ecosystem
* Parts of the model can be broken up into smaller modules and tested in solation.
* Version control - I can review changes to the model before committing.
* [Github](https://github.com/) - code is kept in the cloud in a private (or public) repo.
* Re-using code from one project to the next is pretty straight forward.

### Cons
* Tedious, the project itself was 500+ lines of code just for the dollhouse itself.
* The re-usable api was expanded out as the model was being created.
* If there are bugs in your logic tracking them down can be arduous, the generated models does not necessarily lend themselves well to unit tests.

### In the beginning
The initial outline of the project.
![](doc_image/04.png)<br />
The front is too boring

![](doc_image/03.png)<br />
Shows the breakdown of the nine sections.

### Adding exterior details
![](doc_image/06.png)<br />
I ended simplifying from the initial sketch.

![](doc_image/05.png)<br />
I used [Microsoft 3d Viewer](https://all3dp.com/2/microsoft-3d-viewer-guide/) to generate the lighting on the model

![](doc_image/07.png)<br />
Interior is still plain

---

## Details

## Arches
The arch cutouts are straight forward.<br />
``` python
def make_arch_door(wall, length, width, height, floor_height):
    # find the bottom of the wall to align to.
    bottom = wall.faces("-Z").val()

    #create the initial shape
    cutout = (cq.Workplane(bottom.Center())
              .box(length, width, height)
              .translate((0,0,(height/2)+floor_height))
              )

    # round off the top          
    cutout = cutout.faces("Z").edges("Y").fillet((length/2)-.5)

    #remove the arch from the wall
    w = wall.cut(cutout)
    return w
```
The arch is aligned to the bottom of the object it's being cut out of.
![](doc_image/34.png)


### Stones
I opted, to write a pseudo-random stone pattern generator
![](doc_image/stone_01.png)<br />

Code for a stone section.

``` python
def add_stones(wall, length, height, wall_width, rotate=0, seed="test4"):
    # static boxes to act as stone
    tile = cq.Workplane("XY").box(10,10,2)
    tile2 = cq.Workplane("XY").box(8,8,2)
    tile3 = cq.Workplane("XY").box(6,12,2)

    # create an array of the stones and chamfer / fillet to add interest to the shapes.
    stone_list = [tile.chamfer(0.8), tile2.fillet(.5), tile3.chamfer(0.5)]

    # This is the pattern generator
    stones = stone.make_stones(stone_list, [12,12,2], columns = 14, rows = 3, seed=seed).rotate((0,1,0),(0,0,0), 90).rotate((0,0,1),(0,0,0), 90)

    # Align the pattern and surround with a frame
    stones = stones.translate((0,-2,-1*(height/2)+(24))).rotate((0,0,1),(0,0,0), rotate)
    frame = window.frame(length, 2, 48).translate((0,-1*((1)+(wall_width/2)),-1*(height/2)+(24))).rotate((0,0,1),(0,0,0), rotate)

    # Add the detailing to the room wall
    return wall.add(stones).add(frame)
```

* The generated output of the stone pattern is defined by the seed.
  * different seed means different stone placement.

Let's looks at cqterrain [stone.make_stones](https://github.com/medicationforall/cqterrain/blob/main/src/cqterrain/stone.py) code

``` python
import cadquery as cq
import random
import math

def make_stones(parts, dim=[5,5,2], rows=2, columns=5, seed="test4"):
    grid = cq.Assembly()
    random.seed(seed)

    # loop the rows
    for row_i in range(rows):
        row_offset = (dim[0] * row_i)
        # loop the columns per row
        for col_i in range(columns):
            col_offset = (dim[1] * col_i)

            col_push_x = 0
            col_push_y = 0
            if col_i % 2 == 1:
                col_push_x = 0
                col_push_y = 0

            z_push=0
            # move the part in a random direction along the x and y axis.
            x_rand = random.randrange(-1*(math.floor(dim[0]/2)),(math.floor(dim[0]/2)))
            y_rand = random.randrange(-1*(math.floor(dim[1]/2)),(math.floor(dim[1]/2)))

            # choose a random part from the parts list
            part_index = random.randrange(0,len(parts))

            # add the part to the assembly
            grid.add(parts[part_index], loc=cq.Location(cq.Vector(row_offset + col_push_x + x_rand, col_offset + col_push_y + y_rand, z_push)))

    length = dim[1] * columns
    width = dim[0] * rows

    # dump the assembly out as a single compound
    comp = grid.toCompound()
    work = cq.Workplane("XZ").center(0, 0).workplane()
    work.add(comp)

    # zero out the grid
    work = work.translate(((dim[0]/2),(dim[1]/2)))
    work = work.translate((-1*(width/2),-1*(length/2)))
    return work
```

* That's all of of it, the double for loop isn't ideal but I kept it for readability.
* I basically yoinked my code for laying a tile onto a grid, and modified it to support pseudo-random selection and placement.
* It's not perfect but it's good enough to give the impression of a stone pattern.
* The code isn't resource intensive since it's made up of very simple primitives.

![](doc_image/39.png)<br />

## Casement Windows
![](doc_image/window_casement_01.png)<br />

``` python
def casement_windows(wall, length, width, height, count, padding):
    # Create the cut out the holes where the windows will be placed.
    window_cutout = cq.Workplane().box(length, width, height)
    window_cut_series = series(window_cutout, count, length_offset = padding)

    # create the window frame, and grill.
    i_window = window.frame(length, width+3, height)
    grill = window.grill(length=length, width=4, height=height, rows=4, columns=2, grill_width=2, grill_height=3)
    i_window.add(grill)

    # Create the window set
    window_series = series(i_window, count, length_offset = padding)

    # Remove the cutout and add the windows
    w = wall.cut(window_cut_series)
    w = w.add(window_series)

    return w
```

Making the grill

``` python
def grill(length=20, width=4, height=40, columns=4, rows=2, grill_width=1, grill_height=1):
    # Make a flat plane
    pane = cq.Workplane("XY").box(length, grill_height, height)
    t_width = length / columns
    t_height = height / rows

    # Make the window cutout
    tile = cq.Workplane("XY").box(t_width, grill_height, t_height).rotate((1,0,0),(0,0,0),90)

    # Repeat the cutout
    tiles = grid.make_grid(tile, [t_width+grill_width, t_height+grill_width], rows=columns, columns=rows).rotate((1,0,0),(0,0,0),-90)

    # Remove the window cutouts leaving the frame
    combine = pane.cut(tiles)
    return combine
```

![](doc_image/window_casement_02.png)<br />

![](doc_image/38.png)<br />

### Roof Details
The roof tiles was a struggle but it was a good opportunity re-learn some trigonometry.


---
## Printing
