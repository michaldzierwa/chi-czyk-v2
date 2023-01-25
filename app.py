from flask import Flask
from flask import render_template
from flask import redirect
from flask import request
import random

app = Flask(__name__)
app.jinja_env.filters['zip'] = zip

class Coin():
    def __init__(self, id, color):
        self.id = id
        self.color = color

    def __repr__(self):
        return f'{self.id} {self.color}'

class Dice():
    def roll(self):
        min = 1
        max = 6
        roll_result = random.randint(min, max)
        return roll_result

class Board():
    def __init__(self):
        self.list = []
        for x in range (40): self.list.append(None)

    def get_coins_by_player(self, player):
        player_coins_on_list = []
        for field in self.list:
            if field in player.coins: player_coins_on_list.append(field)
        return player_coins_on_list
        # return [
        #     #coin for coin in self.list if coin and coin.color == player.color
        #     player_coins_on_list
        # ]


class Game():
    def __init__(self, names):
        self.active_player = 0
        self.players = list()
        #self.plansza = []
        self.dice = Dice()
        self.board = Board()
        self.board_for_jinja = []
        id = 0
        for name in names:
            self.players.append(Player(id, name))
            id += 1
        self.assign_colors_for_players()
        self.assign_coins_for_players()
        self.assigns_coins_to_storage()
        self.make_board_for_jinja()
        self.starting_positions_dict = {
            0: 0,
            1: 10,
            2: 20,
            3: 30
        }

    def assign_colors_for_players(self):
        color = ['Red', 'Blue', 'Green', 'Yellow' ]
        x = 0
        for player in self.players:
            player.color = color[x]
            x += 1
            #print(player.player_name, player.id, player.color)

    def assign_coins_for_players(self):
        for player in self.players:
            for id in range (0,4):
                player.coins.append(Coin(id, player.color))

    def assigns_coins_to_storage(self):
        for player in self.players:
            for coin in player.coins:
                #print(coin)
                player.coins_storage.append(coin)
            #print(player.player_name, player.id, player.coins[0].color)

    def make_board_for_jinja(self):
        self.board_for_jinja = [[0 for col in range(11)] for row in range(11)]
        for i in range(11):
            for j in range(11):
                self.board_for_jinja.append('x')
           # self.board_for_jinja.append(self.board_for_jinja)

    def check_if_there_is_players_coin_on_board(self):
        pass

#starting_positions jhako funckja:
    # def starting_positions(self, player):
    #     if self.players[player].color == 'Red':
    #         start_position = 0#pozcja startowa dla kazdego pionka na liście- planszy
    #     elif self.players[player].color == 'Blue':
    #         start_position = 10
    #     elif self.players[player].color == 'Green':
    #         start_position = 20
    #     elif self.players[player].color == 'Yellow':
    #         start_position = 30

class Player():
    def __init__(self, id, name='Anonimowy'):
        self.id = id
        self.player_name = name
        self.coins = []
        self.coins_storage = []
        self.coins_home =[]
        # self.id = ''
        # self.color

@app.route('/')
def home():
    return render_template('home.htm')

@app.route('/single/form', methods=['GET', 'POST'])
def single_form():
    if request.method == 'POST':
        players = [x for x in request.form.getlist('names') if x]
        #print(players)

        if len(players) == 4:
            return single_phase0(players)
    return render_template('single/form.htm')

def single_phase0(name):
    global game
    game = Game(name)
    return redirect('/single/turn_start', code=302)

@app.route('/single/turn_start')
def turn_start():
    print(game.players[game.active_player].color)
    if len(game.players[game.active_player].coins_home) == 4:
        if game.active_player != 3:
            game.active_player += 1
        elif game.active_player == 3:
            game.active_player = 0
        return turn_start()
    return render_template('single/turn_start.htm', game=game)

@app.route('/single/roll_dice')
def roll_dice():
    throw_result = game.dice.roll()
    print(throw_result)
    #print(game.players[game.active_player].coins)
    #throw_result = 6 # todo
    #throw_result = 3
    player = game.players[game.active_player]
    player_coins_at_board = game.board.get_coins_by_player(player)
    print(player_coins_at_board)
    if throw_result != 6 and len(player_coins_at_board) == 0:
        if game.active_player != 3:
            game.active_player += 1
        elif game.active_player == 3:
            game.active_player = 0
        return turn_start()

    return render_template(
        'single/move_coin.htm',
        game=game,
        throw_result=throw_result
    )

