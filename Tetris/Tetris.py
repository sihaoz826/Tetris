

import cs112_n21_week4_linter
import math, copy, random

from cmu_112_graphics import *

#################################################
# Helper functions
#################################################

def almostEqual(d1, d2, epsilon=10**-7):
    # note: use math.isclose() outside 15-112 with Python version 3.5 or later
    return (abs(d2 - d1) < epsilon)

import decimal
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))


#################################################
# Helper Function
#################################################

# initialize the grid parameters
def gameDimensions():
    rows = 15
    cols = 10
    cellSize = 20 
    margin = 25
    return (rows, cols, cellSize, margin)

# get the distance between two points
def distance(x0, y0, x1, y1):
    return ((x1-x0)**2 + (y1-y0)**2) ** 0.5

# get the cell bounds of a given row / col
def getCellBounds(app, row, col):
    x0 = app.margin + col * app.cellSize
    x1 = app.margin + (col+1) * app.cellSize
    y0 = app.margin + row * app.cellSize
    y1 = app.margin + (row+1) * app.cellSize
    return (x0, y0, x1, y1)

# check if the point is in the grid
def pointInGrid(app, x, y):
    return ((app.margin <= x <= app.width-app.margin)
            and (app.margin <= y <= app.height-app.margin))

# initialize the board
def makeBoard(rows, cols, color):
    result = make2dList(rows, cols, color)
    return result

# generate a new falling piece
def newFallingPiece(app):
    randomIndex = random.randint(0, len(app.tetrisPieces) - 1)
    app.piece = app.tetrisPieces[randomIndex]
    app.pieceColor = app.tetrisPieceColors[randomIndex]
    app.pieceRow = 0
    pieceLength = len(app.piece[0])
    app.pieceCol = app.cols//2 - pieceLength//2

# check if the falling piece is at a legal place
def fallingPieceIsLegal(app):
    curRow = app.pieceRow
    curCol = app.pieceCol
    rowLength = len(app.piece)
    colLength = len(app.piece[0])
    for row in range(rowLength):
        for col in range(colLength):
            if app.piece[row][col] == True:
                # if the teris piece is out of bounds
                if (curRow == -1 or curRow == app.rows 
                    or curCol == -1 or curCol == app.cols):
                    return False 
                # if the tetris piece encounters a cell that's not blue
                elif (app.board[curRow][curCol] != 'blue'):
                    return False
            curCol += 1
        curCol = app.pieceCol
        curRow += 1
    return True 

# move the falling piece
def moveFallingPiece(app, drow, dcol):
    app.pieceRow += drow
    app.pieceCol += dcol
    # undo the step if not legal
    if fallingPieceIsLegal(app) == False:
        app.pieceRow -= drow
        app.pieceCol -= dcol
        return False
    return True

# make a new 2d list without aliasing
def make2dList(rows, cols, text):
    return [([text] * cols) for row in range(rows)]

# make the falling piece rotate
def rotateFallingPiece(app):
    oldState = app.piece
    oldRows = len(oldState)
    oldCols = len(oldState[0])
    newRows = oldCols
    newCols = oldRows
    endState = [([0] * newCols) for row in range(newRows)]
    for row in range(oldRows):
        for col in range(oldCols):
            endState[oldCols-1-col][row] = oldState[row][col]
    # update the values for the piece
    app.piece = endState
    # update the piece locations
    oldRow = app.pieceRow
    app.pieceRow = oldRow + oldRows//2 - newRows//2
    oldCol = app.pieceCol
    app.pieceCol = oldCol + oldCols//2 - newCols//2
    # if the piece is not at a legal position, undo the action
    if fallingPieceIsLegal(app) == False:
        app.piece = oldState
        app.pieceRow = oldRow
        app.pieceCol = oldCol
        
# place the falling piece on the board
def placeFallingPiece(app):
    curRow = app.pieceRow
    curCol = app.pieceCol
    for row in range(len(app.piece)):
        for col in range(len(app.piece[0])):
            if app.piece[row][col] == True:
                app.board[curRow+row][curCol+col] = app.pieceColor
    removeFullRows(app)

# remove all the stuff when the row is full
def removeFullRows(app):
    newBoard = []
    for row in range(len(app.board)):
        if app.emptyColor in app.board[row]:
            newBoard.append(app.board[row])
    difference = len(app.board) - len(newBoard)
    app.score += difference ** 2
    for i in range(difference):
        newBoard.insert(0, ['blue'] * app.cols)
    app.board = newBoard


#################################################
# Model
#################################################


