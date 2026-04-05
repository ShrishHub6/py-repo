import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime

import pygame


SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 680
FPS = 60
PANEL_BG = (28, 34, 43)
BG_COLOR = (17, 20, 27)
CARD_COLOR = (36, 44, 56)
TEXT_COLOR = (233, 236, 240)
ACCENT = (84, 160, 255)
GOOD = (99, 222, 142)
WARN = (255, 193, 82)


@dataclass
class GameBlueprint:
    title: str
    genre: str
    difficulty: int
    world_size: int
    enemy_count: int
    reward_density: int
    mechanics: list[str]


class Advisor:
    def advise(self, blueprint: GameBlueprint) -> list[str]:
        tips: list[str] = []

        if blueprint.difficulty >= 8 and blueprint.reward_density <= 3:
            tips.append("Difficulty is high with low rewards. Add checkpoints or better loot drops.")
        if blueprint.enemy_count > blueprint.world_size * 2:
            tips.append("Enemy density may overwhelm players. Reduce enemies or increase map size.")
        if blueprint.world_size >= 8 and "Fast Travel" not in blueprint.mechanics:
            tips.append("Large map detected. Consider adding Fast Travel for better pacing.")
        if blueprint.genre == "Roguelike" and "Permadeath" not in blueprint.mechanics:
            tips.append("Roguelikes usually benefit from Permadeath or high-stakes failure.")
        if blueprint.genre == "Platformer" and "Double Jump" not in blueprint.mechanics:
            tips.append("Platformers feel better with movement depth like Double Jump.")
        if blueprint.genre == "Shooter" and blueprint.enemy_count < 8:
            tips.append("Shooter setup has low enemy count. Add waves or stronger AI variety.")

        if not tips:
            tips.append("Solid balance overall. Prototype this loop and playtest with 3-5 players.")

        return tips


