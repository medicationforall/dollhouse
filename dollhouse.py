import cadquery as cq
from cqterrain import Building, window, roof, stone
from cadqueryhelper import series, grid

cq_editor_show = False
export_to_file = True
render_floor = False
render_roof_tiles = True

def add_tudor_frame(wall, length, height, wall_width, frame_width=5, frame_height=3, rows=2, columns = 5,  w_length=0, w_height=0, rotate=0):
    #show_object(wall)
    t_length = length/ columns - frame_width
    t_width = frame_height
    t_height =  (height / rows) - frame_width

    frame = window.frame(length, frame_width, height).translate((0,-1*((frame_height/2)+(wall_width/2)),0))
    grill = window.grill(length, wall_width, height, columns, rows, frame_width, frame_height ).translate((0,-1*((frame_height/2)+(wall_width/2)),0))
    if w_length and w_height:
        win_cut = cq.Workplane("XY").box(w_length, frame_height, w_height).translate((0,-1*((frame_height/2)+(wall_width/2)),0))

        grill_cut = grill.cut(win_cut)
        #show_object(grill_cut)

        if rotate:
            grill_cut = grill_cut.rotate((0,0,1),(0,0,0),rotate)
            frame = frame.rotate((0,0,1),(0,0,0),rotate)
        return wall.add(frame).add(grill_cut)
    #show_object(grill2)
    if rotate:
        grill = grill.rotate((0,0,1),(0,0,0),rotate)
        frame = frame.rotate((0,0,1),(0,0,0),rotate)
    return wall.add(frame).add(grill)

def add_stones(wall, length, height, wall_width, rotate=0, seed="test4"):
    tile = cq.Workplane("XY").box(10,10,2)
    tile2 = cq.Workplane("XY").box(8,8,2)
    tile3 = cq.Workplane("XY").box(6,12,2)
    stone_list = [tile.chamfer(0.8), tile2.fillet(.5), tile3.chamfer(0.5)]
    stones = stone.make_stones(stone_list, [12,12,2], columns = 14, rows = 3, seed=seed).rotate((0,1,0),(0,0,0), 90).rotate((0,0,1),(0,0,0), 90)
    stones = stones.translate((0,-2,-1*(height/2)+(24))).rotate((0,0,1),(0,0,0), rotate)
    frame = window.frame(length, 2, 48).translate((0,-1*((1)+(wall_width/2)),-1*(height/2)+(24))).rotate((0,0,1),(0,0,0), rotate)

    #show_object(stones)
    #show_object(wall)
    #show_object(frame)
    return wall.add(stones).add(frame)



def make_roof(roof_width=185, x_offset=0):
    gable_roof_raw = roof.dollhouse_gable(length=roof_width, width=185, height=100)
    gable_roof = roof.shell(gable_roof_raw,face="Y", width=-4)
    angle = roof.angle(185, 100)
    face_x = gable_roof_raw.faces("<X")

    if render_roof_tiles:
        tile = cq.Workplane("XY").box(15,12,2).rotate((0,1,0),(0,0,0),8)
        tiles = roof.tiles(tile, face_x, 185, 100, 15, 12, angle, rows=28, odd_col_push=[3,0], intersect=False).rotate((0,0,1),(0,0,0),90).translate((3,45,0))
        tiles = tiles.translate((x_offset,0,0))
        inter_tiles = cq.Workplane("XY").box(roof_width,185, 100)
        inter_tiles = tiles.intersect(inter_tiles)

        #show_object(inter_tiles)
        #show_object(gable_roof)
        #return gable_roof
        return gable_roof.add(inter_tiles)
    else:
        return gable_roof


