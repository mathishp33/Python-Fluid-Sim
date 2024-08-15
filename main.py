import pygame as pg
import numpy as np

try: 
    import taichi as ti
    ti.init(arch=ti.gpu)
except:
    pass
    
tile_size, tile_grid = 10, 40
RES = WIDTH, HEIGHT = tile_grid*tile_size, tile_grid*tile_size
screen = pg.display.set_mode(RES) 
clock = pg.time.Clock()


k=0.4
r=tile_size
debug = False

def IX(x, y):
    return x+y*tile_grid
          
def lerp(a, b, m):
    a, b, m = float(a), float(b), float(m)
    return a+m*(b-a)

def check(x,y):
    if x != tile_grid-1 or x != 0 or y != tile_grid-1 or y != 0: 
        return False
    else:
        return True
        
class Tile():
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.pos = x, y
        self.Dc = 0
        self.Dn = 0
        self.k = 0.4
        self.c = 0.9
        self.Sc = 0
        self.l = 0
        self.color = (0, 0, 0)
        self.v = np.array([0, 0])
        self.f = np.array([0, 0])
        self.i = np.array([0, 0])
        self.o = np.array([0, 0])
        self.center = (0, 0)
        self.rect = pg.rect.Rect(0, 0, 0, 0)
    def get_d(self):
        return self.d
    def draw(self):
        if 0<=self.Dc<=255:
            self.color = [self.Dc, self.Dc, self.Dc]
        elif self.Dc>255:
            self.color = [255, 255, 255]
        else:
            self.color = [0, 0, 0]
        pg.draw.rect(screen, self.color, pg.rect.Rect(self.x*tile_size, self.y*tile_size, tile_size, tile_size))
        self.rect = pg.rect.Rect(self.x*tile_size, self.y*tile_size, tile_size, tile_size)
        self.center = (self.x*tile_size +tile_size/2, self.y*tile_size +tile_size/2)
        if debug:
            pg.draw.line(screen, (255, 0, 0), self.center+self.v*tile_size, self.center)
    def update(self):
        #diffuse
        self.Sc = 0
        self.l = 0
        if self.x != tile_grid-1: 
            self.Sc += tiles[IX(self.x+1, self.y)].Dc
            self.l += 1
        if self.x != 0: 
            self.Sc += tiles[IX(self.x-1, self.y)].Dc
            self.l += 1
        if self.y != tile_grid-1: 
            self.Sc += tiles[IX(self.x, self.y+1)].Dc
            self.l += 1
        if self.y != 0: 
            self.Sc += tiles[IX(self.x, self.y-1)].Dc
            self.l += 1
        
        self.Sc = self.Sc/self.l
        self.Dn = self.Dc+self.k*(self.Sc-self.Dc)
        self.Dc = self.Dn
        #advection
        if abs(self.v[0])+abs(self.v[1]) < 2: self.v = np.array([0, 0])
        if not (self.v  == np.array([0, 0])).all():
            for tile in tiles:
                if pg.rect.Rect(tile.x*tile_size, tile.y*tile_size, tile_size, tile_size).collidepoint((self.pos+self.v)*tile_size):
                    self.o = np.array([tile.x, tile.y])
                    self.f = self.o - self.v
                    self.i = np.floor(self.f).astype(np.int64)
                    self.j = self.f - self.i
                    if self.x != tile_grid-1:
                        self.z1 = lerp(tiles[IX(self.i[0], self.i[1])].Dc, tiles[IX(self.i[0]+1, self.i[1])].Dc, self.j[0])
                    else : self.z1 = tiles[IX(self.i[0], self.i[1])].Dc
                    if self.y != tile_grid-1 and self.x != tile_grid-1:
                        self.z2 = lerp(tiles[IX(self.i[0], self.i[1]+1)].Dc, tiles[IX(self.i[0]+1, self.i[1]+1)].Dc, self.j[0])
                    elif self.y != tile_grid-1:
                        self.z2 = tiles[IX(self.i[0], self.i[1]+1)].Dc
                    if self.x != tile_grid-1 and  self.y != tile_grid-1: 
                        self.z3 = float(lerp(self.z1, self.z2, self.j[1]))
                    else : self.z3 = self.Dc
                    if self.Dc<self.z3:
                        self.z3 = self.Dc
                    tiles[IX(self.o[0], self.o[1])].Dc += self.z3
                    self.Dc -= self.z3
            self.v = self.v*self.c


        
tiles = [Tile(j, i) for i in range(tile_grid) for j in range(tile_grid)]

running = True
while running :
    pg.display.set_caption('Fluid Simulation | ' + str(round(clock.get_fps()*10)/10))
    screen.fill((0, 0, 0))
    mouse_pos = pg.mouse.get_pos()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    if pg.mouse.get_pressed()[0]:
        for tile in tiles:
            if pg.rect.Rect(tile.x*tile_size, tile.y*tile_size, tile_size, tile_size).collidepoint(mouse_pos):
                tile.Dc += 50
    if pg.mouse.get_pressed()[1]:
        for tile in tiles:
            if pg.rect.Rect(tile.x*tile_size, tile.y*tile_size, tile_size, tile_size).collidepoint(mouse_pos):
                tile.Dc -= 50
    if pg.mouse.get_pressed()[2]:
        mouse_pos0 = mouse_pos
        val = True
        while val:
            d = []
            for tile in tiles:
                if pg.draw.circle(screen, (0, 255, 0), (mouse_pos0), r).colliderect(tile.rect):
                    d.append(tiles.index(tile))
            mouse_pos = pg.mouse.get_pos()
            if not pg.mouse.get_pressed()[1]: val = False
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    val = False
            clock.tick(60)
        v = (np.array(mouse_pos)-np.array(mouse_pos0))//tile_size
        for d0 in d:
            tiles[d0].v += v

            
    for i in  tiles:
        i.update()
        i.draw()
        
    pg.display.update()
    clock.tick(60)
            
pg.quit()