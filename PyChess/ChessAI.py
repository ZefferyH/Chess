import random
pieceScore = {"K": 0, "Q": 24, "R": 12, "B": 8, "N": 8, "p": 2}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3

KnightScore = [
    [-4, -2, 0, -2, -2, 0, -2, -4],
    [-2, 0, 0, 0, 0, 0, 0, -2],
    [-2, 1, 0, 1, 1, 0, 0, -2],
    [0, 1, 1, 2, 2, 1, 1, 0],
    [0, 1, 1, 2, 2, 1, 1, 0],
    [-2, 0, 0, 1, 1, 0, 0, -2],
    [-2, 0, 0, 0, 0, 0, 0, -2],
    [-4, -2, 0, -2, -2, 0, -2, -4]
]
RookScore = [
[0,0,0,2,2,0,0,0],
[1,1,1,1,1,1,1,1],
[0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0],
[1,1,1,1,1,1,1,1],
[0,0,0,2,2,0,0,0]
    ]
PawnScoreW = [
[0,0,0,0,0,0,0,0],
[6,6,6,6,6,6,6,6],
[3,3,3,3,3,3,3,3],
[0,0,0,3,3,0,0,0],
[0,0,2,3,3,0,0,0],
[1,0,0,0,0,0,0,1],
[1,1,1,0,0,1,1,1],
[0,0,0,0,0,0,0,0]
    ]
PawnScoreB = [
[0,0,0,0,0,0,0,0],
[1,1,1,0,0,1,1,1],
[1,0,0,0,0,0,0,1],
[0,0,2,3,3,0,0,0],
[0,0,0,3,3,0,0,0],
[3,3,3,3,3,3,3,3],
[6,6,6,6,6,6,6,6],
[0,0,0,0,0,0,0,0]
    ]
BishopScore = [
    [-2, 0, 0, 0, 0, 0, 0, -2],
    [0, 2, 0, 1, 1, 0, 2, 0],
    [0, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 3, 2, 2, 3, 0, 0],
    [0, 0, 3, 2, 2, 3, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 0],
    [0, 2, 0, 1, 1, 0, 2, 0],
    [-2, 0, 0, 0, 0, 0, 0, -2]
]
QueenScore = [
[-4,0,0,0,0,0,0,-4],
[-1,0,1,0,0,0,0,-1],
[-1,1,0,0,0,0,0,-1],
[1,0,0,0,0,0,0,0],
[1,0,0,0,0,0,0,0],
[-1,1,0,0,0,0,0,-1],
[-1,0,1,0,0,0,0,-1],
[-4,0,0,0,0,0,0,-4]
    ]
KingScoreW = [
[-6,-6,-6,-6,-6,-6,-6,-6],
[-5,-5,-5,-5,-5,-5,-5,-5],
[-4,-4,-4,-4,-4,-4,-4,-4],
[-3,-3,-3,-3,-3,-3,-3,-3],
[-2,-2,-2,-2,-2,-2,-2,-2],
[-1,-1,-1,-1,-1,-1,-1,-1],
[1,0,-1,0,0,-1,0,1],
[2,3,0,0,0,0,3,2]
    ]
KingScoreB = [
[2,3,0,0,0,0,3,2],
[1,0,-1,0,0,-1,0,1],
[-1,-1,-1,-1,-1,-1,-1,-1],
[-2,-2,-2,-2,-2,-2,-2,-2],
[-3,-3,-3,-3,-3,-3,-3,-3],
[-4,-4,-4,-4,-4,-4,-4,-4],
[-5,-5,-5,-5,-5,-5,-5,-5],
[-6,-6,-6,-6,-6,-6,-6,-6],
    ]

def findRandomMoves(validMoves):
    return validMoves[random.randint(0,len(validMoves)-1)] # (inclusive, inclusive)

def findBestMove(gs, validMoves):
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    findMoveNegaMaxAlphaBeta(gs, validMoves,DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    return nextMove

def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    maxScore= -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMove()
        random.shuffle(nextMoves)
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore

def scoreBoard(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.staleMate:
        return STALEMATE
    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]


            if square != "--":
                piecePositionScore = 0
                if square[0] == "w":

                    if square[1] == "N":
                        piecePositionScore = KnightScore[row][col]
                    elif square[1] == "K":
                        piecePositionScore = KingScoreW[row][col]
                    elif square[1] == "B":
                        piecePositionScore = BishopScore[row][col]
                    elif square[1] == "R":
                        piecePositionScore = RookScore[row][col]
                    elif square[1] == "p":
                        piecePositionScore = PawnScoreW[row][col]
                    elif square[1] == "Q":
                        piecePositionScore = QueenScore[row][col]
                    score += (pieceScore[square[1]] + piecePositionScore)
                elif square[0] == "b":
                    if square[1] == "N":
                        piecePositionScore = KnightScore[row][col]
                    elif square[1] == "K":
                        piecePositionScore = KingScoreB[row][col]
                    elif square[1] == "B":
                        piecePositionScore = BishopScore[row][col]
                    elif square[1] == "R":
                        piecePositionScore = RookScore[row][col]
                    elif square[1] == "p":
                        piecePositionScore = PawnScoreB[row][col]
                    elif square[1] == "Q":
                        piecePositionScore = QueenScore[row][col]
                    score -= (pieceScore[square[1]] + piecePositionScore)
    return score

