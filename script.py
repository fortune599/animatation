import mdl
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands, symbols ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)
  
  Should set num_frames and basename if the frames 
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.

  jdyrlandweaver
  ==================== """
def first_pass( commands ):
    basename = "unspecified"
    num_frames = 0
    stop = False
    for command in commands:
        if command[0] == "frames":
            default = True
            for x in commands:
                if x[0] == "basename":
                    default = False
                    break
            if default:
                print 'using name "unspecified"'
            num_frames = int(command[1])
        if command[0] == "basename":
            basename = command[1]
        if command[0] == "vary":
            execute = True
            for x in commands:
                if x[0] == "frames":
                    execute = False
                    break
            if execute:
                stop = True
    return (stop, basename, num_frames)
                    

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go 
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value. 
  ===================="""
def second_pass( commands, num_frames ):
    knobs = []
    for i in range(num_frames):
        knobs.append({})
    for command in commands[0]:
        if command[0] == "vary":
            f_first = int(command[2])
            f_last = int(command[3])
            noframes = f_last - f_first + 1
            for i in range(0, noframes):
                prog = i + 1
                if float(command[5]) > float(command[4]):
                    knobs[i][command[1]] = float(command[5]-command[4]) / noframes * prog 
                else:
                    knobs[i][command[1]] = float(command[4]) - float(command[4]-command[5]) / noframes * prog
    return knobs


def run(filename):
    """
    This function runs an mdl script
    """
    color = [255, 255, 255]
    tmp = new_matrix()
    ident( tmp )

    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    if first_pass(commands)[0]:
        print 'used "vary" without "frames" error'
        return
    basename = first_pass(commands)[1]
    num_frames = first_pass(commands)[2]
    if not num_frames > 1:
        num_frames = 1

    knobs = second_pass(p,num_frames)
    print knobs

    ident(tmp)
    stack = [ [x[:] for x in tmp] ]
    screen = new_screen()
    tmp = []
    step = 0.1
    for frame in range(num_frames):
        print frame
        for command in commands:
            c = command[0]
            args = command[1:]

            if c == 'box':
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'sphere':
                add_sphere(tmp,
                        args[0], args[1], args[2], args[3], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'torus':
                add_torus(tmp,
                        args[0], args[1], args[2], args[3], args[4], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'move':
                tmp = make_translate(args[0], args[1], args[2])
                if len(args) > 3:
                    scalar_mult(tmp, knobs[frame][args[3]])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                if len(args) > 3:
                    c1 = knobs[frame][args[3]] * args[0]
                    c2 = knobs[frame][args[3]] * args[1]
                    c3 = knobs[frame][args[3]] * args[2]
                    tmp = make_scale(c1,c2,c3)
                else:
                    tmp = make_scale(args[0],args[1],args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                theta = args[1] * (math.pi/180)
                if len(args) > 2:
                    theta *= knobs[frame][args[2]]
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                    matrix_mult( stack[-1], tmp )
                    stack[-1] = [ x[:] for x in tmp]
                    tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
        if num_frames > 1:
            save_extension(screen, "anim/" + basename + "%03d.png"%frame)
            clear_screen(screen)
            stack.pop()
    if num_frames > 1:
        make_animation(basename)
