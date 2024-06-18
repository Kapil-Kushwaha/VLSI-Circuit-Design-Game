import pygame
import sys
import json
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 1500
screen_height = 800
icon_bar_height = 30

# Set up the display
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('VLSI CIRCUIT DESIGN')

# Load rectangle data from JSON file
with open('rectangles.json', 'r') as file:
    data = json.load(file)

# Extract rectangle data
rectangles = data["rectangles"]

# Colors
white = (255, 255, 255)
highlight_color = (255, 255, 0)  # Yellow highlight color
black = (0, 0, 0)  # Black for text
gray = (50, 50, 50)
drawing_color = (0, 0, 255)  # Blue color for new rectangles
button_color = (0, 255, 0)  # Green color for the button
icon_bar_color = (100, 0, 100)  # Purple color for icon bar
node_color = (255, 0, 0)  # Red color for sensor nodes

# Extended color palette (similar to MS Paint)
color_palette = [
    (0, 0, 0), (128, 128, 128), (192, 192, 192), (255, 255, 255), (255, 0, 0),
    (128, 0, 0), (255, 255, 0), (128, 128, 0), (0, 255, 0), (0, 128, 0),
    (0, 255, 255), (0, 128, 128), (0, 0, 255), (0, 0, 128), (255, 0, 255),
    (128, 0, 128), (255, 165, 0), (255, 192, 203), (160, 32, 240), (72, 61, 139)
]

# Variables to track the selected rectangle
selected_rect = None
offset_x = 0
offset_y = 0
resizing = False
rotating = False
rotate_handle_size = 8
resize_handle_size = 8
node_radius = 5

# Variables for drawing new rectangles
drawing = False
start_x = 0
start_y = 0
create_mode = False
color_change_mode = False

# Font for displaying coordinates
font_icon_bar = pygame.font.Font(None, 24)
font_grid = pygame.font.Font(None, 16)

# Function to display rectangle coordinates in X1, Y1, X2, Y2 format in icon bar
def display_rectangle_info(rect):
    x1, y1 = rect["x"], rect["y"]
    x2, y2 = x1 + rect["width"], y1 + rect["height"]
    coord_text = font_icon_bar.render(f'X1: {x1} Y1: {y1} X2: {x2} Y2: {y2}', True, white)
    screen.blit(coord_text, (200, 5))

# Function to draw grid
def draw_grid(screen, color, width, height, interval):
    for x in range(0, width, interval):
        pygame.draw.line(screen, color, (x, icon_bar_height), (x, height))
    for y in range(icon_bar_height, height, interval):
        pygame.draw.line(screen, color, (0, y), (width, y))

# Function to draw rectangles
def draw_rectangles():
    for rect_data in rectangles:
        x = rect_data["x"]
        y = rect_data["y"]
        width = rect_data["width"]
        height = rect_data["height"]
        color = tuple(rect_data["color"])
        angle = rect_data.get("angle", 0)
        draw_rotated_rect(screen, x, y, width, height, color, angle)
        draw_nodes(rect_data)
        if rect_data == selected_rect:
            # Draw the highlight around the selected rectangle
            pygame.draw.rect(screen, highlight_color, pygame.Rect(x-2, y-2, width+4, height+4), 2)
            # Draw resize handles
            draw_resize_handles(x, y, width, height, angle)
            # Draw rotate handle
            draw_rotate_handle(x, y, width, height, angle)

