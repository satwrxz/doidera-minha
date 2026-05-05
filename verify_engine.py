import os
import json
import pygame

# Mock pygame for headless environment
os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()
pygame.display.set_mode((1, 1))

from scft import Game, build_level

def test_persistence():
    print("Testing persistence...")
    if os.path.exists("save_data.json"):
        os.remove("save_data.json")

    g = Game()
    g.unlocked = 3
    g.souls = 150
    g.health_upgrades = 2
    g.difficulty = 1.5
    g._save_data()

    if not os.path.exists("save_data.json"):
        raise Exception("save_data.json not created")

    g2 = Game()
    if g2.unlocked != 3 or g2.souls != 150 or g2.health_upgrades != 2 or g2.difficulty != 1.5:
        raise Exception(f"Persistence failed: {g2.unlocked}, {g2.souls}, {g2.health_upgrades}, {g2.difficulty}")
    print("Persistence: OK")

def test_levels():
    print("Testing level layouts...")
    levels = [
        (1, 4000, (3850, 474)),
        (2, 4500, (4350, 514)),
        (3, 4800, (4650, 494)),
        (4, 5200, (5050, 464)),
        (5, 4000, (3880, 484))
    ]

    for lv_id, expected_w, goal_pos in levels:
        res = build_level(lv_id)
        world_w = res[8]
        goal = res[4]
        if world_w != expected_w:
            raise Exception(f"Level {lv_id} width mismatch: {world_w} != {expected_w}")
        if (goal.rect.x, goal.rect.y) != goal_pos:
            raise Exception(f"Level {lv_id} goal mismatch: {(goal.rect.x, goal.rect.y)} != {goal_pos}")
    print("Levels: OK")

def test_fade():
    print("Testing entry fade...")
    g = Game()
    if g.entry_fade != 255:
        raise Exception("Initial entry_fade should be 255")
    g.update()
    if g.entry_fade != 250:
        raise Exception(f"Fade not decrementing: {g.entry_fade}")
    print("Fade: OK")

if __name__ == "__main__":
    try:
        test_persistence()
        test_levels()
        test_fade()
        print("\nALL SYSTEM CHECKS PASSED (v2.0)")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        exit(1)
