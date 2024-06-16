import pygame, sys, random
from pygame.locals import *

BOARDWIDTH = 4
BOARDHEIGHT = 4
TILESIZE = 80
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
FPS = 30
BLANK =None

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BRIGHTBLUE = (0, 50, 255)
DARKTURQUOISE = (3, 54, 73)
GREEN = (0, 204, 0)

BGCOLOR  = DARKTURQUOISE
TILECOLOR = GREEN
TEXTCOLOR = WHITE
BORDERCOLOR = BRIGHTBLUE
BASICFONTSIZE = 20

BUTTONCOLOR = WHITE
BUTTONTEXTCOLOR = BLACK
MESSAGECOLOR = WHITE

XMARGIN = int((WINDOWWIDTH -(TILESIZE * BOARDWIDTH + (BOARDWIDTH - 1))) / 2)
YMARGIN = int((WINDOWHEIGHT - (TILESIZE * BOARDHEIGHT + (BOARDHEIGHT - 1))) / 2)

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, RESET_SURF, RESET_RECT, NEW_SURF, NEW_RECT, SOLVE_SURF, SOLVE_RECT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Slide Puzzule')
    BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)

    RESET_SURF, RESET_RECT = makeText('Reset', TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 90)
    NEW_SURF, NEW_RECT = makeText('New Game', TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 60)
    SOLVE_SURF, SOLVE_RECT = makeText('Solve', TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 30)

    mainBoard, solutionSeq = generateNewPuzzle(80)
    # solutionSeq is the list of stored random move performed
    SOLVEDBOARD = getStartingBoard()
    # a solved board is the same as a board in the start state
    allMoves = [] # list storing all moves made from the solved configuration

    while True: # main game loop
        slideTo = None # the direction a tile should slide
        msg = '' # message shown in upper left corner
        if mainBoard == SOLVEDBOARD:
            msg = 'Solved!'

            drawBoard(mainBoard, msg)

        checkForQuit()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                spot_x, spot_y = getSpotClicked(mainBoard, event.pos[0], event.pos[1])
                if (spot_x, spot_y) == (None, None):
                    # check if user clicked on an option button
                    if RESET_RECT.collidepoint(event.pos):
                        resetAnimation(mainBoard, allMoves) #clicked on reset button
                        allMoves = []
                    elif NEW_RECT.collidepoint(event.pos):
                        mainBoard, solutionSeq = generateNewPuzzle(80)
                        # clicked on new game button
                        allMoves = []
                    elif SOLVE_RECT.collidepoint(event.pos):
                        resetAnimation(mainBoard, solutionSeq + allMoves)
                        # clicked on solved button
                        allMoves = []
                    else:
                        # check if the clicked tile was next to the blank spot
                        # slides tiles with mouse
                        blank_x, blank_y = getBlankPosition(mainBoard)
                        if spot_x == blank_x + 1 and spot_y == blank_y:
                            slideTo = LEFT
                        elif spot_x == blank_x - 1 and spot_y == blank_y:
                            slideTo = RIGHT
                        elif spot_x == blank_x and spot_y == blank_y + 1:
                            slideTo = UP
                        elif spot_x == blank_x and spot_y == blank_y -1:
                            slideTo = DOWN
            elif event.type == KEYUP:
                # check if a user pressed a key to slide a tile
                # "event.key in (K_LEFT, k_a)" is the same as "event.key == K_LEFT or event.key == K_a"
                if event.key in (K_LEFT, K_a) and isValidMove(mainBoard, LEFT):
                    slideTo = LEFT
                elif event.key in (K_RIGHT, K_d) and isValidMove(mainBoard, RIGHT):
                    slideTo = RIGHT
                elif event.key in (K_UP, K_w) and isValidMove(mainBoard, UP):
                    slideTo = UP
                elif event.key in (K_DOWN, K_s) and isValidMove(mainBoard, DOWN):
                    slideTo = DOWN

        if slideTo:
            '''
            the parameters for the slideAnimation() are; the baord data structure, the direction of the slide,
            the msg to display during the move and the speed of the move. 
            '''
            slideAnimation(mainBoard, slideTo, 'Click tile or press arrow keys to slide.', 8)
            # show slide on screen
            makeMove(mainBoard, slideTo) # updates data structure
            '''
            appends the allmoves list with slideTo variable so that the player can undo all
            of their moves when reset is clicked vv
            '''
            allMoves.append(slideTo) # record the slide
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def terminate():
    pygame.quit()
    sys.exit()

def checkForQuit():
    for event in pygame.event.get(QUIT): # get all the quit events
        terminate() # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP): # get all key up events
        if event.key == K_ESCAPE:
            terminate() # terminate if the event was for the escape key
        pygame.event.post(event) # put the other KEYUP event objects back

