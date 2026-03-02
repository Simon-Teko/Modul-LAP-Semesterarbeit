import pygame
import random
import math

#=========================================================
# Variablen
#=========================================================

# Spielfeld
WIDTH, HEIGHT = 1200, 1000

# Tick Speed
FPS = 30

# Farben
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

# Wegpunkte für die Platzrunde (Traffic Circuit)
WAYPOINTS = {
    "Downwind": (300, 400),
    "Base": (900, 400),
    "Final": (900, 700),
    "Airport": (550, 700)
}
# Wegpunkte Reihenfolge
WAYPOINT_ORDER = ["Downwind", "Base", "Final", "Airport"]

#=========================================================
# Aircraft
#=========================================================

class Aircraft:
    def __init__(self, x, y): # Initialisierung eines Flugzeugs
        self.x = x # Koordinate X
        self.y = y # Koordinate Y
        self.speed = random.uniform(1.5, 3.5) # Geschwindigkeit (Zufällig)
        self.altitude = random.randrange(6000, 10001, 10) # Höhe in Fuss (Zufällig + durch 10 Teilbar)
        self.target_wp_index = 0 # Kurs / Ziel --> Waypoint
        self.state = "cruising" # Status
        self.collision_avoidance = False # Kollisionserkennung

    def get_target(self): # Waypoint
        if self.target_wp_index < len(WAYPOINT_ORDER): # überprüfen ob bereits alle Waypoints abgearbetet wurden
            return WAYPOINTS[WAYPOINT_ORDER[self.target_wp_index]] # nächsten Waypoint auslesen
        return None

    def update(self, all_aircrafts): 
        # Kollisionsprüfung
        self.collision_avoidance = False
        for other in all_aircrafts: 
            if other != self:
                dist = math.hypot(self.x - other.x, self.y - other.y)
                alt_diff = abs(self.altitude - other.altitude)
                
                # Check sight line < 250 pixels and altitude +- 100 feet
                if dist < 250 and alt_diff <= 100:
                    self.collision_avoidance = True
                    # Ausweichen durch Höhenänderung
                    if self.altitude >= other.altitude: # Wenn hörer als Gegner --> Steigen 
                        self.altitude += 50
                    else:
                        self.altitude -= 50

        # Navigation
        target = self.get_target() # Nächster Waypoint auslesen
        if not target:
            return # Ziel erreicht (gelandet)

        tx, ty = target
        dist_to_target = math.hypot(tx - self.x, ty - self.y) # Distanz zum nächsten Waypoint berechnen

        # Ist Flugzeug im Radius von 5 Pixeln zum Wegpunkt?
        if dist_to_target < 5:
            self.target_wp_index += 1 # Kurs zum nächsten Waypoint
            target = self.get_target()
            if not target:
                return
            tx, ty = target

        # Höhenanpassung zum Wegpunkt (Sinkflug simulieren)
        goal_altitude = 4500 - (self.target_wp_index * 1500) # Simulierter Glide Slope
        if self.altitude > goal_altitude:
            self.altitude -= 10
        elif self.altitude < goal_altitude:
            self.altitude += 10

        # Kurs berechnen und bewegen
        angle = math.atan2(ty - self.y, tx - self.x)
        
        # In Approach State? (Wenn auf "Final")
        if WAYPOINT_ORDER[self.target_wp_index] == "Final" or WAYPOINT_ORDER[self.target_wp_index] == "Airport":
            move_speed = 2 # Feste Approach Speed simulieren (8 Pixel entspräche hier einem sehr großen Sprung)
        else:
            move_speed = self.speed

        self.x += math.cos(angle) * move_speed
        self.y += math.sin(angle) * move_speed

    def draw(self, screen):
        pygame.draw.circle(screen, RED if self.collision_avoidance else BLUE, (int(self.x), int(self.y)), 5)
        # Höhe als Text anzeigen
        font = pygame.font.SysFont(None, 20)
        alt_text = font.render(f"{int(self.altitude)} ft", True, BLACK)
        screen.blit(alt_text, (int(self.x) + 10, int(self.y) - 10))



#=========================================================
# Main
#=========================================================



def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("ATC Simulator")
    clock = pygame.time.Clock()

    # Scoreboard
    score = 0
    font_large = pygame.font.SysFont(None, 36)

    # Flugzeuge generieren (Startwert)
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
            # Flugzeuge per Mausklick generieren
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

        
        #=========================================================
        # Zeichnen / Darstellung
        #=========================================================
        
        # Drawing
        screen.fill(WHITE)

        # Spielfeld und Flughafen zeichnen
        pygame.draw.rect(screen, GRAY, (WAYPOINTS["Airport"][0]-20, WAYPOINTS["Airport"][1]-10, 120, 20))
        
        # Waypoints zeichnen (zur Visualisierung)
        for name, pos in WAYPOINTS.items():
            pygame.draw.circle(screen, GREEN, pos, 5)
            wp_text = font_large.render(name, True, GREEN)
            screen.blit(wp_text, (pos[0] + 10, pos[1] + 10))

        # Flugzeuge zeichnen
        for ac in aircrafts:
            ac.draw(screen)

        # Scoreboard zeichnen
        score_text = font_large.render(f"Score: {score} | Flugzeuge: {len(aircrafts)}", True, BLACK)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main() # Start