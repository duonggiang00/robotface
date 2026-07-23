class ComponentAnim:
    def __init__(self, comp):
        self.current = comp; self.target = comp; self.outgoing = None; self.fade_t = 1.0
    def set_target(self, new_comp):
        if type(self.current) == type(new_comp): self.target = new_comp
        else: self.outgoing = self.current; self.target = new_comp; self.current = new_comp; self.fade_t = 0.0
    def update(self, speed):
        if self.fade_t < 1.0:
            self.fade_t += 0.15 # Fast fixed crossfade
            if self.fade_t >= 1.0: 
                self.fade_t = 1.0; self.outgoing = None
        else: 
            self.current = self.current.lerp(self.target, speed)
            
    def draw(self, painter, cx, cy):
        if self.fade_t < 1.0 and self.outgoing:
            self.outgoing.draw(painter, cx, cy, 1.0 - self.fade_t)
        self.current.draw(painter, cx, cy, self.fade_t)