def make_over_roof(roof_part, width=185):
    gable_roof_raw = roof.dollhouse_gable(length=width, width=185, height=100).translate((0,0,-4.5))

    length=185
    height = 100
    inner_height = 60
    roof_half_one = roof.dollhouse_gable(length=140, width=40, height=30).translate((0,0,29)).rotate((0,0,1),(0,0,0),90).translate((-20,15,0))
    roof_half_two = roof.dollhouse_gable(length=140, width=40, height=30).translate((0,0,29)).rotate((0,0,1),(0,0,0),-90).translate((20,15,0))

    if render_roof_tiles:
        angle = roof.angle(40, 30)
        face_x = roof_half_one.faces(">X")
        tile = cq.Workplane("XY").box(15,12,2).rotate((0,1,0),(0,0,0),8)
        tiles = roof.tiles(tile, face_x, 140, 30, 15, 12, angle, rows=4, odd_col_push=[3,0], intersect=False).translate((-14.5,23,29))
        tiles2 = roof.tiles(tile, face_x, 140, 30, 15, 12, angle, rows=4, odd_col_push=[3,0], intersect=False).translate((-14.5,23,29)).rotate((0,0,1),(0,0,0),180).translate((0,46,0))


    inner = roof_part.faces("<Z").box(80,110,inner_height, combine=False).translate((0,0,inner_height/2+4))
    inner = inner.union(roof_half_one).union(roof_half_two)
    #show_object(inner)
    #show_object(roof_part)

    inner_shell = roof_part.faces("<Z").box(80,140,inner_height, combine=False).translate((0,15,inner_height/2+4))
    inner_shell = inner_shell.union(roof_half_one).union(roof_half_two)

    inner_shell = inner_shell.faces(">Y").shell(-4)

    if render_roof_tiles:
        tile_cut = cq.Workplane("XY").box(40,140,50).translate((20,15,25))
        tile_cut2 = cq.Workplane("XY").box(40,140,50).translate((-20,15,25))

        tiles = tiles.intersect(tile_cut)
        tiles2 = tiles2.intersect(tile_cut2)

        inner_shell = inner_shell.add(tiles).add(tiles2)
    inner_shell = inner_shell.cut(gable_roof_raw)

    combine = roof_part.cut(inner).add(inner_shell)

    window_slug = inner.faces("<Y").cylinder(8,20,combine=False).rotateAboutCenter((1,0,0),90).translate((0,2.5,10))
    window_inner = inner.faces("<Y").cylinder(8,17,combine=False).rotateAboutCenter((1,0,0),90).translate((0,2.5,10))
    win_frame = window_slug.cut(window_inner)
    grill = window.grill(40, 5, 40, 2, 2, 3, 3 ).translate((0,-52,5))
    combine = combine.cut(window_slug).add(win_frame).add(grill)

    #show_object(window_slug)
    #show_object(combine)
    return combine



def lattice_windows(wall, length, width, height, count, padding):
    #log(f'custom window lattice {length}, {height}')
    window_cutout = cq.Workplane().box(length, width, height)
    window_cut_series = series(window_cutout, count, length_offset = padding)

    i_window = window.frame(length, width+3, height)
    lattice = window.lattice(length=length, width=4, height=height, tile_size=6, lattice_height=2)
    i_window.add(lattice)
    window_series = series(i_window, count, length_offset = padding)

    w = wall.cut(window_cut_series)
    w = w.add(window_series)

    return w

def casement_windows(wall, length, width, height, count, padding):
    window_cutout = cq.Workplane().box(length, width, height)
    window_cut_series = series(window_cutout, count, length_offset = padding)

    i_window = window.frame(length, width+3, height)
    grill = window.grill(length=length, width=4, height=height, rows=4, columns=2, grill_width=2, grill_height=3)
    i_window.add(grill)
    window_series = series(i_window, count, length_offset = padding)

    w = wall.cut(window_cut_series)
    w = w.add(window_series)

    return w

def casement_windows_2(wall, length, width, height, count, padding):
    window_cutout = cq.Workplane().box(length, width, height)
    window_cut_series = series(window_cutout, count, length_offset = padding)

    i_window = window.frame(length, width+3, height)
    grill = window.grill(length=length, width=4, height=height, rows=4, columns=4, grill_width=2, grill_height=3)
    i_window.add(grill)
    window_series = series(i_window, count, length_offset = padding)

    w = wall.cut(window_cut_series)
    w = w.add(window_series)

    return w

if render_floor:
    pattern = cq.importers.importStep('stl/floral.step')
    scaled = pattern.val().scale(0.15)
    center = scaled.CenterOfBoundBox()
    pattern = cq.Workplane().add(scaled).translate((center.x*-1,center.y*-1,center.z*-1))


def make_arch_door(wall, length, width, height, floor_height):
    bottom = wall.faces("-Z").val()
    cutout = (cq.Workplane(bottom.Center())
              .box(length, width, height)
              .translate((0,0,(height/2)+floor_height))
              )
    cutout = cutout.faces("Z").edges("Y").fillet((length/2)-.5)
    w = wall.cut(cutout)
    return w


