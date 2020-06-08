# =============================================================================
# All code from this file is written by Tarun Ravi
# Date Written: 6/7/2020
# =============================================================================

import pygame
import numpy as np
from collections import defaultdict
import pygame.freetype
height = 600
width = 1000
screen = pygame.display.set_mode((width, height))

backgroundImage = pygame.image.load('Cards/background.jpg')
backgroundImage = pygame.transform.scale(backgroundImage, (height, width)) #scales an image

pygame.init()
effect = pygame.mixer.Sound('Cards/cardSound.wav')

programIcon = pygame.image.load('Cards/playing_cards.png')
pygame.display.set_icon(programIcon)

actionSpace = [0,1] #These are the actions the AI can take, 0 for stick, 1 for hit


#Changeable Variables
dealerLimit = 18 #Sum needed for dealer to stop hitting. 
breakTime = 2 #Delay (in seconds) between games
FPS = 30 #How many frames will be drawn every second.
volume = True


#Changeable AI Variables
AI = False #If False, you can play against the dealer without the AI
e = 0.1 #Epsilon Value for Monte Carlo Algorithm
gamma = 1 #Gamma Value for Monte Carlo Algorithm
alpha=0.02 #Alpha Value for Monte Carlo Algorithm


# =============================================================================
# Card Class
# =============================================================================
class card():
    def __init__(self, x, y, player, show=True):
        self.number = np.random.choice(range(1, 14)) #1: Ace, 2-10: Number Card, 11: Jack, 12: Queen, 13: King
        self.x = x #X location of the card
        self.y = y #Y location of the card
        self.show = show #If false, the card will be face down. If true, card will be revealed. 
        self.player = player #Identify if the card is for the player's or dealer's
        if self.player: #Different card image if player vs dealer
            location = 'Cards/card_b_s'
        else:
            location = 'Cards/card_b_h'
        self.image = pygame.image.load(location+str(self.number)+'.png')
        self.w, self.h = self.image.get_rect().size #Width/height of card image
        
        if self.number>10:self.number=10 #If a card is a facecard, its value is 10
        
        if volume: #Play sound only if audio is turned on
            effect.play()
    
    def reveal(self): #The dealers second card is initially hidden, this will reveal that card
        self.show = True 
        if volume: #Play sound only if audio is turned on
            effect.play()
    
    def draw(self): #Will draw the card to screen
        if self.show:
            screen.blit(self.image, (self.x,self.y))
        else:
            screen.blit(pygame.image.load('Cards/faceDown.png'), (self.x,self.y))


#Hit method, will create new card for either the dealer or player
def hit(cardCount, isPlayer): 
    if isPlayer: 
        return card(850-130*cardCount-5*cardCount, 378, True) #Will create a new card next to any existing cards
    else:
        return card(20 + 130*cardCount + 5*cardCount, 20, False) #Will create a new card next to any existing cards
    
#Will determine if the ace can be counted as 11, without it exceeding the 21st limit
def checkAce(playersCard, hidden=False):
    isAce=False
    sumOfList = 0
    
    for i in playersCard:
        sumOfList += i.number
        if i.number == 1:
            isAce = True
    
    if isAce and sumOfList-1+11<=21:
        return True
    
    return False

#Will return the player/dealer's hand sum. This will return the highest sum possible, in the case of aces.
def checkSum(cards, hidden=False):
    cardSum = 0
    for i in cards:
       if not hidden:   
          cardSum += i.number
       else:
           if i.show == True:
               cardSum += i.number
           
    if checkAce(cards, hidden):
        cardSum = cardSum - 1 + 11
    
    return cardSum

#Will determine who won/lost/draw
def whoWon(dealer,playersCard, dealersCards):
    playersSum = checkSum(playersCard)
    dealersSum = checkSum(dealersCards)
    if playersSum>21:
        return True, False #Game over, who won
    if playersSum==21:
        return True, True
    if dealersSum == 21:
        return True, False
    if not dealer:
        return False, False
    if dealer and playersSum <= 21 and dealersSum>21:
        return True, True #Game over, who won
    if dealer and playersSum>dealersSum:
        return True, True
    if dealer and dealersSum>playersSum:
        return True, False
    if dealer and dealersSum==playersSum:
        return True, None
    else:
        return False, False
    
#Given an action (0 or 1), will execute the action. 
def aiStep(action, playersCard, dealersCards):
    if action == 1: #Hit
        playersCard.append(hit(len(playersCard), True))
    else:
        dealersCards[-1].reveal()
        while checkSum(dealersCards) <= dealerLimit:
            dealersCards.append(hit(len(dealersCards), False))
    return playersCard, dealersCards

