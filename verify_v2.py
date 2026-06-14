
import os
import json
import pygame

# Mocking pygame to run headlessly
os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()

# We need to mock key presses for Game.update()
class MockKeys:
    def __getitem__(self, key):
        return 0

def mock_get_pressed():
    return MockKeys()

pygame.key.get_pressed = mock_get_pressed

from scft import Game, SAVE_FILE

def test_persistence():
    print("Testing persistence...")
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)

    game = Game()
    game.unlocked = 3
    game.souls = 150
    game.health_upgrades = 2
    game.difficulty = 1.5
    game._save_data()

    assert os.path.exists(SAVE_FILE), "Save file not created"

    new_game = Game()
    assert new_game.unlocked == 3, f"Expected 3, got {new_game.unlocked}"
    assert new_game.souls == 150
    assert new_game.health_upgrades == 2
    assert new_game.difficulty == 1.5
    print("Persistence test passed!")

def test_reset():
    print("Testing progress reset...")
    game = Game()
    game.unlocked = 4
    game._save_data()
    game._reset_progress()

    assert game.unlocked == 1
    assert not os.path.exists(SAVE_FILE)
    print("Reset test passed!")

def test_level_dimensions():
    print("Testing level dimensions...")
    game = Game()

    levels = [
        (1, 4000, 900),
        (2, 4500, 900),
        (3, 4800, 900),
        (4, 5200, 900),
        (5, 4200, 900)
    ]

    for lv, w, h in levels:
        game.current_level = lv
        game._init_game()
        assert game.world_w == w, f"Level {lv} width: expected {w}, got {game.world_w}"
        assert game.world_h == h, f"Level {lv} height: expected {h}, got {game.world_h}"
    print("Level dimensions test passed!")

if __name__ == "__main__":
    try:
        test_persistence()
        test_reset()
        test_level_dimensions()
        print("\nALL TESTS PASSED!")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    finally:
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