def make_kitchen():
    bp = Building(length=175, width=175, height=350, stories=2)

    bp.room['build_walls']= [False,True,True,True]
    bp.room['window_walls'] = [False, True, True, False]
    bp.room['door_walls'] = [False, False, False, True]
    bp.room['make_custom_door'] = make_arch_door
    if render_floor:
        bp.room['floor_tile'] = pattern
        bp.room['floor_tile_padding'] = .5

    bp.door['length'] = 60
    bp.door['height'] = 100

    bp.window['height'] = 55
    bp.window['length'] = 78

    bp.make()
    bp.floors[0].window_count=4
    bp.floors[0].window['height'] = 45
    bp.floors[0].window['length'] = 28
    bp.floors[0].make_custom_windows = casement_windows
    bp.floors[0].make()

    st_front_wall = bp.floors[0].walls[1]
    stone_wall = add_stones(st_front_wall, 175, bp.floors[1].height, bp.floors[1].wall_width)
    bp.floors[0].walls[1] = stone_wall

    st_side_wall = bp.floors[0].walls[2]
    stone_side_wall = add_stones(st_side_wall, 175, bp.floors[0].height, bp.floors[0].wall_width, rotate = -90, seed="test5")
    bp.floors[0].walls[2] = stone_side_wall

    bp.floors[1].make_custom_windows = lattice_windows
    bp.floors[1].make()

    front_wall = bp.floors[1].walls[1]
    paneled_wall = add_tudor_frame(front_wall, 175, bp.floors[1].height, bp.floors[1].wall_width, frame_width=5, frame_height=1.5, columns=4, w_length=78, w_height=55)
    bp.floors[1].walls[1] = paneled_wall

    side_wall = bp.floors[1].walls[2]
    paneled_wall2 = add_tudor_frame(side_wall, 175, bp.floors[1].height, bp.floors[1].wall_width, frame_width=5, frame_height=1.5, columns=4, w_length=78, w_height=55, rotate=-90)
    bp.floors[1].walls[2] = paneled_wall2#.rotate((0,0,1),(0,0,0),-90)

    left = bp.build()
    left_roof = make_roof()#x_offset=5)#.translate((5,-5,312.5))
    over_roof = make_over_roof(left_roof, 125)
    over_roof2 = over_roof.translate((5,-5,312.5))

    combine = cq.Workplane("XY").add(left).add(over_roof2)
    #return over_roof
    return combine

def make_back_kitchen():
    bp = Building(length=175, width=175, height=350, stories=2)

    bp.room['build_walls']= [True,False,True,True]
    bp.room['window_walls'] = [True, False, True, False]
    bp.room['door_walls'] = [False, False, False, True]
    bp.room['make_custom_door'] = make_arch_door
    bp.door['length'] = 60
    bp.door['height'] = 100

    #if render_floor:
    #    bp.room['floor_tile'] = pattern
    #    bp.room['floor_tile_padding'] = .5

    bp.window['height'] = 55
    bp.window['length'] = 78

    bp.make()
    bp.floors[0].window_count=4
    bp.floors[0].window['height'] = 45
    bp.floors[0].window['length'] = 28
    bp.floors[0].make_custom_windows = casement_windows
    bp.floors[0].make()

    st_front_wall = bp.floors[0].walls[0]
    stone_wall = add_stones(st_front_wall, 175, bp.floors[1].height, bp.floors[1].wall_width, rotate = -180)
    bp.floors[0].walls[0] = stone_wall

    st_side_wall = bp.floors[0].walls[2]
    stone_side_wall = add_stones(st_side_wall, 175, bp.floors[0].height, bp.floors[0].wall_width, rotate = -90, seed="test5")
    bp.floors[0].walls[2] = stone_side_wall

    bp.floors[1].make_custom_windows = lattice_windows
    bp.floors[1].make()

    front_wall = bp.floors[1].walls[0]
    paneled_wall = add_tudor_frame(front_wall, 175, bp.floors[1].height, bp.floors[1].wall_width, frame_width=5, frame_height=1.5, columns=4, w_length=78, w_height=55, rotate=-180)
    bp.floors[1].walls[0] = paneled_wall

    side_wall = bp.floors[1].walls[2]
    paneled_wall2 = add_tudor_frame(side_wall, 175, bp.floors[1].height, bp.floors[1].wall_width, frame_width=5, frame_height=1.5, columns=4, w_length=78, w_height=55, rotate=-90)
    bp.floors[1].walls[2] = paneled_wall2#.rotate((0,0,1),(0,0,0),-90)

    left = bp.build()
    left_roof = make_roof().rotate((0,0,1),(0,0,0),180).translate((5,5,312.5))

    combine = cq.Workplane("XY").add(left).add(left_roof)
    return combine