# Return a board data structure with tiles in the solved state.
def getStartingBoard():
    '''
    for example, if BOARDWIDTH and BOARDHEIGht are both 3
    this function returns [[1, 4, 7], [2, 5, 8], [3, 6, None]]

    -Initialization: It starts by initializing a counter variable to 1. 
    This variable will be used to populate the tiles of the board.
-Nested Loop: The function then enters into two nested loops. 
The outer loop iterates over the rows of the board (x), and the inner loop iterates over the columns of the board (y).
-Populating Tiles: Within the nested loops, each tile of the board is assigned a number incrementally starting from 1.
This is done by appending the value of the counter variable to the column list.
After appending, the counter is incremented.
-Handling Wraparound: There is a special case for handling the wraparound when the end of a row is reached. 
After filling in the tiles for a row, the counter variable is adjusted to start filling in the next row.
This adjustment ensures that the numbers are placed in the correct order on the board.
-Setting the Blank Space: Once all the tiles are populated,
the last tile in the bottom-right corner is assigned a 
value of None to represent the blank space.
-Returning the Board: Finally, the function returns the generated board,
which is a 2D list containing the numbers and the blank 
space arranged in the starting configuration.
    '''
    counter = 1
    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(counter)
            counter += BOARDWIDTH
        board.append(column)
        counter -= BOARDWIDTH * (BOARDHEIGHT - 1) + BOARDWIDTH - 1

    board[BOARDWIDTH - 1][BOARDHEIGHT - 1] = None
    return board

def getBlankPosition(board):
    # return the x and y coordinates of the blank space.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == None:
                return (x, y)
            
def makeMove(board, move):
    # this function does not check if the move is valid
    blank_x, blank_y = getBlankPosition(board)
    # updates the data structutre 'board' by swapping the value of tile with the blank space value


    if move == UP:
        board[blank_x][blank_y], board[blank_x][blank_y + 1] = board[blank_x][blank_y + 1], board[blank_x][blank_y]
    elif move == DOWN:
        board[blank_x][blank_y], board[blank_x][blank_y - 1] = board[blank_x][blank_y - 1], board[blank_x][blank_y]
    elif move == LEFT:
        board[blank_x][blank_y], board[blank_x + 1][blank_y] = board[blank_x + 1][blank_y], board[blank_x][blank_y]
    elif move == RIGHT:
        board[blank_x][blank_y], board[blank_x - 1][blank_y] = board[blank_x - 1][blank_y], board[blank_x][blank_y]
        # there is no need for a return value here because the function has a list value as an argument
        # any changes made to 'board' will be made to the list value

# pass in the 2D board and a move the player wants to make
def isValidMove(board, move):
    blank_x, blank_y = getBlankPosition(board)
    # returns True if the move is possible and False if not
    # because the expressions are joined by 'or' operators, only part of it needs to be true for the whole expression to be true
    # the 'len(board[0] - 1)' is basically a boundary that stops the player from moving off board
    return (move == UP and blank_y != len(board[0]) - 1) or \
            (move == DOWN and blank_y != 0) or \
            (move == LEFT and blank_x != len(board) - 1) or \
            (move == RIGHT and blank_x != 0)

def getRandomMove(board, lastMove=None):
    # v start with a full list of all four moves v
    validMoves = [UP, DOWN, LEFT, RIGHT]
    # remove moves from the list as they are disqualified
    if lastMove == UP or not isValidMove(board, DOWN):
        validMoves.remove(DOWN)
        # prevents random move from being the opposite of the move that just took place
    if lastMove == DOWN or not isValidMove(board, UP):
        validMoves.remove(UP)
    if lastMove == LEFT or not isValidMove(board, RIGHT):
        validMoves.remove(RIGHT)
    if lastMove == RIGHT or not isValidMove(board, LEFT):
        validMoves.remove(LEFT)

    # return random move from list of remaining moves ^ apove ^
    return random.choice(validMoves)

def getLeftTopOFTile(tile_X, tile_Y):
    left = XMARGIN + (tile_X * TILESIZE) + (tile_X - 1)
    top = YMARGIN + (tile_Y * TILESIZE) + (tile_Y - 1)
    # returns tile coordinates as pixel coordinates
    return (left, top)

def getSpotClicked(board, x, y):
    # from the x and y pixel coordinates, get the board coordinates
    for tile_X in range(len(board)):
        for tile_Y in range(len(board[0])):
            left, top = getLeftTopOFTile(tile_X, tile_Y)
            tileRect = pygame.Rect(left, top, TILESIZE, TILESIZE)
            """
            Scine all of the tiles have a width and height that is set in the TILESIZE constant,
            we can create a Rect odj that represnets the space on the board by getting the pixel coords
            of the top left corner of the board space, and then use the collidepoint() Rect method to 
            see if the pixel coords are inside the Rect objects area
            """
            if tileRect.collidepoint(x, y):
                # if returned pixel coordinates are within board space coordinates
                return (tile_X, tile_Y)
                # return as board coordinates
    return (None, None)