#Will follow an epsilon greedy policy, given Q to determine the next action 
#Meaning it will determine the best action to take in the current moment
def genAction(state, e, Q):
    probHit = Q[state][1]
    probStick = Q[state][0]
    
    if probHit>probStick:
        probs = [e, 1-e]
    elif probStick>probHit:
        probs = [1-e, e]
    else:
        probs = [0.5, 0.5]
        
    action = np.random.choice(np.arange(2), p=probs)   
    return action
    
#Will create the current state value. 
#The state value is a tuple containing the player's current sum, dealer's current sum, and if the ace can be counted as 11
def createStateValues(playersCard, dealersCards):
    return checkSum(playersCard), checkSum(dealersCards, True), checkAce(playersCard)

#Will change Q after each completed game/episode
#This is where the "learning" is taking place
def setQ(Q, currentEpisode, gamma, alpha):
    for t in range(len(currentEpisode)):
        #episode[t+1:,2] gives all the rewards in the episode from t+1 onwords
        rewards = currentEpisode[t:,2]
        #Create a list with the gamma rate increasing
        discountRate = [gamma**i for i in range(1,len(rewards)+1)]
        #Discounting the rewards from t+1 onwards
        updatedReward = rewards*discountRate
        #Summing up the discounted rewards to equal the return at time step t
        Gt = np.sum(updatedReward)
        #Calculating the actual Q table value of the state, actionn pair. 
        Q[currentEpisode[t][0]][currentEpisode[t][1]] += alpha *(Gt - Q[currentEpisode[t][0]][currentEpisode[t][1]])
    return Q

