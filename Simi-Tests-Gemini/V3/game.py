import pygame
import random
import math

FLUGZEUG_TYPEN = {
    "Kleinflugzeug": {"speed": (2.0, 3.0), "radius": 12, "holding_dist": 40, "color": (100, 200, 255)},
    "Passagierjet": {"speed": (1.2, 1.8), "radius": 20, "holding_dist": 70, "color": (50, 50, 200)},
    "Frachter": {"speed": (0.8, 1.2), "radius": 25, "holding_dist": 100, "color": (150, 150, 150)}
}

# --- Konfiguration ---
WIDTH, HEIGHT = 900, 700
FPS = 60
AIRPORT_POS = [WIDTH // 2, HEIGHT // 2]
LANDING_ENTRY = [WIDTH // 2, HEIGHT // 2 + 180]

# --- Logik-Funktionen ---

def erstelle_flugzeug(x, y, typ=None):
    """Erstellt ein Flugzeug basierend auf den Typen im 'JSON'."""
    if not typ:
        typ = random.choice(list(FLUGZEUG_TYPEN.keys()))
    
    daten = FLUGZEUG_TYPEN[typ]
    speed = random.uniform(daten["speed"][0], daten["speed"][1])
    
    return {
        "pos": [float(x), float(y)],
        "speed": speed,
        "radius": daten["radius"],
        "holding_dist": daten["holding_dist"],
        "color": daten["color"],
        "state": "APPROACHING",
        "angle": random.uniform(0, 2 * math.pi),
        "typ": typ
    }

def bewege_flugzeug(f, bahn_besetzt):
    """Steuert die Flugphasen."""
    dx_e = LANDING_ENTRY[0] - f["pos"][0]
    dy_e = LANDING_ENTRY[1] - f["pos"][1]
    dist_entry = math.sqrt(dx_e**2 + dy_e**2)

    # Logik für Zustandswechsel
    if f["state"] == "APPROACHING" and dist_entry < 15:
        f["state"] = "HOLDING" if bahn_besetzt else "LANDING"
    
    if f["state"] == "HOLDING" and not bahn_besetzt:
        f["state"] = "LANDING"

    # Bewegung ausführen
    if f["state"] == "HOLDING":
        f["angle"] += (f["speed"] * 0.01) # Geschwindigkeit im Kreis
        f["pos"][0] = LANDING_ENTRY[0] + math.cos(f["angle"]) * f["holding_dist"]
        f["pos"][1] = LANDING_ENTRY[1] + math.sin(f["angle"]) * f["holding_dist"]
    else:
        target = AIRPORT_POS if f["state"] == "LANDING" else LANDING_ENTRY
        dx = target[0] - f["pos"][0]
        dy = target[1] - f["pos"][1]
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 0:
            f["pos"][0] += (dx / dist) * f["speed"]
            f["pos"][1] += (dy / dist) * f["speed"]

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Courier", 20, bold=True)
    
    flugzeuge = []
    score = 0

    running = True
    while running:
        screen.fill((245, 245, 245))
        bahn_besetzt = any(f["state"] == "LANDING" for f in flugzeuge)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                flugzeuge.append(erstelle_flugzeug(mx, my))

        # Visualisierung Bodenstationen
        pygame.draw.rect(screen, (50, 50, 50), (AIRPORT_POS[0]-30, AIRPORT_POS[1]-10, 60, 20)) # Landebahn
        pygame.draw.circle(screen, (200, 200, 200), LANDING_ENTRY, 5, 0) # ILS Sender

        # Flugzeuge Loop
        for f in flugzeuge[:]:
            bewege_flugzeug(f, bahn_besetzt)
            
            # Zeichnen: Kreis + Typ-Text
            pygame.draw.circle(screen, f["color"], (int(f["pos"][0]), int(f["pos"][1])), f["radius"], 2)
            label = font.render(f["typ"][0], True, (100, 100, 100))
            screen.blit(label, (f["pos"][0]-5, f["pos"][1]-10))

            # Score bei Landung
            dist_airp = math.sqrt((f["pos"][0]-AIRPORT_POS[0])**2 + (f["pos"][1]-AIRPORT_POS[1])**2)
            if f["state"] == "LANDING" and dist_airp < 5:
                score += 10
                flugzeuge.remove(f)
                continue

            # Kollision: Sie dürfen sich am Rand berühren!
            # Kollision erst, wenn Distanz < (Radius1 + Radius2) * 0.6 (Überlappung erlaubt)
            for andere in flugzeuge:
                if f != andere:
                    d = math.sqrt((f["pos"][0]-andere["pos"][0])**2 + (f["pos"][1]-andere["pos"][1])**2)
                    if d < (f["radius"] + andere["radius"]) * 0.5: # Harte Kollision im Kern
                        score -= 50
                        if f in flugzeuge: flugzeuge.remove(f)
                        if andere in flugzeuge: flugzeuge.remove(andere)
                        break

        # UI Scoreboard
        score_surf = font.render(f"SCORE: {score}", True, (200, 0, 0))
        screen.blit(score_surf, (20, 20))
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()