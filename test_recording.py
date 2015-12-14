import recording
import models

def test_initial_layout():
    record = recording.GameRecord()

    players = set()
    players.add(models.Player(seat=0, name='yurick', color='green'))
    players.add(models.Player(seat=1, name='ross', color='red'))
    players.add(models.Player(seat=2, name='josh', color='blue'))
    players.add(models.Player(seat=3, name='zach', color='orange'))

    resources =
    record.record_pregame()
