import copy

import numpy as np
##
class GameState:

    def __init__(self):
        # board is a 8x8 matrix
        self.board = np.array([
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ])
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = () # (row,column)
        self.currentCastlingRight = CastleRights(True,True,True,True)
        self.moveLog = []
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.whiteKingSide,
                                             self.currentCastlingRight.blackKingSide,
                                             self.currentCastlingRight.whiteQueenSide,
                                             self.currentCastlingRight.blackQueenSide)]
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        if move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
        if move.isPawnPromotion:  # Pawn Promotion
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + move.promotionChoice
        if move.isEnpassantMove: # En passant
            self.board[move.startRow][move.endCol] = '--' # Capture
        ## update enpassantPossible = ()
        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)

        else:
            self.enpassantPossible = ()

        ## castle move:
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: # kingSide
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1] = "--"
            else: # queenSide
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = "--"

        ## update castling rights
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.whiteKingSide,
                                             self.currentCastlingRight.blackKingSide,
                                             self.currentCastlingRight.whiteQueenSide,
                                             self.currentCastlingRight.blackQueenSide))
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

            ## undo two square pawn move
            if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()
            ## undo en passant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            else: # check last move
                if self.moveLog:
                    lastMove = self.moveLog[-1]
                    if lastMove.pieceMoved[1] == "p" and abs(lastMove.startRow - lastMove.endRow) == 2:
                        self.enpassantPossible = ((lastMove.startRow + lastMove.endRow) // 2, lastMove.startCol)


            ## undo castling rights
            self.castleRightsLog.pop()
            castleRights = copy.deepcopy(self.castleRightsLog[-1])
            self.currentCastlingRight = castleRights
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: # kingSide
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol - 1] = "--"
                else: # queenSide
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = "--"
            self.checkMate = False
            self.staleMate = False

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.whiteQueenSide = False
            self.currentCastlingRight.whiteKingSide = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRight.blackQueenSide = False
            self.currentCastlingRight.blackKingSide = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0: # left rook
                    self.currentCastlingRight.whiteQueenSide = False
                elif move.startCol == 7: # right rook
                    self.currentCastlingRight.whiteKingSide = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0: # left rook
                    self.currentCastlingRight.blackQueenSide = False
                elif move.startCol == 7: # right rook
                    self.currentCastlingRight.blackKingSide = False
        if move.pieceCaptured == "wR":
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRight.whiteQueenSide = False
                elif move.endCol == 7:
                    self.currentCastlingRight.whiteKingSide = False
        elif move.pieceCaptured == "bR":
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRight.blackQueenSide = False
                elif move.endCol == 7:
                    self.currentCastlingRight.blackKingSide = False
    def getValidMove(self):
        tempEnpassantPossible = self.enpassantPossible
        castleRights = CastleRights(self.currentCastlingRight.whiteKingSide,
                                             self.currentCastlingRight.blackKingSide,
                                             self.currentCastlingRight.whiteQueenSide,
                                             self.currentCastlingRight.blackQueenSide)
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0],self.whiteKingLocation[1],moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0],self.blackKingLocation[1],moves)
        for i in range(len(moves)-1, -1, -1): #whenever removing, do it backwards
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True

            else:
                self.staleMate = True

        else:
            self.checkMate = False
            self.staleMate = False
        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = castleRights
        return moves


    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r,c,moves)
        return moves
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:
            if self.board[r-1][c] == "--": # one square forward
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--": # two square forward
                    moves.append(Move((r,c), (r-2,c),self.board))
            if c-1 >= 0: # capture left
                if self.board[r-1][c-1][0] == "b":
                    moves.append(Move((r,c), (r-1,c-1), self.board))
                elif (r-1,c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r-1, c-1), self.board, isEnpassantMove=True))
            if c+1 <= 7: # capture right
                if self.board[r - 1][c + 1][0] == "b":
                    moves.append(Move((r,c),(r-1,c+1),self.board))
                elif (r-1,c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r-1, c+1), self.board, isEnpassantMove=True))
        else:
            if self.board[r+1][c] == "--":  # one square forward
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":  # two square forward
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:
                if self.board[r + 1][c + 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True))
    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0),(0,-1),(1,0),(0,1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':
                        moves.append(Move((r,c),(endRow,endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r,c),(endRow, endCol),self.board))
                        break
                    else: #friendly
                        break
                else:
                    break #outofrange
    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1),(-2, 1),(-1, -2), (1, -2),(-1, 2), (1,2), (2,-1),(2,1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r,c),(endRow,endCol), self.board))
    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # friendly
                        break
                else:
                    break  # outofrange
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (1,1), (1,-1),(-1,-1),(-1,1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endRow = r + directions[i][0]
            endCol = c + directions[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))


    def getCastleMoves(self,r,c,moves):
        if self.squareUnderAttack(r,c):
            return
        if (self.whiteToMove and self.currentCastlingRight.whiteKingSide) or (not self.whiteToMove and self.currentCastlingRight.blackKingSide):
            self.getKingsideCastleMoves(r,c,moves)
        if (self.whiteToMove and self.currentCastlingRight.whiteQueenSide) or (not self.whiteToMove and self.currentCastlingRight.blackQueenSide):
            self.getQueensideCastleMoves(r,c, moves)
    def getKingsideCastleMoves(self,r,c,moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c + 2):
                moves.append(Move((r,c),(r,c+2),self.board, isCastleMove = True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--":
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
               moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove = True))


class CastleRights():
    def __init__(self, whiteKingSide, blackKingSide, whiteQueenSide, blackQueenSide):
        self.whiteKingSide = whiteKingSide
        self.blackKingSide = blackKingSide
        self.whiteQueenSide = whiteQueenSide
        self.blackQueenSide = blackQueenSide
    def __repr__(self):
        return f"{self.whiteKingSide, self.blackKingSide, self.whiteQueenSide, self.blackQueenSide}"


class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}
    def __init__(self, startSq, endSq, board, isEnpassantMove = False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        ## Promotion
        self.isPawnPromotion = ((self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7))
        self.promotionChoice = "Q" # "Q", "B", "R", or "N"
        ## En passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"
        ##Castle
        self.isCastleMove = isCastleMove



    def __eq__(self, other):
        if isinstance(other, Move):
            if self.moveID == other.moveID:
                return True
        return False
    def __repr__(self):
        startsqr = self.colsToFiles[self.startCol] + self.rowsToRanks[self.startRow]
        endsqr = self.colsToFiles[self.endCol] + self.rowsToRanks[self.endRow]

        ## Castle
        if self.isCastleMove:
            returnText = "O-O" if self.endCol == 6 else "O-O-O"

        ## Promotion
        elif self.isPawnPromotion:
            if self.pieceCaptured != "--":
                returnText = f"{startsqr[0]}x{endsqr}={self.promotionChoice}"
            else:
                returnText = f"{endsqr}={self.promotionChoice}"

        else:
            if self.pieceCaptured != "--":
                if self.pieceMoved[1] == "p":
                    returnText = startsqr[0] + "x" + endsqr
                else:
                    returnText = self.pieceMoved[1] + "x" + endsqr
            else:
                returnText = endsqr if self.pieceMoved[1] == "p" else self.pieceMoved[1] + endsqr

        return returnText
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    def getRankFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]
