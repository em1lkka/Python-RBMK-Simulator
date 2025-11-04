import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RBMK Simulator")
clock = pygame.time.Clock()

#variables
power = 0.8
temperature = 0.3
coolant_pump = 0.5
xenon = 0.0
reactivity = 0.0


#rods
rods = [0.0 for _ in range(9)]
rod_targets = [False for _ in range(9)]

def draw_bar(x, value, color, label):
    bar_height = int(value * 200)
    pygame.draw.rect(screen, color, (x, HEIGHT - bar_height - 50, 50, bar_height))
    font = pygame.font.Font(None, 24)
    if label == "Temp":
        real_temp = 200 + value * 600
        text = font.render(f"{label}: {real_temp:.0f}°C", True, (200, 200, 200))
    else:
        text = font.render(f"{label}: {value*100:.0f}%", True, (200, 200, 200))

    screen.blit(text, (x - 15, HEIGHT - 30))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            # Toggle control rods 1–9
            for i in range(9):
                key = getattr(pygame, f"K_{i + 1}")
                if event.key == key:
                    rod_targets[i] = not rod_targets[i]

    keys = pygame.key.get_pressed()

    #LEFT/RIGHT coolant setting steering
    if keys[pygame.K_RIGHT] and coolant_pump < 1.0:
        coolant_pump += 0.01
        pygame.time.wait(10)

    if keys[pygame.K_LEFT] and coolant_pump > 0.0:
        coolant_pump -= 0.01
        pygame.time.wait(10)

    for i in range(9):
        key = getattr(pygame, f"K_{i + 1}")  # K_1 ... K_9
        if keys[key]:
            rods[i] = min(1.0, rods[i] + 0.02)
        else:
            rods[i] = max(0.0, rods[i] - 0.005)


    # Temperature follows power, cooled by pump
    temperature += (power - temperature) * 0.02
    temperature -= coolant_pump * 0.005
    temperature = max(0.0, min(temperature, 1.0))

    # Control rods and coolant affect reactivity
    rod_effect = sum(rods) / len(rods)
    void_fraction = 1.0 - coolant_pump  # less coolant -> more voids
    reactivity = 0.5 - rod_effect * 0.5 + void_fraction * 0.4  # RBMK quirk!

    # Apply xenon poisoning (reduces reactivity)
    reactivity -= xenon * 0.6

    # Power moves toward reactivity gradually
    power += (reactivity - power) * 0.01
    power = max(0.0, min(power, 1.5))  # allow some overshoot

    # Xenon buildup: more at high power, decays at low power
    xenon += power * 0.0003 - xenon * 0.001
    xenon = max(0.0, min(xenon, 1.0))

    # 3. Draw everything
    screen.fill((30, 30, 30))

    draw_bar(100, power, (255, 150, 0), "Power")
    draw_bar(250, temperature, (255, 0, 0), "Temp")
    draw_bar(400, coolant_pump, (0, 150, 255), "Coolant")
    draw_bar(550, xenon, (150, 0, 200), "Xenon")

    rod_width = 40
    rod_height_max = 100
    for i in range(9):
        if rod_targets[i]:
            rods[i] = min(1.0, rods[i] + 0.02)  # insert
        else:
            rods[i] = max(0.0, rods[i] - 0.02)  # withdraw

    for i, pos in enumerate(rods):
        rod_height = int(pos * rod_height_max)
        x = 50 + i * (rod_width + 5)
        y = HEIGHT - 250
        pygame.draw.rect(screen, (100, 100, 100), (x, y - rod_height, rod_width, rod_height))
        font = pygame.font.Font(None, 20)
        num = font.render(str(i + 1), True, (200, 200, 200))
        screen.blit(num, (x + 10, y + 5))

    pygame.display.flip()
    clock.tick(60)