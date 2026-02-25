import pygame
import random
import math

# --- KONSTANTEN ---
WIDTH, HEIGHT = 800, 600
FPS = 30

# Farben
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

# Wegpunkte für die Platzrunde (Traffic Circuit) - 
# Reihenfolge: Downwind -> Base -> Final -> Airport
WAYPOINTS = {
    "Downwind": (200, 100),
    "Base": (600, 100),
    "Final": (600, 400),
    "Airport": (400, 400)
}
WAYPOINT_ORDER = ["Downwind", "Base", "Final", "Airport"]

class Aircraft:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = random.uniform(1.5, 3.5) # Story 1.1.1: Zufällige Geschwindigkeiten
        self.altitude = random.randint(3000, 8000)
        self.target_wp_index = 0
        self.state = "cruising"
        self.collision_avoidance = False

    def get_target(self):
        if self.target_wp_index < len(WAYPOINT_ORDER):
            return WAYPOINTS[WAYPOINT_ORDER[self.target_wp_index]]
        return None

    def update(self, all_aircrafts):
        # --- Kollisionsprüfung (PAP Seite 5) --- 
        self.collision_avoidance = False
        for other in all_aircrafts:
            if other != self:
                dist = math.hypot(self.x - other.x, self.y - other.y)
                alt_diff = abs(self.altitude - other.altitude)
                
                # Check sight line < 250 pixels and altitude +- 100 feet [cite: 47, 50]
                if dist < 250 and alt_diff <= 100:
                    self.collision_avoidance = True
                    # Ausweichen durch Höhenänderung [cite: 55]
                    if self.altitude >= other.altitude:
                        self.altitude += 50
                    else:
                        self.altitude -= 50

        # --- Navigation (PAP Seite 7) --- [cite: 35]
        target = self.get_target()
        if not target:
            return # Ziel erreicht (gelandet)

        tx, ty = target
        dist_to_target = math.hypot(tx - self.x, ty - self.y)

        # Ist Flugzeug im Radius von 50 Pixeln zum Wegpunkt? [cite: 61]
        if dist_to_target < 50:
            self.target_wp_index += 1 # Set course to next waypoint [cite: 69]
            target = self.get_target()
            if not target:
                return
            tx, ty = target

        # Höhenanpassung zum Wegpunkt (Sinkflug simulieren) [cite: 65, 72]
        goal_altitude = 5000 - (self.target_wp_index * 1500) # Simulierter Glide Slope
        if self.altitude > goal_altitude:
            self.altitude -= 25 # [cite: 71]
        elif self.altitude < goal_altitude:
            self.altitude += 25 # [cite: 74]

        # Kurs berechnen und bewegen [cite: 75, 78]
        angle = math.atan2(ty - self.y, tx - self.x)
        
        # In Approach State? (Wenn auf "Final") [cite: 76]
        if WAYPOINT_ORDER[self.target_wp_index] == "Final" or WAYPOINT_ORDER[self.target_wp_index] == "Airport":
            move_speed = 2 # Feste Approach Speed simulieren (8 Pixel entspräche hier einem sehr großen Sprung) [cite: 81]
        else:
            move_speed = self.speed

        self.x += math.cos(angle) * move_speed
        self.y += math.sin(angle) * move_speed

    def draw(self, screen):
        pygame.draw.circle(screen, RED if self.collision_avoidance else BLUE, (int(self.x), int(self.y)), 5)
        # Höhe als Text anzeigen [cite: 24, 25]
        font = pygame.font.SysFont(None, 20)
        alt_text = font.render(f"{int(self.altitude)} ft", True, BLACK)
        screen.blit(alt_text, (int(self.x) + 10, int(self.y) - 10))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("ATC Simulator")
    clock = pygame.time.Clock()

    # Scoreboard [cite: 5]
    score = 0
    font_large = pygame.font.SysFont(None, 36)

    # Flugzeuge generieren (Startwert) [cite: 21, 23]
    aircrafts = []
    initial_aircraft_count = 5 
    for _ in range(initial_aircraft_count):
        aircrafts.append(Aircraft(random.randint(0, 300), random.randint(0, 500)))

    running = True
    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Story 1.1.2: Eigene Flugzeuge per Mausklick
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                aircrafts.append(Aircraft(mx, my))

        # Update Logic
        to_remove = []
        for ac in aircrafts:
            ac.update(aircrafts)
            
            # Überprüfen ob gelandet (Ziel erreicht)
            if ac.target_wp_index >= len(WAYPOINT_ORDER):
                to_remove.append(ac)
                score += 10 # Punkte für erfolgreiche Landung

        # Story 1.1.5: Hard Collision Check (Absturz, wenn an derselben Stelle)
        for i, ac1 in enumerate(aircrafts):
            for j, ac2 in enumerate(aircrafts):
                if i < j and ac1 not in to_remove and ac2 not in to_remove:
                    dist = math.hypot(ac1.x - ac2.x, ac1.y - ac2.y)
                    alt_diff = abs(ac1.altitude - ac2.altitude)
                    if dist < 10 and alt_diff < 50: # Harte Kollision
                        to_remove.extend([ac1, ac2])
                        score -= 50 # Punktabzug bei Crash

        for ac in set(to_remove):
            if ac in aircrafts:
                aircrafts.remove(ac)

        # Drawing
        screen.fill(WHITE)

        # Spielfeld und Flughafen zeichnen [cite: 12]
        pygame.draw.rect(screen, GRAY, (WAYPOINTS["Airport"][0]-20, WAYPOINTS["Airport"][1]-10, 40, 20))
        
        # Waypoints zeichnen (zur Visualisierung)
        for name, pos in WAYPOINTS.items():
            pygame.draw.circle(screen, GREEN, pos, 5)
            wp_text = font_large.render(name, True, GREEN)
            screen.blit(wp_text, (pos[0] + 10, pos[1] + 10))

        # Flugzeuge zeichnen [cite: 22]
        for ac in aircrafts:
            ac.draw(screen)

        # Scoreboard zeichnen [cite: 5, 26]
        score_text = font_large.render(f"Score: {score} | Flugzeuge: {len(aircrafts)}", True, BLACK)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main() # Start [cite: 1, 15]