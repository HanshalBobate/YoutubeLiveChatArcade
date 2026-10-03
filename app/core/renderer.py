

class Renderer:
    def render(self, game_state) -> list[list[str]]:
        raise NotImplementedError

def render_to_string(grid: list[list[str]]) -> str:
    return "\n".join("".join(row) for row in grid)
