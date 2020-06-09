# Blackjack AI

In this personal project, I designed an AI to learn how to play the popular cardgame Blackjack without any humans teaching it.  
This project has two primary components: Building the Blackjack game, and adding the Blackjack AI

## Demo of the AI

![AI Demo](https://github.com/MyWorldRules/BlackjackAI/blob/master/images/AI_Gif.gif?raw=true)

## Demo of User playing Blackjack
![Blackjack Demo](https://github.com/MyWorldRules/BlackjackAI/blob/master/images/Image1.png?raw=true)

## Building the Blackjack Game
I used Pygame with Python to design the game. 
In the code, if you set `AI = False` in line 34, you as the user will be able to play Blackjack against the dealer. 

### Playing the Game
To "Hit" you may press the Hit button on screen, or press 'H' on your keyboard

To "Stick" you may press the Stick button on screen, or press 'S' on your keyboard

To Mute the card dealing sound, you may press the Mute button on screen, or press 'M' on your keyboard

## Adding the Blackjack AI
To create the Blackjack AI, I used the Monte Carlo Method of reinforcement learning. 

You may change the `Epsilon`, `Gamma` or `Alpha` values on lines 35-37 of the code. 

On average, the AI can start to beat the dealer within 5000 iterations of the game. 

## AI Learning Progression
### After 5 iterations
At this point the AI's only played 5 games, this isn't yet familiar with the Blackjack environment. This is evident in the plot, as everything's still gray. 

In addition, the AI has only won 1 out of the 5 games. 

![5 Iterations](https://github.com/MyWorldRules/BlackjackAI/blob/master/Trial%201/Figure_1.png?raw=true)

### After 1000 iterations
The AI has basically visited a lot of the possible states at least one time, as evident because the entire plot is still gray but more filled out.

Again the AI has more loses then wins (463 wins to 537 loses)

![1000 Iterations](https://github.com/MyWorldRules/BlackjackAI/blob/master/Trial%201/Figure_7.png?raw=true)

### After 5000 iterations
Parts of the plot is starting to develop color, meaning the AI has visited that state more, and is more confident on what action to take in that particular state.

The AI now has more wins than loses (2517 wins to 2483 loses)

![5000 Iterations](https://github.com/MyWorldRules/BlackjackAI/blob/master/Trial%201/Figure_8.png?raw=true)

### After 250,000 iterations
Skipping ahead to 250,000 iterations, the AI has nearly visited every possible state and is confident on the action to take at each state.

Again the AI has more wins than loses and that gap has increased. 

![5000 Iterations](https://github.com/MyWorldRules/BlackjackAI/blob/master/Trial%202/Figure_7.png?raw=true)

