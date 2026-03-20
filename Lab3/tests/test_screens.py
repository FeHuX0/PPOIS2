import pygame


def test_menu_mouse_navigation_and_escape(app):
    app.change_state('menu')
    menu = app.state_manager.current_screen
    menu.render(app.surface)
    rect = menu.option_rects[1]
    menu.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=rect.center))
    assert app.state_manager.current_name == 'scores'
    app.change_state('menu')
    menu = app.state_manager.current_screen
    menu.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    assert app.running is False


def test_menu_help_and_back(app):
    app.change_state('menu')
    menu = app.state_manager.current_screen
    menu.selected = 2
    menu.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    assert app.state_manager.current_name == 'help'
    help_screen = app.state_manager.current_screen
    help_screen.render(app.surface)
    help_screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    assert app.state_manager.current_name == 'menu'


def test_scores_and_game_over_navigation(app):
    app.change_state('game_over', score=10, wave=2, victory=True)
    screen = app.state_manager.current_screen
    screen.render(app.surface)
    screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB))
    assert app.state_manager.current_name == 'scores'
    scores = app.state_manager.current_screen
    scores.render(app.surface)
    assert len(scores.entries) == 10
    scores.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    assert app.state_manager.current_name == 'menu'


def test_name_input_screen_saves_score(app):
    app.change_state('name_input', score=2500, wave=7, victory=False, is_first_place=True)
    screen = app.state_manager.current_screen
    screen.render(app.surface)
    screen.handle_event(pygame.event.Event(pygame.TEXTINPUT, text='A'))
    screen.handle_event(pygame.event.Event(pygame.TEXTINPUT, text='B'))
    screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    assert app.state_manager.current_name == 'scores'
    assert app.score_system.top_scores()[0].name.startswith('AB')


def test_name_input_backspace_and_escape(app):
    app.change_state('name_input', score=900, wave=2, victory=False, is_first_place=False)
    screen = app.state_manager.current_screen
    screen.handle_event(pygame.event.Event(pygame.TEXTINPUT, text='Z'))
    screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE))
    assert screen.name == ''
    screen.render(app.surface)
    screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    assert app.state_manager.current_name == 'menu'