# initialize all the parameters
def appStarted(app):
    # board parameters
    app.rows, app.cols, app.cellSize, app.margin = gameDimensions()
    app.emptyColor = 'blue'
    app.board = makeBoard(app.rows, app.cols, app.emptyColor)

    # falling piece parameters
    iPiece = [
        [  True,  True,  True,  True ]
    ]

    jPiece = [
        [  True, False, False ],
        [  True,  True,  True ]
    ]

    lPiece = [
        [ False, False,  True ],
        [  True,  True,  True ]
    ]

    oPiece = [
        [  True,  True ],
        [  True,  True ]
    ]

    sPiece = [
        [ False,  True,  True ],
        [  True,  True, False ]
    ]

    tPiece = [
        [ False,  True, False ],
        [  True,  True,  True ]
    ]

    zPiece = [
        [  True,  True, False ],
        [ False,  True,  True ]
    ]

    # piece parameters
    app.tetrisPieces = [ iPiece, jPiece, lPiece, oPiece,
                        sPiece, tPiece, zPiece ]
    app.tetrisPieceColors = [ "red", "yellow", "magenta",
                            "pink", "cyan", "green", "orange" ]
    app.piece = None
    app.pieceColor = None
    app.pieceRow = None
    app.pieceCol = None
    newFallingPiece(app)

    # score and pausing
    app.paused = False
    app.isGameOver = False
    app.score = 0
    app.timerDelay = 100

#################################################
# Controller
#################################################


def keyPressed(app, event):
    # rotation
    if event.key == 'Up':
        rotateFallingPiece(app)
    # move piece
    elif event.key == 'Down':
        moveFallingPiece(app, +1, 0)
    elif event.key == 'Left':
        moveFallingPiece(app, 0, -1)
    elif event.key == 'Right':
        moveFallingPiece(app, 0, +1)
    # pause
    elif event.key == 'p':
        app.paused = not app.paused
    # do a single step
    elif event.key == 's':
        moveFallingPiece(app, +1, 0)
    # reset
    elif event.key == 'r':
        appStarted(app)
    # force it to the very bottom
    elif event.key == 'Space':
        while moveFallingPiece(app, +1, 0):
            pass

def timerFired(app):
    # if puased don't move
    if app.paused == True:
        return 
    # if gameover don't move
    if app.isGameOver == True:
        return 
    # if it is a legal move
    if moveFallingPiece(app, +1, 0) == False:
        if fallingPieceIsLegal(app) == False:
                app.isGameOver = True
        placeFallingPiece(app)
        newFallingPiece(app)

    
#################################################
# View
#################################################

def redrawAll(app, canvas):
    drawBackGround(app, canvas)
    drawBoard(app, canvas)
    drawFallingPiece(app, canvas)
    drawScore(app, canvas)
    # only draw game over when it is over
    if app.isGameOver == True:
        drawWin(app, canvas)

# big orange background
def drawBackGround(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = 'orange')

# draw a single cell
def drawCell(app, canvas, row, col, color):
    (x0, y0, x1, y1) = getCellBounds(app, row, col)
    canvas.create_rectangle(x0, y0, x1, y1, fill = color)

# draw the grid 
def drawBoard(app, canvas):
    for row in range(len(app.board)):
        for col in range(len(app.board[0])):
            drawCell(app, canvas, row, col, app.board[row][col])

# draw single falling piece          
def drawFallingPiece(app, canvas):
    curRow = app.pieceRow
    curCol = app.pieceCol
    for row in range(len(app.piece)):
        for col in range(len(app.piece[0])):
            # draw the cell as other colors when the piece index is True
            if app.piece[row][col] == True:
                drawCell(app, canvas, curRow, curCol, app.pieceColor)
            curCol = curCol + 1
        curCol = app.pieceCol
        curRow = curRow + 1

# draw the score on top
def drawScore(app, canvas):
    canvas.create_text(app.width//2, 0 + app.height/75,
                        text = f'Score: {app.score}',
                        anchor = 'n',
                        font = 'Helvetica 13 bold')

# draw the game over sign 
def drawWin(app, canvas):
    canvas.create_rectangle(app.margin, app.height/5,
                            app.width - app.margin, app.height*2/5,
                            fill = 'black')

    canvas.create_text(app.width/2, app.height/5 + app.height/15,
                        text = 'Game Over!!!',
                        anchor = 'n',
                        fill = 'yellow',
                        font = 'Helvetica 17 bold')

#################################################
# Functions for you to write
#################################################
def playTetris():
    rows, cols, cellSize, margin = gameDimensions()
    wid = margin*2 + cellSize*cols
    hei = margin*2 + cellSize*rows
    runApp(width = wid, height = hei)


#################################################
# main
#################################################

def main():
    cs112_n21_week4_linter.lint()
    playTetris()

if __name__ == '__main__':
    main()