def drawTile(tile_X, tile_Y, number, adj_x=0, adj_y=0):
    # draw a tile at board coordinates tile_x and tile_y
    # optionally a few pixels over (determined by adj_x and adj_y)
    left, top = getLeftTopOFTile(tile_X, tile_Y)
    # Draw a rectangle representing the tile on the game surface.
    pygame.draw.rect(DISPLAYSURF, TILECOLOR, (left + adj_x, top + adj_y, TILESIZE, TILESIZE))
    # Render the number onto the tile surface using the BASICFONT font object.
    textSurf = BASICFONT.render(str(number), True, TEXTCOLOR)
    textRect = textSurf.get_rect()
    # Center the text within the tile.
    textRect.center = left + int(TILESIZE / 2) + adj_x, top + int(TILESIZE / 2) + adj_y # left and top TILSIZE divided by 2 gives us center of rect
    # Blit the text surface onto the game surface.
    DISPLAYSURF.blit(textSurf, textRect)

def makeText(text, color, bgcolor, top, left):
    # create the Surface and Rect objects for some text.
    textSurf = BASICFONT.render(text, True, color, bgcolor) # Render text onto a surface with specified color and background color.
    textRect = textSurf.get_rect() # Get the rectangle representing the dimensions and position of the text surface.
    textRect.topleft = (top, left) # Set the top-left corner of the text rectangle to the specified coordinates.

    return (textSurf, textRect) # Return a tuple containing the text surface and text rectangle.

def drawBoard(board, message):
    # Clear the display surface by filling it with the background color.
    DISPLAYSURF.fill(BGCOLOR)
    # Display the message if provided.
    if message:
        textSurf, textRect = makeText(message, MESSAGECOLOR, BGCOLOR, 5, 5)
        DISPLAYSURF.blit(textSurf, textRect)
        # Draw each tile on the board
        for tile_X in range(len(board)):
            for tile_Y in range(len(board[0])):
                if board[tile_X][tile_Y]:
                    drawTile(tile_X, tile_Y, board[tile_X][tile_Y])
    
    # Calculate the left and top positions of the game board.
    left, top = getLeftTopOFTile(0, 0)
    width = BOARDWIDTH * TILESIZE
    height = BOARDHEIGHT * TILESIZE
    # Draw a border around the game board.
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (left - 5, top - 5, width + 11, height + 11), 4)

    # Display the option buttons. the text position never changes
    # this is why they are stored as const vars at the begining of main()
    DISPLAYSURF.blit(RESET_SURF, RESET_RECT)
    DISPLAYSURF.blit(NEW_SURF, NEW_RECT)
    DISPLAYSURF.blit(SOLVE_SURF, SOLVE_RECT)


def slideAnimation(board, direction, message, animationSpeed):
    # this fuction does NOT check if the move is valid
    blank_x, blank_y = getBlankPosition(board)
    if direction == UP:
        move_x = blank_x
        move_y = blank_y + 1
    elif direction == DOWN:
        move_x = blank_x
        move_y = blank_y - 1
    elif direction == LEFT:
        move_x = blank_x + 1
        move_y = blank_y
    elif direction == RIGHT:
        move_x = blank_x - 1
        move_y = blank_y

    # prepare the base surface
    drawBoard(board, message)
    baseSurf = DISPLAYSURF.copy()
    # draw a blank space over the moving tile on the base Surf Surface.
    moveLeft, moveTop = getLeftTopOFTile(move_x, move_y)
    pygame.draw.rect(baseSurf, BGCOLOR, (moveLeft, moveTop, TILESIZE, TILESIZE))

    for i in range(0, TILESIZE, animationSpeed):
        #animate the tile sliding over
        checkForQuit()
        DISPLAYSURF.blit(baseSurf, (0, 0))
        if direction == UP:
            drawTile(move_x, move_y, board[move_x][move_y], 0, -i)
        if direction == DOWN:
            drawTile(move_x, move_y, board[move_x][move_y], 0, i)
        if direction == LEFT:
            drawTile(move_x, move_y, board[move_x][move_y], -i, 0)
        if direction == RIGHT:
            drawTile(move_x, move_y, board[move_x][move_y], i, 0)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def generateNewPuzzle(numSlides):
    '''
    From a starting configuration, make numslides muber
    of moves (and animate these moves).
    '''
    sequence = []
    board = getStartingBoard()
    drawBoard(board, '')
    pygame.display.update()
    pygame.time.wait(500) # 5 millisecond pause
    lastMove = None
    for i in range(numSlides):
        move = getRandomMove(board, lastMove)
        slideAnimation(board, move, 'Generating new puzzle...', int(TILESIZE / 3))
        makeMove(board, move)
        sequence.append(move)
        lastMove = move
    return (board, sequence)

def resetAnimation(board, allMoves):
    # make all of the moves in allMoves reverse.
    revAllMoves = allMoves[:] # gets a copy of the list
    revAllMoves.reverse()
    # list slicing with no number specification creates a slice of the whole list of moves
    # making a copy of the list to store in 'revAllMoves' that when then reverse to solve the puzzule

    for move in revAllMoves:
        if move == UP:
            oppositeMove = DOWN
        elif move == DOWN:
            oppositeMove = UP
        elif move == RIGHT:
            oppositeMove = LEFT
        elif move == LEFT:
            oppositeMove = RIGHT
        slideAnimation(board, oppositeMove, '', int(TILESIZE / 2))
        makeMove(board, oppositeMove)


if __name__ == '__main__':
    main()