class GameBuilderUI:
    GENRES = ["Platformer", "Shooter", "Roguelike", "Adventure"]
    MECHANICS = ["Double Jump", "Dash", "Fast Travel", "Permadeath", "Parry", "Crafting"]

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Game Builder + Advisor")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("consolas", 22)
        self.small_font = pygame.font.SysFont("consolas", 18)
        self.title_font = pygame.font.SysFont("consolas", 30, bold=True)

        self.genre_index = 0
        self.difficulty = 5
        self.world_size = 5
        self.enemy_count = 10
        self.reward_density = 5
        self.mechanics_index = 0
        self.mechanics_selected: set[str] = {"Dash"}

        self.advisor = Advisor()
        self.current_blueprint = self.build_blueprint()
        self.tips = self.advisor.advise(self.current_blueprint)
        self.status = "Press ENTER to refresh advice | S to save blueprint"

    def build_blueprint(self) -> GameBlueprint:
        genre = self.GENRES[self.genre_index]
        title = f"{genre} Prototype"
        return GameBlueprint(
            title=title,
            genre=genre,
            difficulty=self.difficulty,
            world_size=self.world_size,
            enemy_count=self.enemy_count,
            reward_density=self.reward_density,
            mechanics=sorted(self.mechanics_selected),
        )

    def regenerate_advice(self):
        self.current_blueprint = self.build_blueprint()
        self.tips = self.advisor.advise(self.current_blueprint)

    def save_blueprint(self):
        os.makedirs("exports", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join("exports", f"blueprint_{timestamp}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(self.current_blueprint), f, indent=2)
        self.status = f"Saved blueprint to {path}"

    def wrap_text(self, text: str, width: int, font: pygame.font.Font) -> list[str]:
        words = text.split()
        lines: list[str] = []
        current = ""
        for word in words:
            trial = f"{current} {word}".strip()
            if font.size(trial)[0] <= width:
                current = trial
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def draw_slider(self, label: str, value: int, min_v: int, max_v: int, x: int, y: int):
        text = self.font.render(f"{label}: {value}", True, TEXT_COLOR)
        self.screen.blit(text, (x, y))

        bar_y = y + 34
        pygame.draw.rect(self.screen, (90, 104, 120), (x, bar_y, 300, 8), border_radius=4)
        ratio = (value - min_v) / (max_v - min_v)
        knob_x = x + int(ratio * 300)
        pygame.draw.circle(self.screen, ACCENT, (knob_x, bar_y + 4), 10)

    def draw(self):
        self.screen.fill(BG_COLOR)

        left = pygame.Rect(24, 24, 510, 632)
        right = pygame.Rect(548, 24, 508, 632)
        pygame.draw.rect(self.screen, PANEL_BG, left, border_radius=14)
        pygame.draw.rect(self.screen, PANEL_BG, right, border_radius=14)

        title = self.title_font.render("Game Builder", True, TEXT_COLOR)
        self.screen.blit(title, (42, 40))

        genre = self.font.render(f"Genre: {self.GENRES[self.genre_index]}  (Q / E)", True, ACCENT)
        self.screen.blit(genre, (42, 92))

        self.draw_slider("Difficulty", self.difficulty, 1, 10, 42, 145)
        self.draw_slider("World Size", self.world_size, 1, 10, 42, 220)
        self.draw_slider("Enemy Count", self.enemy_count, 1, 20, 42, 295)
        self.draw_slider("Reward Density", self.reward_density, 1, 10, 42, 370)

        me_title = self.font.render("Mechanics (TAB to move, SPACE to toggle)", True, TEXT_COLOR)
        self.screen.blit(me_title, (42, 450))

        for idx, name in enumerate(self.MECHANICS):
            is_active = idx == self.mechanics_index
            selected = name in self.mechanics_selected
            color = GOOD if selected else (180, 186, 196)
            if is_active:
                pygame.draw.rect(self.screen, CARD_COLOR, (42, 485 + idx * 24, 300, 22), border_radius=6)
            prefix = "[x]" if selected else "[ ]"
            item = self.small_font.render(f"{prefix} {name}", True, color)
            self.screen.blit(item, (50, 488 + idx * 24))

        ad_title = self.title_font.render("Advisor", True, TEXT_COLOR)
        self.screen.blit(ad_title, (566, 40))

        bp = self.current_blueprint
        summary = [
            f"Title: {bp.title}",
            f"Genre: {bp.genre}",
            f"Difficulty: {bp.difficulty}/10",
            f"World Size: {bp.world_size}/10",
            f"Enemies: {bp.enemy_count}",
            f"Rewards: {bp.reward_density}/10",
            "Mechanics: " + (", ".join(bp.mechanics) if bp.mechanics else "None"),
        ]

        y = 95
        for line in summary:
            txt = self.small_font.render(line, True, (204, 212, 224))
            self.screen.blit(txt, (566, y))
            y += 28

        tips_title = self.font.render("Design Advice:", True, WARN)
        self.screen.blit(tips_title, (566, 310))

        y = 346
        for tip in self.tips:
            for wrapped in self.wrap_text(f"- {tip}", 460, self.small_font):
                txt = self.small_font.render(wrapped, True, TEXT_COLOR)
                self.screen.blit(txt, (566, y))
                y += 24
            y += 4

        footer = self.small_font.render(
            "Arrows: tune values | ENTER: regenerate | S: save | ESC: quit",
            True,
            (180, 190, 206),
        )
        self.screen.blit(footer, (42, 628))

        status = self.small_font.render(self.status, True, GOOD)
        self.screen.blit(status, (566, 628))

        pygame.display.flip()

    def handle_input(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            if event.key == pygame.K_q:
                self.genre_index = (self.genre_index - 1) % len(self.GENRES)
            if event.key == pygame.K_e:
                self.genre_index = (self.genre_index + 1) % len(self.GENRES)
            if event.key == pygame.K_UP:
                self.difficulty = min(10, self.difficulty + 1)
            if event.key == pygame.K_DOWN:
                self.difficulty = max(1, self.difficulty - 1)
            if event.key == pygame.K_RIGHT:
                self.world_size = min(10, self.world_size + 1)
            if event.key == pygame.K_LEFT:
                self.world_size = max(1, self.world_size - 1)
            if event.key == pygame.K_w:
                self.enemy_count = min(20, self.enemy_count + 1)
            if event.key == pygame.K_s:
                self.save_blueprint()
                return True
            if event.key == pygame.K_x:
                self.enemy_count = max(1, self.enemy_count - 1)
            if event.key == pygame.K_r:
                self.reward_density = min(10, self.reward_density + 1)
            if event.key == pygame.K_f:
                self.reward_density = max(1, self.reward_density - 1)
            if event.key == pygame.K_TAB:
                self.mechanics_index = (self.mechanics_index + 1) % len(self.MECHANICS)
            if event.key == pygame.K_SPACE:
                selected = self.MECHANICS[self.mechanics_index]
                if selected in self.mechanics_selected:
                    self.mechanics_selected.remove(selected)
                else:
                    self.mechanics_selected.add(selected)
            if event.key == pygame.K_RETURN:
                self.regenerate_advice()
                self.status = "Advice refreshed"

            if event.key in {
                pygame.K_q,
                pygame.K_e,
                pygame.K_UP,
                pygame.K_DOWN,
                pygame.K_RIGHT,
                pygame.K_LEFT,
                pygame.K_w,
                pygame.K_x,
                pygame.K_r,
                pygame.K_f,
                pygame.K_TAB,
                pygame.K_SPACE,
            }:
                self.regenerate_advice()

        return True

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                running = self.handle_input(event)
                if not running:
                    break
            self.draw()

        pygame.quit()


def main():
    app = GameBuilderUI()
    app.run()


if __name__ == "__main__":
    main()