# Function to draw resize handles
def draw_resize_handles(x, y, width, height, angle):
    # Calculate rotated corners
    corners = [
        (x, y),
        (x + width, y),
        (x, y + height),
        (x + width, y + height)
    ]
    rotated_corners = [rotate_point(x + width / 2, y + height / 2, corner, angle) for corner in corners]
    for handle in rotated_corners:
        pygame.draw.rect(screen, highlight_color, pygame.Rect(handle[0] - resize_handle_size // 2, handle[1] - resize_handle_size // 2, resize_handle_size, resize_handle_size))

# Function to draw rotate handle
def draw_rotate_handle(x, y, width, height, angle):
    cx, cy = x + width / 2, y + height / 2
    handle_x = cx + (width / 2 + 20) * math.cos(math.radians(angle))
    handle_y = cy + (height / 2 + 20) * math.sin(math.radians(angle))
    pygame.draw.circle(screen, highlight_color, (int(handle_x), int(handle_y)), rotate_handle_size)

# Function to draw nodes
def draw_nodes(rect):
    cx, cy = rect["x"] + rect["width"] / 2, rect["y"] + rect["height"] / 2
    angle = rect.get("angle", 0)
    left_node = rotate_point(cx, cy, (rect["x"], rect["y"] + rect["height"] / 2), angle)
    right_node = rotate_point(cx, cy, (rect["x"] + rect["width"], rect["y"] + rect["height"] / 2), angle)
    pygame.draw.circle(screen, node_color, (int(left_node[0]), int(left_node[1])), node_radius)
    pygame.draw.circle(screen, node_color, (int(right_node[0]), int(right_node[1])), node_radius)

# Function to draw coordinates on the grid
def draw_coordinates(screen, color, width, height, interval, font):
    for x in range(0, width, interval):
        text = font.render(str(x), True, color)
        screen.blit(text, (x, icon_bar_height + 1))
    for y in range(icon_bar_height, height, interval):
        text = font.render(str(y), True, color)
        screen.blit(text, (0, y + 31))

# Function to draw the icon bar
def draw_icon_bar():
    pygame.draw.rect(screen, icon_bar_color, pygame.Rect(0, 0, screen_width, icon_bar_height))
    pygame.draw.rect(screen, button_color, pygame.Rect(5, 0, 80, 30), border_radius=5)
    text = font_icon_bar.render("NR", True, black)
    screen.blit(text, (15, 5))

    pygame.draw.rect(screen, button_color, pygame.Rect(90, 0, 80, 30), border_radius=5)
    text = font_icon_bar.render("Color", True, black)
    screen.blit(text, (100, 5))

    if selected_rect:
        display_rectangle_info(selected_rect)

# Check if the mouse is over a resize handle
def get_resize_handle(x, y, rect):
    handles = [
        pygame.Rect(rect["x"] - resize_handle_size // 2, rect["y"] - resize_handle_size // 2, resize_handle_size, resize_handle_size),
        pygame.Rect(rect["x"] + rect["width"] - resize_handle_size // 2, rect["y"] - resize_handle_size // 2, resize_handle_size, resize_handle_size),
        pygame.Rect(rect["x"] - resize_handle_size // 2, rect["y"] + rect["height"] - resize_handle_size // 2, resize_handle_size, resize_handle_size),
        pygame.Rect(rect["x"] + rect["width"] - resize_handle_size // 2, rect["y"] + rect["height"] - resize_handle_size // 2, resize_handle_size, resize_handle_size)
    ]
    for handle in handles:
        if handle.collidepoint(x, y):
            return handle
    return None

# Check if the mouse is over the rotate handle
def is_over_rotate_handle(x, y, rect):
    cx, cy = rect["x"] + rect["width"] / 2, rect["y"] + rect["height"] / 2
    handle_x = cx + (rect["width"] / 2 + 20) * math.cos(math.radians(rect.get("angle", 0)))
    handle_y = cy + (rect["height"] / 2 + 20) * math.sin(math.radians(rect.get("angle", 0)))
    return pygame.Rect(handle_x - rotate_handle_size, handle_y - rotate_handle_size, 2 * rotate_handle_size, 2 * rotate_handle_size).collidepoint(x, y)

# Function to draw a rotated rectangle
def draw_rotated_rect(surface, x, y, width, height, color, angle):
    rect = pygame.Surface((width, height), pygame.SRCALPHA)
    rect.fill(color)
    rotated_rect = pygame.transform.rotate(rect, angle)
    new_rect = rotated_rect.get_rect(center=(x + width / 2, y + height / 2))
    surface.blit(rotated_rect, new_rect.topleft)

# Function to rotate a point around a center
def rotate_point(cx, cy, p, angle):
    s = math.sin(math.radians(angle))
    c = math.cos(math.radians(angle))
    px, py = p
    px -= cx
    py -= cy
    xnew = px * c - py * s
    ynew = px * s + py * c
    return xnew + cx, ynew + cy

# Function to draw color palette
def draw_color_palette():
    x_offset = 180
    for color in color_palette:
        pygame.draw.rect(screen, color, pygame.Rect(x_offset, 0, 30, 30))
        x_offset += 35

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if pygame.Rect(5, 0, 80, 30).collidepoint(event.pos):
                    create_mode = not create_mode
                    color_change_mode = False
                elif pygame.Rect(90, 0, 80, 30).collidepoint(event.pos):
                    color_change_mode = not color_change_mode
                    create_mode = False
                elif create_mode:
                    if not drawing:
                        drawing = True
                        start_x, start_y = event.pos
                    else:
                        drawing = False
                        end_x, end_y = event.pos
                        width = abs(end_x - start_x)
                        height = abs(end_y - start_y)
                        new_rect = {
                            "x": min(start_x, end_x),
                            "y": min(start_y, end_y),
                            "width": width,
                            "height": height,
                            "color": [100, 50, 75],  # Default color for new rectangles
                            "angle": 0  # Default angle for new rectangles
                        }
                        rectangles.append(new_rect)
                        create_mode = False
                elif color_change_mode:
                    x_offset = 180
                    for color in color_palette:
                        if pygame.Rect(x_offset, 0, 30, 30).collidepoint(event.pos):
                            if selected_rect:
                                selected_rect["color"] = list(color)
                            color_change_mode = False
                            break
                        x_offset += 35
                else:  # Check if an existing rectangle is clicked
                    clicked_rect = None
                    for rect in rectangles:
                        cx, cy = rect["x"] + rect["width"] / 2, rect["y"] + rect["height"] / 2
                        rotated_point = rotate_point(cx, cy, event.pos, -rect.get("angle", 0))
                        rect_obj = pygame.Rect(rect["x"], rect["y"], rect["width"], rect["height"])
                        if rect_obj.collidepoint(rotated_point):
                            clicked_rect = rect
                            offset_x = rect["x"] - event.pos[0]
                            offset_y = rect["y"] - event.pos[1]
                            resizing = get_resize_handle(event.pos[0], event.pos[1], rect)
                            rotating = is_over_rotate_handle(event.pos[0], event.pos[1], rect)
                            break
                    if clicked_rect:
                        selected_rect = clicked_rect
                    else:
                        selected_rect = None
        elif event.type == pygame.MOUSEBUTTONUP:
            resizing = False
            rotating = False
        elif event.type == pygame.MOUSEMOTION:
            if selected_rect and pygame.mouse.get_pressed()[0]:
                if resizing:
                    selected_rect["width"] = max(10, event.pos[0] - selected_rect["x"])
                    selected_rect["height"] = max(10, event.pos[1] - selected_rect["y"])
                elif rotating:
                    cx, cy = selected_rect["x"] + selected_rect["width"] / 2, selected_rect["y"] + selected_rect["height"] / 2
                    dx, dy = event.pos[0] - cx, event.pos[1] - cy
                    angle = math.degrees(math.atan2(dy, dx)) + 90  # Adjust for correct rotation
                    selected_rect["angle"] = angle % 360  # Normalize angle between 0 and 360 degrees
                else:
                    selected_rect["x"] = event.pos[0] + offset_x
                    selected_rect["y"] = event.pos[1] + offset_y
        elif event.type == pygame.KEYDOWN:
            if selected_rect:
                if event.key == pygame.K_DELETE:
                    rectangles.remove(selected_rect)
                    selected_rect = None
                elif event.key == pygame.K_LEFT:
                    selected_rect["x"] -= 5
                elif event.key == pygame.K_RIGHT:
                    selected_rect["x"] += 5
                elif event.key == pygame.K_UP:
                    selected_rect["y"] -= 5
                elif event.key == pygame.K_DOWN:
                    selected_rect["y"] += 5

    # Fill the screen with white
    screen.fill(white)

    # Draw the icon bar
    draw_icon_bar()

    # Draw the grid and coordinates
    draw_grid(screen, gray, screen_width, screen_height, 20)
    draw_coordinates(screen, black, screen_width, screen_height, 20, font_grid)

    # Draw the rectangles from JSON data
    draw_rectangles()

    # Draw the currently drawing rectangle
    if drawing:
        end_x, end_y = pygame.mouse.get_pos()
        width = abs(end_x - start_x)
        height = abs(end_y - start_y)
        pygame.draw.rect(screen, drawing_color, pygame.Rect(min(start_x, end_x), min(start_y, end_y), width, height), 1)

    # Draw the color palette if in color change mode
    if color_change_mode:
        draw_color_palette()

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
