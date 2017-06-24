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
    frames = 0
    basename = None
    vary = False
    for command in commands:
        c = command[0]
        args = command[1:]
        if (c == "frames"):
            frames = int(args[0])
        if (c == "basename"):
            basename = args[0]
        if (c == "vary"):
            vary = True
    if vary and frames == 0:
        print "frames is not defined."
        exit()
    if frames > 0 and basename == None:
        basename = "untitled"
        print "no basename initiated. set basename to 'untitled.'"
    return frames, basename, vary


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
    knobs = [dict() for i in range(num_frames)]
    for command in commands:
        c = command[0]
        args = command[1:]
        if c == "vary":
            knob = args[0]
            startFrame = int(args[1])
            endFrame = int(args[2])
            startVal = float(args[3])
            endVal = float(args[4])
            for i in range(len(knobs)):
                if not(knob in knobs[i]):
                    knobs[i][knob] = 0
                if i >= startFrame and i <= endFrame:
                    knobs[i][knob] = startVal + (((endVal-startVal)*(i-startFrame))/(endFrame-startFrame))
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
    ident(tmp)
    stack = [ [x[:] for x in tmp] ]
    screen = new_screen()
    tmp = []
    step = 0.1
    frames, basename, vary = first_pass(commands)
    knob = second_pass(commands, frames)
    for frame in range(frames):
        tmp = new_matrix()
        ident(tmp)
        stack = [ [x[:] for x in tmp] ]
        tmp = []
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
                if args[3] != None:
                    x = args[0]*knob[frame][args[3]]
                    y = args[1]*knob[frame][args[3]]
                    z = args[2]*knob[frame][args[3]]
                    args = [x,y,z]
                tmp = make_translate(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                if args[3] != None:
                    x = args[0]*knob[frame][args[3]]
                    y = args[1]*knob[frame][args[3]]
                    z = args[2]*knob[frame][args[3]] 
                    args = [x, y, z]
                tmp = make_scale(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                if args[2] != None:
                    angle = args[1]*knob[frame][args[2]]
                    args = [args[0], angle]
                theta = args[1] * (math.pi/180)
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == "set":
                knob[frame][args[0]] = float(args[1])
            elif c == "set_knobs":
                for variables in knob[frame]:
                    knob[frame][variables] = float(args[0])
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
        if frame < 10:
            save_extension(screen, 'anim/' + basename + '0' +str(frame))
        else:
            save_extension(screen, 'anim/' + basename + str(frame))
        clear_screen(screen)
