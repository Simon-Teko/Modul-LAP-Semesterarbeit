import pygame
import random
import json
import math

# Initialisierung
pygame.init()
WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ATC Simulator: ILS Landing Edition")

# Konstanten & JSON Laden
def load_config():
    try:
        with open('planes.json', 'r') as f: return json.load(f)
    except:
        return {"aircraft_types": [{"speed_range": [1, 3], "color": [255,0,0]}], 
                "airport": {"pos": [450, 350], "runway_vector": [-150, 0]}}

CONFIG = load_config()
AIRPORT_POS = pygame.Vector2(CONFIG["airport"]["pos"])
RUNWAY_START = AIRPORT_POS + pygame.Vector2(CONFIG["airport"]["runway_vector"])

class Plane:
    def __init__(self, x, y):
        cfg = random.choice(CONFIG["aircraft_types"])
        self.pos = pygame.Vector2(x, y)
        self.speed = random.uniform(cfg["speed_range"][0], cfg["speed_range"][1])
        self.color = cfg["color"]
        self.radius = 12
        self.state = "APPROACH" # APPROACH -> LANDING -> DONE
        
    def update(self, all_planes):
        # 1. Navigation & Kollisionsvermeidung (Anti-Collision Logic)
        separation_vector = pygame.Vector2(0, 0)
        for other in all_planes:
            if other == self: continue
            dist = self.pos.distance_to(other.pos)
            if dist < 50: # Sicherheitsabstand
                separation_vector += (self.pos - other.pos).normalize() * 0.5

        # 2. ILS Logik (Story: Lande-Vektor)
        if self.state == "APPROACH":
            target = RUNWAY_START
            if self.pos.distance_to(RUNWAY_START) < 10:
                self.state = "LANDING"
        else:
            target = AIRPORT_POS

        # Bewegung berechnen
        direction = (target - self.pos).normalize()
        self.pos += (direction + separation_vector) * self.speed

    def draw(self, surface):
        # Zeichne Flugzeug
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)
        # Kleiner Richtungszeiger
        end_pt = self.pos + (AIRPORT_POS - self.pos).normalize() * 20
        pygame.draw.line(surface, (100, 100, 100), self.pos, end_pt, 2)

def main():
    clock = pygame.time.Clock()
    planes = [Plane(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(4)]
    score = 0
    font = pygame.font.SysFont("Consolas", 20)

    running = True
    while running:
        screen.fill((30, 30, 30)) # Dunkler Radar-Hintergrund
        
        # Flughafen & ILS Glide Slope zeichnen
        pygame.draw.line(screen, (0, 255, 0), RUNWAY_START, AIRPORT_POS, 2) # ILS Pfad
        pygame.draw.rect(screen, (255, 255, 255), (AIRPORT_POS.x-10, AIRPORT_POS.y-10, 20, 20), 2)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                planes.append(Plane(*event.pos))

        new_planes = []
        collided = set()

        # Kollisions-Check (Story: Kollision)
        for i, p1 in enumerate(planes):
            for j, p2 in enumerate(planes):
                if i < j and p1.pos.distance_to(p2.pos) < (p1.radius + p2.radius):
                    collided.add(i); collided.add(j)
                    score -= 50

        for i, plane in enumerate(planes):
            if i in collided: continue
            
            plane.update(planes)
            
            # Landung erfolgreich?
            if plane.pos.distance_to(AIRPORT_POS) < 10 and plane.state == "LANDING":
                score += 20
            else:
                plane.draw(screen)
                new_planes.append(plane)
        
        planes = new_planes

        # UI
        screen.blit(font.render(f"SCORE: {score} | TRAFFIC: {len(planes)}", True, (0, 255, 0)), (20, 20))
        screen.blit(font.render("ILS VECTOR ACTIVE", True, (0, 200, 0)), (RUNWAY_START.x, RUNWAY_START.y - 20))
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()