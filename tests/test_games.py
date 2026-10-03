import pytest
from app.core.manager import GameManager
from app.chat.models import ChatMessage

def test_command_parsing():
    manager = GameManager()
    msg = ChatMessage("1", "user1", "User1", "!game sokoban")
    manager.process_messages([msg])
    assert manager.state == "SOKOBAN"

def test_quit_voting():
    manager = GameManager()
    manager.viewer_count = 3
    manager._start_game("sokoban")
    
    # Needs 2 votes
    msg1 = ChatMessage("1", "u1", "U1", "!game quit")
    manager.process_messages([msg1])
    assert manager.state == "SOKOBAN"
    
    # Duplicate vote
    msg2 = ChatMessage("2", "u1", "U1", "!game quit")
    manager.process_messages([msg2])
    assert manager.state == "SOKOBAN"
    
    # Second vote
    msg3 = ChatMessage("3", "u2", "U2", "!game quit")
    manager.process_messages([msg3])
    assert manager.state == "MAIN_MENU"



def test_ttt_logic():
    from app.games.ttt import TicTacToeGame
    game = TicTacToeGame()
    
    game.handle_command("!ttt join", "u1", "U1")
    game.handle_command("!ttt join", "u2", "U2")
    
    game.handle_command("!ttt 1", "u1", "U1")
    assert game.board[0] == "X"
    
    game.handle_command("!ttt 2", "u2", "U2")
    assert game.board[1] == "O"


