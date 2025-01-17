import pygame
import numpy as np
import random

# Dimensions de la fenêtre
WIDTH, HEIGHT = 800, 600

# Dimensions du but
goal_width = 500
goal_height = 200
goal_x = WIDTH // 2 - goal_width // 2
goal_y = 100

gk_x = 325
gk_y = 300

# Couleurs
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 128, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)

# Ballon
ball_radius = 15
ball_start_pos = np.array([WIDTH // 2, HEIGHT - 50])  # Position initiale du ballon
ball_pos = ball_start_pos.copy()

# Point B (cible)
target_pos = np.array([WIDTH // 2, goal_y + goal_height // 2])

# Point de contrôle pour l'effet
control_point = np.array([WIDTH // 2, HEIGHT // 2])

# Gardien
goalkeeper_pos = np.array([WIDTH // 2, goal_y + goal_height // 2])
goalkeeper_width = 60
goalkeeper_height = 10
goalkeeper_head_radius = 20

# Initialisation de Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Penalty Game")
clock = pygame.time.Clock()

# Variables globales
x_choice = goal_x + goal_width // 2  # Position horizontale cible (au milieu du but)
x_direction = 5  # Direction du curseur

y_choice = goal_y + goal_height // 2  # Position verticale cible (au centre du but)
y_direction = 5  # Direction verticale

# Effet
effect = 0  # Valeur de l'effet (-1: extérieur, 1: intérieur)
effect_direction = 1  # Direction de l'effet

# Puissance
power = 0  # Valeur de la puissance (0-100)
power_direction = 1  # Direction du curseur de puissance

# Animation du tir
t = 0  # Temps pour la courbe de Bézier
trajectory_control_point = None  # Point de contrôle figé pour la trajectoire
trajectory_end_point = None  # Point de fin figé pour la trajectoire

state = "choosing_x"  # État du jeu
space_released = True  # Vérifie si la barre espace a été relâchée

# Fonction pour calculer une courbe de Bézier quadratique
def bezier_quadratic(t, P0, P1, P2):
    return (1 - t)**2 * P0 + 2 * (1 - t) * t * P1 + t**2 * P2

# Fonction pour dessiner le terrain et les objets
def draw():
    # Dessiner le terrain (pelouse)
    screen.fill(GREEN)

    # Dessiner le but
    pygame.draw.rect(screen, WHITE, (goal_x, goal_y, goal_width, goal_height), 5)

    # Ligne sortie de but
    pygame.draw.line(screen, WHITE, (0, 300), (800, 300), 5)

    # Ligne de la surface de but en tant que trapèze pour donner l'effet 2D
    pygame.draw.line(screen, WHITE, (60, 300), (20, 400), 5)
    pygame.draw.line(screen, WHITE, (20, 400), (780, 400), 5)
    pygame.draw.line(screen, WHITE, (780, 400), (720, 300), 5)

    # Dessiner le ballon
    ball_image = pygame.image.load("C:/Users/1000r/OneDrive/Documents/mini_jeu/jeu/ballon.png").convert()
    ball_image.set_colorkey((255, 255, 255))
    ball_image = pygame.transform.scale(ball_image, (ball_radius * 2, ball_radius * 2))  # Redimensionner à la taille du rayon
    screen.blit(ball_image, (ball_pos[0] - ball_radius, ball_pos[1] - ball_radius))

    # Dessiner le gardien
    goalkeeper = pygame.image.load("C:/Users/1000r/OneDrive/Documents/mini_jeu/jeu/man.webp")
    goalkeeper = pygame.transform.scale(goalkeeper, (150, 170))
    screen.blit(goalkeeper, (gk_x, 130))

    # Dessiner le point rouge pour choisir la trajectoire
    pygame.draw.circle(screen, RED, (x_choice, y_choice), 8)

    # Dessiner la courbe de Bézier visible au début et pendant le tir
    if trajectory_control_point is None or trajectory_end_point is None:
        temp_control_point = control_point + np.array([effect * 200, 0])
        temp_end_point = np.array([x_choice, y_choice])
    else:
        temp_control_point = trajectory_control_point
        temp_end_point = trajectory_end_point

    for t_local in np.linspace(0, 1, 50):
        point = bezier_quadratic(t_local, ball_start_pos, temp_control_point, temp_end_point)
        pygame.draw.circle(screen, BLACK, point.astype(int), 2)

    # Dessiner la barre de puissance
    pygame.draw.rect(screen, WHITE, (50, 550, 200, 20))  # Contour de la barre
    for i in range(200):
        if i < 100:
            color = (255, i * 2, 0)  # Dégradé de rouge à orange
        else:
            color = (255 - (i - 100) * 2, 255, 0)  # Dégradé de orange à vert
        pygame.draw.line(screen, color, (50 + i, 550), (50 + i, 570))
    pygame.draw.line(screen, RED, (50 + int(power * 2), 550), (50 + int(power * 2), 570), 3)  # Curseur rouge

    # Texte pour indiquer l'état
    font = pygame.font.Font(None, 36)
    text = font.render(f"État: {state}", True, WHITE)
    screen.blit(text, (10, 10))

# Mise à jour des choix utilisateur
def update_choices():
    global x_choice, x_direction, y_choice, y_direction, effect, effect_direction, power, power_direction, state, space_released, t, ball_pos, trajectory_control_point, trajectory_end_point

    keys = pygame.key.get_pressed()

    if state == "choosing_x":
        # Déplacer le curseur horizontalement
        x_choice += x_direction
        if x_choice <= goal_x or x_choice >= goal_x + goal_width:
            x_direction *= -1  # Inverser la direction si on atteint les limites

        # Vérifier si le joueur relâche ESPACE pour valider
        if not keys[pygame.K_SPACE]:
            space_released = True
        elif keys[pygame.K_SPACE] and space_released:
            space_released = False
            state = "choosing_y"

    elif state == "choosing_y":
        # Déplacer le curseur verticalement
        y_choice += y_direction
        if y_choice <= goal_y or y_choice >= goal_y + goal_height:
            y_direction *= -1  # Inverser la direction si on atteint les limites

        # Vérifier si le joueur relâche ESPACE pour valider
        if not keys[pygame.K_SPACE]:
            space_released = True
        elif keys[pygame.K_SPACE] and space_released:
            space_released = False
            state = "choosing_effect"

    elif state == "choosing_effect":
        # Déplacer la ligne pour l'effet
        effect += effect_direction * 0.1
        if effect <= -1 or effect >= 1:
            effect_direction *= -1  # Inverser la direction si on atteint les limites

        # Vérifier si le joueur relâche ESPACE pour valider
        if not keys[pygame.K_SPACE]:
            space_released = True
        elif keys[pygame.K_SPACE] and space_released:
            space_released = False
            state = "choosing_power"

    elif state == "choosing_power":
        # Déplacer le curseur de puissance
        power += power_direction * 1
        if power <= 0 or power >= 100:
            power_direction *= -1  # Inverser la direction si on atteint les limites

        # Vérifier si le joueur relâche ESPACE pour effectuer le tir
        if not keys[pygame.K_SPACE]:
            space_released = True
        elif keys[pygame.K_SPACE] and space_released:
            space_released = False
            # Fixer les points de contrôle pour la trajectoire
            trajectory_control_point = control_point + np.array([effect * 200, 0])
            trajectory_end_point = np.array([x_choice, y_choice])
            t = 0  # Réinitialiser le temps d'animation
            state = "shooting"

    elif state == "shooting":
        # Animer la trajectoire de la balle
        t += 0.05 * (power / 100)  # Ajuster la vitesse avec la puissance
        if t <= 1:
            ball_pos[:] = bezier_quadratic(t, ball_start_pos, trajectory_control_point, trajectory_end_point)
        else:
            state = "done"

# Boucle principale
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    update_choices()
    draw()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
