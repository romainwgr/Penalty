import pygame
import numpy as np
import random

WIDTH, HEIGHT = 800, 600

# Dimensions du but
goal_width = 500
goal_height = 200
goal_x = WIDTH // 2 - goal_width // 2
goal_y = 100


# Couleurs
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN_TERRAIN = (0, 122, 0)
GREEN = (0,255,0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)


# Initialisation de Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Penalty")
clock = pygame.time.Clock()

def initialize_game():
    """Initialize global variables for the game."""
    global ball_pos, trajectory_control_point, trajectory_end_point, t, control_point, ball_radius, ball_start_pos
    global x_choice, x_direction, y_choice, y_direction
    global effect, effect_direction, power, power_direction
    global goalkeeper_pos, state, space_released, score, goalkeeper_width

    # Ball position
    ball_start_pos = np.array([WIDTH // 2, HEIGHT - 50]) 
    ball_pos = ball_start_pos.copy()
    ball_radius = 15
    trajectory_control_point = None
    trajectory_end_point = None
    control_point = np.array([WIDTH // 2, HEIGHT // 2])
    t = 0  # Time for Bézier curve animation



    # Player choices
    x_choice = goal_x + goal_width // 2
    x_direction = 5  # Direction for horizontal choice
    y_choice = goal_y + goal_height // 2
    y_direction = 5  # Direction for vertical choice

    # Effect and power
    effect = 0
    effect_direction = 1  # Effect direction (-1 to 1)
    power = 0
    power_direction = 1  # Power increase direction

    # Goalkeeper position
    goalkeeper_pos = np.array([WIDTH // 2, goal_y + goal_height // 2])
    goalkeeper_width = 60

    # Game state
    state = "x"
    space_released = True
    score = 0  # Initial score

    



# Fonction pour calculer la courbe de Bézier quadratique selon l'effet de la balle
def bezier_quadratic(t, P0, P1, P2):
    return (1 - t)**2 * P0 + 2 * (1 - t) * t * P1 + t**2 * P2

# Fonction pour dessiner le terrain et les objets
def draw():
    # Dessiner la pelouse
    screen.fill(GREEN_TERRAIN)

    # Dessiner le but
    pygame.draw.rect(screen, WHITE, (goal_x, goal_y, goal_width, goal_height), 5)

    # Ligne sortie de but
    pygame.draw.line(screen, WHITE, (0, 300), (800, 300), 5)

    # Ligne de la surface de but en tant que trapèze pour donner l'effet 2D
    pygame.draw.line(screen, WHITE, (60, 300), (20, 400), 5)
    pygame.draw.line(screen, WHITE, (20, 400), (780, 400), 5)
    pygame.draw.line(screen, WHITE, (780, 400), (720, 300), 5)

    # ballon
    ball_image = pygame.image.load("ballon.png").convert()
    ball_image.set_colorkey((255, 255, 255))
    ball_image = pygame.transform.scale(ball_image, (ball_radius * 2, ball_radius * 2))  # Redimensionner à la taille du rayon
    screen.blit(ball_image, (ball_pos[0] - ball_radius, ball_pos[1] - ball_radius))

    # gardien
    goalkeeper = pygame.image.load("man.webp")
    goalkeeper = pygame.transform.scale(goalkeeper, (150, 170))
    screen.blit(goalkeeper, (goalkeeper_pos[0] - 75, goalkeeper_pos[1] - 85))
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

    # barre de puissance avec un degradé 
    pygame.draw.rect(screen, WHITE, (50, 550, 200, 20))  
    for i in range(200):
        if i<100:  # Rouge  Orange
            r= 255
            g= i * 165 // 100  
            b= 0
        else:  # Orange  Vert
            r= 255 - (i - 100) * 255 // 100  
            g= 165 + (i - 100) * 90 // 100  
            b= 0

        color =(r, g, b)
        pygame.draw.line(screen, color, (50 + i, 550), (50 + i, 570))

    pygame.draw.line(screen, BLACK, (50 + int(power * 2), 550), (50 + int(power * 2), 570), 3)  # Curseur 

    # Texte pour indiquer l'état
    font = pygame.font.Font(None, 36)
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (10, 10))

# Mise à jour des choix utilisateur
def update_choices():
    global x_choice, x_direction, y_choice, y_direction, effect, effect_direction, power, power_direction, state, space_released, t, ball_pos, trajectory_control_point, trajectory_end_point

    keys = pygame.key.get_pressed()

    if state == "x":
        # Déplacer le curseur horizontalement
        x_choice += x_direction
        if x_choice <= goal_x or x_choice >= goal_x + goal_width:
            x_direction *= -1  # Inverser la direction si on atteint les limites

        # Vérifier si le joueur relâche ESPACE pour valider
        if not keys[pygame.K_SPACE]:
            space_released = True
        elif keys[pygame.K_SPACE] and space_released:
            space_released = False
            state = "y"

    elif state == "y":
        # Déplacer le curseur verticalement
        y_choice += y_direction
        if y_choice <= goal_y or y_choice >= goal_y + goal_height:
            y_direction *= -1  # Inverser la direction si on atteint les limites

        # Vérifier si le joueur relâche ESPACE pour valider
        if not keys[pygame.K_SPACE]:
            space_released = True
        elif keys[pygame.K_SPACE] and space_released:
            space_released = False
            state = "effet"

    elif state == "effet":
        # Déplacer la ligne pour l'effet
        effect += effect_direction * 0.1
        if effect <= -1 or effect >= 1:
            effect_direction *= -1  

        # Vérifier si le joueur relâche ESPACE pour valider
        if not keys[pygame.K_SPACE]:
            space_released = True
        elif keys[pygame.K_SPACE] and space_released:
            space_released = False
            state = "force"

    elif state == "force":
        power += power_direction * 1
        if power <= 0 or power >= 100:
            power_direction *= -1  

        if not keys[pygame.K_SPACE]:
            space_released = True
        elif keys[pygame.K_SPACE] and space_released:
            space_released = False
            trajectory_control_point = control_point + np.array([effect * 200, 0])
            trajectory_end_point = np.array([x_choice, y_choice])
            t = 0  
            state = "tir"
            random_gk_position()  


    elif state == "tir":
        t += 0.05 * (power / 100) 
        if t <= 1:
            ball_pos[:] = bezier_quadratic(t, ball_start_pos, trajectory_control_point, trajectory_end_point)
        else:
            state = "fini"
    elif state == "fini":
        check_goal()  

def random_gk_position():
    global goalkeeper_pos
    goalkeeper_pos[0] = random.randint(goal_x, goal_x + goal_width - goalkeeper_width)


def reset_game():
    global ball_pos, trajectory_control_point, trajectory_end_point, t, x_choice, y_choice, effect, power, goalkeeper_pos
    ball_pos = ball_start_pos.copy() 
    trajectory_control_point = None
    trajectory_end_point = None
    t = 0  
    x_choice = goal_x + goal_width // 2  
    y_choice = goal_y + goal_height // 2  
    effect = 0 
    power = 1  
    goalkeeper_pos = np.array([WIDTH // 2, goal_y + goal_height // 2])


def check_goal():
    global score, state
    if abs(ball_pos[0] - goalkeeper_pos[0]) < goalkeeper_width // 2 +50:
        score =0
        print("Raté ! Le gardien a arrêté le penalty.")
    else:
        score += 1
        print("But ! Score :", score)
    state = "x" 
    reset_game()  



initialize_game()

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
