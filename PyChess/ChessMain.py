import pygame as p
import ChessEngine
import ChessAI as ai
##CONSTANTS
p.init()
BOARD_WIDTH = BOARD_HEIGHT = 768
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 60
IMAGES = {}
colors = [p.Color("white"),p.Color("grey")]
highlightCheck = True

##
ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
rowsToRanks = {v: k for k, v in ranksToRows.items()}
filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
colsToFiles = {v: k for k, v in filesToCols.items()}


## images are global
def loadImages():
    pieces = ["wp","bp","wR", "wN", "wB", "wQ", "wK","bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(f"chess_set_3/{piece}.png"),(SQ_SIZE,SQ_SIZE))

def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH,BOARD_HEIGHT))
    p.display.set_caption("Chess")
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    endGameFont = p.font.SysFont("Cambria Math", 30, True, False)
    moveLogFont = p.font.SysFont("Cambria Math", 20, False, False)
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMove()
    moveMade = False
    animated = True
    loadImages() # Only gets loaded once
    running = True
    sqSelected = () # (row, col)
    playerClicks = [] # [(row1, col1), (row2, col2)]
    gameOver = False
    playAsWhite = True # if set to True, then human is playing. Else, AI is playing.
    playAsBlack = True

    while running:
        isHumanTurn = (gs.whiteToMove and playAsWhite) or (not gs.whiteToMove and playAsBlack)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and isHumanTurn:
                    location = p.mouse.get_pos() #(x, y)
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col) or col >= 8:
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            tempMove = validMoves[i]
                            if move == validMoves[i]:
                                if move.isPawnPromotion == True:
                                    tempMove.promotionChoice = promotion(move,screen)


                                gs.makeMove(tempMove)
                                moveMade = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: # Undo
                    gs.undoMove()
                    if not isHumanTurn:
                        gs.undoMove()
                    animated = False
                    moveMade = True
                    gameOver = False
                if e.key == p.K_r: # Reset
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMove()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    gameOver = False
                if e.key == p.K_t: # Test
                    pass
        ## Chess AI
        if not gameOver and not isHumanTurn:
            AIMove = ai.findBestMove(gs, validMoves)
            if AIMove is None:
                AIMove = ai.findRandomMoves(validMoves)
            gs.makeMove(AIMove)
            moveMade = True



        if moveMade:
            validMoves = gs.getValidMove()
            if gs.moveLog and animated:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            moveMade = False
            animated = True

        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)

        if gs.checkMate:
            gameOver = True
            if gs.staleMate:
                text = "Draw"
            else:
                text = "Black wins" if gs.whiteToMove else "White wins"
            drawEndGameText(screen,text,endGameFont)

        clock.tick(MAX_FPS)
        p.display.flip()

## ALL GRAPHICS HERE
def drawGameState(screen, gs, validMoves, sqSelected,moveLogFont):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen,gs.board)
    drawMoveLog(screen,gs,moveLogFont)

def drawBoard(screen):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen,color,p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"):
            ## Highlight
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(150) # transparency
            s.fill(p.Color("lightblue"))
            screen.blit(s, (c*SQ_SIZE, r* SQ_SIZE))


            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    if move.pieceCaptured == "--":
                        s.fill(p.Color("green"))
                        s.set_alpha(50)
                        screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))
                    else:
                        s.fill(p.Color("red"))
                        s.set_alpha(75)
                        screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))
    ## highlight check
    if highlightCheck:
        if gs.inCheck():
            r = gs.whiteKingLocation[0] if gs.whiteToMove else gs.blackKingLocation[0]
            c = gs.whiteKingLocation[1] if gs.whiteToMove else gs.blackKingLocation[1]
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(125)  # transparency
            s.fill(p.Color("red"))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
def drawPieces(screen,board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))
def drawEndGameText(screen, text, font):
    textObject = font.render(text, 0, p.Color("Gray"))
    textLocation = p.Rect(0,0,BOARD_WIDTH,BOARD_HEIGHT).move(BOARD_WIDTH/2 - textObject.get_width()/2, BOARD_HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject,textLocation)
    textObject2 = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject2, textLocation.move(2,2))
def drawMoveLog(screen,gs,font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog),2):
        moveString = f"{str(i//2 + 1)}. {str(moveLog[i])}  "
        if i + 1 < len(moveLog):
            moveString += str(moveLog[i+1])
        moveTexts.append(moveString)
    padding = 5
    lineSpacing = 4
    textY = padding
    for i in range(len(moveTexts)):
        text = str(moveTexts[i])
        textObject = font.render(text, True, p.Color("white"))
        textLocation = moveLogRect.move(5,textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing

    


def animateMove(move,screen,board,clock):
    deltaR = move.endRow - move.startRow
    deltaC = move.endCol - move.startCol
    framesPerSquare = 120 // (abs(deltaR) + abs(deltaC))

    frameCount = (abs(deltaR) + abs(deltaC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r,c = (move.startRow + deltaR * frame/frameCount, move.startCol + deltaC * frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the piece
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != "--":
            if move.isEnpassantMove:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == "b" else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE,SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
## Promotion Choice
def promotion(move,screen):
    c = move.endCol
    r = move.endRow
    promotionChoice = "Q"
    whiteToPromote = True
    if r == 0: # white promote
        promotionChoices = ["wQ","wN","wR","wB"]
        for i in range(0,4):
            color = colors[((i + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, (r + i) * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.fill(p.Color("green"))
            s.set_alpha(30)
            screen.blit(s, (c * SQ_SIZE, (r + i) * SQ_SIZE))
            screen.blit(IMAGES[promotionChoices[i]], p.Rect(c * SQ_SIZE, (r+i) * SQ_SIZE, SQ_SIZE, SQ_SIZE))

    else: # black promote
        promotionChoices = ["bQ", "bN", "bR", "bB"]
        whiteToPromote = False
        for i in range(0, 4):
            color = colors[((i + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, (r - i) * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.fill(p.Color("green"))
            s.set_alpha(30)
            screen.blit(s, (c * SQ_SIZE, (r - i) * SQ_SIZE))
            screen.blit(IMAGES[promotionChoices[i]], p.Rect(c * SQ_SIZE, (r - i) * SQ_SIZE, SQ_SIZE, SQ_SIZE))
    p.display.flip()

    decisionNotMade = True
    while decisionNotMade:
        for e in p.event.get():
            if e.type == p.QUIT:
                decisionNotMade = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # (x, y)
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if c == col:
                    if (row == 0 and whiteToPromote) or (row == 7 and not whiteToPromote):
                        promotionChoice = "Q"
                    elif (row == 1 and whiteToPromote) or (row == 6 and not whiteToPromote):
                        promotionChoice = "N"
                    elif (row == 2 and whiteToPromote) or (row == 5 and not whiteToPromote):
                        promotionChoice = "R"
                    elif (row == 3 and whiteToPromote) or (row == 4 and not whiteToPromote):
                        promotionChoice = "B"
                    else:
                        continue
                    decisionNotMade = False
    return promotionChoice


if __name__ == "__main__":
    main()