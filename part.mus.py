#!/Users/...

from math import sqrt, pi, fabs, cos, sin
import cairo
from random import random

max=32767.0 # 2^15 - 1
frame_len=2940 # 44.1 kHz, 2 channels, and 30 fps
N_FILES=15

data = open( '0.dat' )

data_points=0
for line in data : 
    data_points=data_points+1

data=[]
for i in range( N_FILES ) :
    data.append( open( '{}.dat'.format( i ) ) )

# setup cairo

WIDTH=1920  # 1280
HEIGHT=1080 # 720

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

ctx.scale(WIDTH, HEIGHT)  # Normalizing the canvas

ctx.rectangle(0, 0, 1, 1)  # Rectangle(x0, y0, x1, y1)

ctx.set_source_rgb(0.0, 0.0, 0.0)
ctx.fill()

ctx.translate(0.0, 0.0)  # Changing the current transformation matrix

# clear canvas

def clear_canv( canv ) :

    canv.rectangle(0, 0, 1, 1)

    canv.set_source_rgba(1.0, 1.0, 1.0,1.0)
    canv.fill()

def draw_circle( canv, x, y, r, cr, cg, cb ) :
    ctx.move_to(x, y)
    ctx.arc(x, y, r, 0, 2*pi)
    ctx.close_path()
    ctx.set_source_rgb(cr, cg, cb)
    ctx.fill()

# draw line

def draw_line( canv, p_x1, p_y1, p_x2, p_y2, rc, gc, bc, alpha ) :

    canv.move_to(p_x1, p_y1)

    canv.line_to(p_x2, p_y2)  # Line to (x,y)

    canv.set_line_width(1/400)

    canv.close_path()

    canv.set_source_rgba( rc, gc, bc, alpha )

    canv.stroke()

clear_canv( ctx )

k=0.01*pi

set=[] # holds audio data

q=[] # coordinate list
q.append( [ 0.0, 0.0 ] )
p=[] # momentum list
m=[] # mass list
col=[] # color list
col.append( [ 0.0, 0.0, 0.0 ] )

for i in range( 1, len( data ) ) :
    q.append( [ 0.32*cos(2*pi*(i/(N_FILES-1)))*HEIGHT/WIDTH, 0.32*sin(2*pi*(i/(N_FILES-1))) ] )
    col.append( [ random()*0.5, random()*0.5, random()*0.5 ] )
for i in range( len( data ) ) :
    p.append( [ 0, 0 ] )
    m.append( 0 )

t=0
sc=0.0002

max_p=0

for sf in range( data_points//frame_len ) :

    set=[]

    for i in range( len( data ) ) :
        set.append( [] )
        set[i].append( float( data[i].readline().strip() )/32767.0 )
        m[i]=0

    for i in range( int( frame_len )-1 ) :
        for j in range( len( data ) ) :
            set[j].append( float( data[j].readline().strip() )/32767.0 )

            theta=pi-k*i
            theta_o=pi-k*(i+1)

            upr=400
            low=20

            r=set[j][i]*upr+low*(set[j][i]>0)-low*(set[j][i]<=0)
            r_o=set[j][i+1]*upr+low*(set[j][i+1]>0)-low*(set[j][i+1]<=0)

            m[j]=m[j]+fabs( (r/220)/float( frame_len ) )

            alpha=0.08
            r_c=col[j][0]*i/int(frame_len)+col[j][2]*(1-i/int(frame_len))
            b_c=col[j][1]*i/int(frame_len)+col[j][0]*(1-i/int(frame_len))
            g_c=col[j][2]*i/int(frame_len)+col[j][1]*(1-i/int(frame_len))

            xa=( WIDTH/2+cos( theta )*r )/WIDTH+q[j][0]
            ya=( HEIGHT/2-sin( theta )*r )/HEIGHT+q[j][1]
            xb=( WIDTH/2+cos( theta_o )*r_o )/WIDTH+q[j][0]
            yb=( HEIGHT/2-sin( theta_o )*r_o )/HEIGHT+q[j][1]

            for nx in range( 3 ) :
                for my in range( 3 ) :
                    draw_line( ctx, xa+1.1*nx-1.1, ya+1.1*my-1.1, xb+1.1*nx-1.1, yb+1.1*my-1.1, r_c, g_c, b_c, alpha )


    for i in range( len( data ) ) :
        dpx=0
        dpy=0
        for j in range( len( data ) ) :
            if i != j :
                dx=q[i][0]-q[j][0]
                dy=q[i][1]-q[j][1]
                if dx > 0.55 :
                    dx=-1.1+dx
                elif dx < -0.55 :
                    dx=1.1+dx
                if dy > 0.55 :
                    dy=-1.1+dy
                elif dy < -0.55 :
                    dy=1.1+dy

                mag=sqrt( dx**2+dy**2 )

                dpx=dpx-dx*m[i]*m[j]/mag
                dpy=dpy-dy*m[i]*m[j]/mag

        p[i][0]=p[i][0]+sc*dpx
        p[i][1]=p[i][1]+sc*dpy

    for i in range( len( data ) ) :
        q[i][0]=q[i][0]+p[i][0]/m[i]
        q[i][1]=q[i][1]+p[i][1]/m[i]

        if sqrt( p[i][0]**2+p[i][1]**2 ) > max_p :
            max_p=sqrt( p[i][0]**2+p[i][1]**2 )

        for kk in range( 2 ) :

            if q[i][kk] > 0.55 :
                q[i][kk]=q[i][kk]-1.1
            elif q[i][kk] < -0.55 :
                q[i][kk]=q[i][kk]+1.1

    print( 'Writing frame {}'.format( t ) )
    print( 'Max vel: {}'.format( max_p ) )
    surface.write_to_png('rep/part.test{}.png'.format( t ))
    t=t+1

    clear_canv( ctx )