#The actual main method
def main():
    pygame.display.set_caption("Blackjack AI")
    running = True
    clock = pygame.time.Clock()
    
    
    #Will create 2 random cards for player and dealer. 
    #The dealer's second card is hidden
    #Each card is 5 pixels away from each other 
    dealersCards = [card(20,20, False), card(155,20, False, False)]
    playersCard = [card(850, 378, True)]
    playersCard.append(hit(len(playersCard), True))
    gameOver = False #Is the game over or not?
    dealer=False #Is it the dealer's turn or not?
    winner=False #If the player won. 
    delayBetweenGames=0 #This is how I track how long the delay is

    currentEpisode = [] #The list containing the moves of the game
    Q = defaultdict(lambda: np.zeros(2)) #Initialling an empty dictionary for Q
    
    gamesWon = gamesLost = gamesPlayed = 0 #Initially the games won and lost are 0
    
    GAME_FONT = pygame.freetype.Font("Roboto-Light.ttf", 24)
    
    while running:
        clock.tick(FPS)
        screen.fill(pygame.Color(33,42,49))
        
        global volume
        #Draw dealer's cards
        for i in dealersCards:
            i.draw() 

        for i in playersCard:
            i.draw()
        
        #Will display all the text
        if AI:
            name = "AI"
        else:
            name = "Player"
        text_surface, rect = GAME_FONT.render((name + "'s Current Sum: " + str(checkSum(playersCard))), pygame.Color('white'))
        
        if not AI:
            screen.blit(text_surface, (722, 350))
        else:
            screen.blit(text_surface, (760, 350))
        text_surface, rect = GAME_FONT.render(("Dealer's Current Sum: " + str(checkSum(dealersCards, True))), pygame.Color('white'))
        screen.blit(text_surface, (23, 230))
        
        text_surface, rect = GAME_FONT.render(("Games Won by "  + name + ": " + str(gamesWon)), pygame.Color('white'))
        screen.blit(text_surface, (23, 470))
        
        text_surface, rect = GAME_FONT.render(("Games Lost: " + str(gamesLost)), pygame.Color('white'))
        screen.blit(text_surface, (23, 510))
        
        text_surface, rect = GAME_FONT.render(("Number of Rounds: " + str(gamesPlayed)), (232, 75, 61))
        screen.blit(text_surface, (23, 550))
        

        if volume:
            screen.blit(pygame.image.load('Cards/audio.png'), (width-50-10,210))
        else:
            screen.blit(pygame.image.load('Cards/mute.png'), (width-50-10,210))
        #Draws the Hit and Stick buttons, if AI mode is off
        if not AI:
            screen.blit(pygame.image.load('Cards/HIT.png'), (width-200,20))
            screen.blit(pygame.image.load('Cards/STICK.png'), (width-200,110))

        gameOver, winner = whoWon(dealer,playersCard,dealersCards)
        
        #End of game mechanics            
        if gameOver and delayBetweenGames<=breakTime*FPS:
            if delayBetweenGames==0:
                gamesPlayed+=1
                if None:
                    gamesWon = gamesWon
                elif winner:
                    #print("You Won")
                    gamesWon+=1
                    #print(gamesWon, gamesLost)
                else:
                    gamesLost+=1
                    #print(gamesWon, gamesLost)
                '''
                if gamesPlayed in [100000, 150000, 200000, 300000] :
                    from plot_utils import plot_blackjack_values
                    plot_blackjack_values(dict((k,np.max(v)) for k, v in Q.items()), gamesPlayed, gamesWon, gamesLost )
                 '''  
            delayBetweenGames+=1
    
            
        if gameOver and delayBetweenGames>=breakTime*FPS:
            dealersCards = [card(20,20, False), card(155,20, False, False)] #5 space
            playersCard = [card(850, 378, True)]
            playersCard.append(hit(len(playersCard), True))
            gameOver = dealer = winner = False
            delayBetweenGames = 0



        #AI aspect, stores each state/reward of an episode. After an episode it updates the Q values
        if AI and not gameOver and not dealer:
            #print("AI MODE")
            currentState = createStateValues(playersCard, dealersCards)
            action = genAction(currentState, e, Q)
            if action==0:
                dealer=True
            playersCard, dealersCards = aiStep(action, playersCard, dealersCards)
            gameOver, winner = whoWon(dealer,playersCard,dealersCards)
            if gameOver and winner:
                reward = 1
            elif gameOver and not winner:
                reward = -1            
            else:
                reward = 0

            currentEpisode.append((currentState, action, reward))
            
            if gameOver:
                currentEpisode = np.array(currentEpisode)
                Q = setQ(Q, currentEpisode, gamma, alpha)
                currentEpisode= []
        

        for event in pygame.event.get():
            #Key Presses
            #Pressing r will reset the current game
            #Pressing p will plot the current plot
            #Pressing w will print games won/lost
            #Pressing t will reset the win/lose numbers
            #Pressing h will do a hit (when not in AI mode)
            #Pressing s will do a stick (when not in AI mode)
            #Pressing m will mute sounds
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    dealersCards = [card(20,20, False), card(155,20, False, False)] #5 space
                    playersCard = [card(850, 378, True)]
                    gameOver = dealer = winner = False
                    delayBetweenGames = 0
                    currentEpisode = 0
                if event.key == pygame.K_p:
                    from plot_utils import plot_blackjack_values
                    plot_blackjack_values(dict((k,np.max(v)) for k, v in Q.items()), gamesPlayed, gamesWon, gamesLost )
                if event.key==pygame.K_w:
                    print("Wins:",gamesWon,"Losses:",gamesLost, "Games Played:",gamesPlayed)
                if event.key==pygame.K_t:
                    gamesWon=gamesLost=0
                if event.key == pygame.K_h and not gameOver and not AI:
                    playersCard.append(hit(len(playersCard), True))
                if event.key == pygame.K_s and not gameOver and not AI:
                    dealer=True
                    
                    for i in dealersCards:
                        i.draw() 
                        i.reveal()
                    while checkSum(dealersCards) <= dealerLimit:
                        dealersCards.append(hit(len(dealersCards), False))
                if event.key == pygame.K_m:
                    volume = not volume
                
            #Mouse Clicks
            #Click on Hit button to Hit
            #Click on Stick button to Stick
            #Click on Volume button to mute/unmute
            if  event.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()
                print(mouseX, mouseY)
                if mouseX>=940 and mouseX<=990 and mouseY>=210 and mouseY<=260:
                    volume = not volume
                if mouseX>=800 and mouseX<=990 and mouseY>=30 and mouseY<=120 and not AI:
                    playersCard.append(hit(len(playersCard), True))
                if mouseX>=800 and mouseX<=990 and mouseY>=120 and mouseY<=210 and not AI: 
                    dealer=True
                    
                    for i in dealersCards:
                        i.draw() 
                        i.reveal()
                    while checkSum(dealersCards) <= dealerLimit:
                        dealersCards.append(hit(len(dealersCards), False))
                        
        pygame.display.update()
        
    pygame.display.quit()
 
#Will call the main method
if __name__ == "__main__":
    main()