@app.route('/single/pop_coin_from_storage')
def pop_coin_from_storage():
    player = game.players[game.active_player]
    game.board.list[game.starting_positions_dict[game.active_player]] = player.coins_storage.pop()
    return turn_start()

@app.route('/single/move')
@app.route('/single/move/<selected_coin>/<throw_result>/<x>')
def move(throw_result, selected_coin, x):
    throw_result = int(throw_result)
    x = int(x)
    temp = selected_coin
    game.board.list[x] = None
    #del game.board.list[int(x)]
    if (x + throw_result) > 39:
        new_position = throw_result - (39 - x) - 1
        game.board.list[new_position] = temp
    else:
        game.board.list[x + throw_result] = temp
    if throw_result != 6:
        if game.active_player != 3:
            game.active_player += 1
        elif game.active_player == 3:
            game.active_player = 0

    return turn_start()

# @app.route('/single/turn_start')
# def turn_start():
#     #print(game.players)
#     #print(game.players[game.active_player].player_name)
#     # if game.active_player != 3:
#     #     game.active_player +=1
#     # elif game.active_player == 3:
#     #     game.active_player = 0
#     if len(game.players[game.active_player].coins_home) == 4:
#         if game.active_player != 3:
#             game.active_player += 1
#         elif game.active_player == 3:
#             game.active_player = 0
#         return turn_start()
#
#         return turn_start()
#     # else:
#     #     if len(game.players[game.active_player].coins_storage) < 4:
#     #         a = game.board.list[game.starting_positions_dict[game.active_player]]
#     #         game.board.list[game.starting_positions_dict[game.active_player]] = None
#     #
#     #         game.board.list[game.starting_positions_dict[game.active_player] + throw_result] = a
#     #     if game.active_player != 3:
#     #         game.active_player += 1
#     #     elif game.active_player == 3:
#     #         game.active_player = 0
#     return render_template('single/turn_start.htm', game=game, throw_result=throw_result)
#    # print(game.dice.roll())

    # @app.route('/single/phase1')
    # def single_phase1():
    #     if len(game.players[game.active_player].coins_home) == 4:
    #         return single_phase1()
    #     throw_result = game.dice.roll()
    #     print(throw_result)
    #     if throw_result == 6:
    #         coin_start = game.players[game.active_player].coins_storage.pop()
    #         game.board.list[game.starting_positions_dict[game.active_player]] = coin_start
    #         return single_phase1()
    #     else:
    #         if len(game.players[game.active_player].coins_storage) < 4:
    #             a = game.board.list[game.starting_positions_dict[game.active_player]]
    #             game.board.list[game.starting_positions_dict[game.active_player]] = None
    #
    #             game.board.list[game.starting_positions_dict[game.active_player] + throw_result] = a
    #         if game.active_player != 3:
    #             game.active_player += 1
    #         elif game.active_player == 3:
    #             game.active_player = 0
    #
    #     print(game.players[game.active_player].coins_storage)

    #return render_template('single/turn_start.htm', game= game, throw_result= throw_result)
#napisane 21.01; do wykorzystania przy ruszaniu, metoda będzie w obiekcie np gry albo raczej w widoku
#game.board.list przekazane jako argument z frontu z planszy- przy tej metodzie poruszania nie trzeba pzechowywac pozycji pionka
# def move(game.board.list[x], cala_plansza_lista, x):
#     temp = game.board.list[x]
#     game.board.list[x] = None
#     cala plansza lista[x + throw_result]
    #return faza rzutu kostką dla następnego gracza czyli wcześniej dodać active player + 1


@app.route('/test')
def test():  # put application's code here
    return 'test!'


if __name__ == '__main__':
    #app.run(host="wierzba.wzks.uj.edu.pl", port=5106, debug=True)
    app.run(host="127.0.0.1", port=8080, debug=True)