def make_center():
    bp = Building(length=125, width=175, height=350, stories=2)
    bp.room['build_walls']= [False,True,True,True]
    bp.room['window_walls'] = [False, False, False, False]
    bp.room['door_walls'] = [False, False, True, True]
    bp.room['make_custom_door'] = make_arch_door

    bp.door['length'] = 60
    bp.door['height'] = 100

    bp.make()
    bp.floors[0].door_walls = [False, True, True, True]
    bp.floors[0].make()

    front_wall = bp.floors[1].walls[1]
    paneled_wall = add_tudor_frame(front_wall, 125, bp.floors[1].height, bp.floors[1].wall_width, frame_width=5, frame_height=1.5, columns=4)
    bp.floors[1].walls[1] = paneled_wall

    center = bp.build()

    center_roof = make_roof(125)
    over_roof = make_over_roof(center_roof, 125)
    over_roof = over_roof.translate((0,-5,312.5))

    combine = cq.Workplane("XY").add(center).add(over_roof)
    return over_roof
    return combine

def make_center_back():
    bp = Building(length=125, width=175, height=350, stories=2)
    bp.room['build_walls']= [True,False,True,True]
    bp.room['window_walls'] = [False, False, False, False]
    bp.room['door_walls'] = [False, False, True, True]
    bp.room['make_custom_door'] = make_arch_door

    bp.door['length'] = 60
    bp.door['height'] = 100

    bp.make()
    bp.floors[0].door_walls = [True, False, True, True]
    bp.floors[0].make()

    front_wall = bp.floors[1].walls[0]
    paneled_wall = add_tudor_frame(front_wall, 125, bp.floors[1].height, bp.floors[1].wall_width, frame_width=5, frame_height=1.5, columns=4, rotate = 180)
    bp.floors[1].walls[0] = paneled_wall

    center = bp.build()

    center_roof = make_roof(125)
    center_roof = center_roof.rotate((0,0,1),(0,0,0),180).translate((0,5,312.5))

    combine = cq.Workplane("XY").add(center).add(center_roof)
    return combine


def make_living():
    bp = Building(length=175, width=175, height=350, stories=2)

    bp.room['build_walls']= [False,True,True,True]
    bp.room['window_walls'] = [False, True, False, True]
    bp.room['door_walls'] = [False, False, True, False]
    bp.room['make_custom_door'] = make_arch_door

    bp.door['length'] = 60
    bp.door['height'] = 100

    bp.window['height'] = 55
    bp.window['length'] = 78

    bp.make()

    bp.floors[0].make_custom_windows = casement_windows_2
    bp.floors[0].make()

    st_front_wall = bp.floors[0].walls[1]
    stone_wall = add_stones(st_front_wall, 175, bp.floors[1].height, bp.floors[1].wall_width, seed="test7")
    bp.floors[0].walls[1] = stone_wall

    st_side_wall = bp.floors[0].walls[3]
    stone_side_wall = add_stones(st_side_wall, 175, bp.floors[0].height, bp.floors[0].wall_width, rotate = 90, seed="test9")
    bp.floors[0].walls[3] = stone_side_wall

    bp.floors[1].make_custom_windows = lattice_windows
    bp.floors[1].make()

    front_wall = bp.floors[1].walls[1]
    paneled_wall = add_tudor_frame(front_wall, 175, bp.floors[1].height, bp.floors[1].wall_width, frame_width=5, frame_height=1.5, columns=4, w_length=78, w_height=55)
    bp.floors[1].walls[1] = paneled_wall

    side_wall = bp.floors[1].walls[3]
    paneled_wall2 = add_tudor_frame(side_wall, 175, bp.floors[1].height, bp.floors[1].wall_width, frame_width=5, frame_height=1.5, columns=4, w_length=78, w_height=55, rotate=90)
    bp.floors[1].walls[3] = paneled_wall2#.rotate((0,0,1),(0,0,0),-90)


    right = bp.build()
    right_roof = make_roof()#.translate((-5,-5,312.5))
    over_roof = make_over_roof(right_roof, 125)
    over_roof2 = over_roof.translate((-5,-5,312.5))

    combine = cq.Workplane("XY").add(right).add(over_roof2)
    #return over_roof
    return combine


#left = make_kitchen().translate((87.5 + 62.5,0,0))
#left_back = make_back_kitchen().translate((87.5 + 62.5,175,0))
center = make_center()
#center_back = make_center_back().translate((0,175,0))
#right = make_living().translate((-87.5 - 62.5,0,0))

scene = (cq.Workplane("XY")
         #.add(left)
         #.add(left_back)
         .add(center)
         #.add(center_back)
         #.add(right)
         )


if cq_editor_show:
    show_object(scene)

if export_to_file:
    cq.exporters.export(scene,'out/dollhouse_03_center.stl')
