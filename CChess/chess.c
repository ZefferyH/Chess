#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <stdlib.h>

// Represents the game board and state
char board[8][8];
int currentPlayer = 0; // 0 for White, 1 for Black

// Castling flags
int whiteKingMoved = 0;
int blackKingMoved = 0;
int whiteRookA_moved = 0;
int whiteRookH_moved = 0;
int blackRookA_moved = 0;
int blackRookH_moved = 0;

// En Passant flag
int enPassantTargetCol = -1; // Column for en passant, or -1 if none

// --- Function Prototypes ---
void initializeBoard();
void printBoard();
int isValidMove(int fromRow, int fromCol, int toRow, int toCol);
int isKingInCheck(int player);
int canPlayerMove(int player);
void makeMove(int fromRow, int fromCol, int toRow, int toCol);
int parseInput(const char* input, int* fromRow, int* fromCol, int* toRow, int* toCol);
int isSquareAttacked(int row, int col, int attackerPlayer);


// --- Piece-specific move validation ---
int isValidPawnMove(int fromRow, int fromCol, int toRow, int toCol);
int isValidRookMove(int fromRow, int fromCol, int toRow, int toCol);
int isValidKnightMove(int fromRow, int fromCol, int toRow, int toCol);
int isValidBishopMove(int fromRow, int fromCol, int toRow, int toCol);
int isValidQueenMove(int fromRow, int fromCol, int toRow, int toCol);
int isValidKingMove(int fromRow, int fromCol, int toRow, int toCol);


/**
 * @brief Sets up the chessboard with pieces in their starting positions.
 */
void initializeBoard() {
    // Use memcpy to avoid string-overflow warnings with strcpy.
    // strcpy adds a null terminator, which overflows our 8-char arrays.
    memcpy(board[0], "rnbqkbnr", 8); // Black pieces
    memcpy(board[1], "pppppppp", 8); // Black pawns
    for (int i = 2; i < 6; i++) {
        memcpy(board[i], "        ", 8); // Empty squares
    }
    memcpy(board[6], "PPPPPPPP", 8); // White pawns
    memcpy(board[7], "RNBQKBNR", 8); // White pieces

    // Reset game state variables
    currentPlayer = 0; // White always starts

    // Reset castling flags
    whiteKingMoved = 0;
    blackKingMoved = 0;
    whiteRookA_moved = 0;
    whiteRookH_moved = 0;
    blackRookA_moved = 0;
    blackRookH_moved = 0;

    // Reset en passant flag
    enPassantTargetCol = -1;
}

/**
 * @brief Prints the current state of the board to the console.
 */
void printBoard() {
    printf("\n  +-----------------+\n");
    for (int i = 0; i < 8; i++) {
        printf("%d | ", 8 - i);
        for (int j = 0; j < 8; j++) {
            printf("%c ", board[i][j]);
        }
        printf("|\n");
    }
    printf("  +-----------------+\n");
    printf("    a b c d e f g h\n");
}


/**
 * @brief Main function to run the chess game loop.
 */
int main() {
    int quitGame = 0;

    do {
        initializeBoard();
        char input[10];
        int fromRow, fromCol, toRow, toCol;

        // This loop runs for a single game
        while (1) {
            printBoard();

            // Check for checkmate or stalemate
            if (isKingInCheck(currentPlayer)) {
                if (!canPlayerMove(currentPlayer)) {
                    printf("Checkmate! %s wins.\n", (currentPlayer == 0) ? "Black" : "White");
                    break; // End the current game
                }
                printf("%s is in check!\n", (currentPlayer == 0) ? "White" : "Black");
            } else if (!canPlayerMove(currentPlayer)) {
                 printf("Stalemate! It's a draw.\n");
                 break; // End the current game
            }

            // Prompt for user input
            printf("%s's turn. Enter move (e.g., e2e4 or exit): ", (currentPlayer == 0) ? "White" : "Black");
            scanf("%s", input);

            if (strcmp(input, "exit") == 0) {
                quitGame = 1; // Set flag to exit after this game
                break;
            }

            // Parse and validate the input
            if (!parseInput(input, &fromRow, &fromCol, &toRow, &toCol)) {
                printf("Invalid input format. Use algebraic notation (e.g., e2e4).\n");
                continue;
            }
            
            // Check if the move is valid
            if (isValidMove(fromRow, fromCol, toRow, toCol)) {
                // Temporarily make the move to check for self-check
                char tempBoard[8][8];
                int tempEnPassant = enPassantTargetCol; // Save en passant state
                memcpy(tempBoard, board, 64);
                
                makeMove(fromRow, fromCol, toRow, toCol);
                
                if (isKingInCheck(currentPlayer)) {
                    printf("Invalid move: this would leave your king in check.\n");
                    memcpy(board, tempBoard, 64); // Revert the move
                    enPassantTargetCol = tempEnPassant; // Revert en passant state
                } else {
                    // Pawn Promotion
                    char piece = board[toRow][toCol];
                    if ( (piece == 'P' && toRow == 0) || (piece == 'p' && toRow == 7) ) {
                        printf("Pawn promotion! Enter Q, R, B, or N: ");
                        char promo;
                        scanf(" %c", &promo);
                        promo = (currentPlayer == 0) ? toupper(promo) : tolower(promo);
                        if (promo == 'Q' || promo == 'R' || promo == 'B' || promo == 'N' ||
                            promo == 'q' || promo == 'r' || promo == 'b' || promo == 'n') {
                            board[toRow][toCol] = promo;
                        } else {
                            board[toRow][toCol] = (currentPlayer == 0) ? 'Q' : 'q'; // Default to Queen
                        }
                    }
                    currentPlayer = 1 - currentPlayer; // Switch player
                }
            } else {
                printf("Invalid move. Please try again.\n");
            }
        } // End of single game loop

        if (quitGame) {
            break; // Exit the do-while loop
        }

        // Ask to play again
        printf("\nPlay again? (y/n): ");
        char playAgainChoice;
        scanf(" %c", &playAgainChoice);
        
        // Clear the input buffer in case the user types more than one character
        while (getchar() != '\n'); 

        if (playAgainChoice != 'y' && playAgainChoice != 'Y') {
            quitGame = 1;
        }

    } while (!quitGame);
    
    printf("\nThanks for playing!\n");
    return 0;
}

/**
 * @brief Parses algebraic notation (e.g., "e2e4") into board coordinates.
 * @return 1 on success, 0 on failure.
 */
int parseInput(const char* input, int* fromRow, int* fromCol, int* toRow, int* toCol) {
    if (strlen(input) != 4) return 0;

    *fromCol = tolower(input[0]) - 'a';
    *fromRow = '8' - input[1];
    *toCol = tolower(input[2]) - 'a';
    *toRow = '8' - input[3];

    // Basic bounds check
    if (*fromRow < 0 || *fromRow > 7 || *fromCol < 0 || *fromCol > 7 ||
        *toRow < 0 || *toRow > 7 || *toCol < 0 || *toCol > 7) {
        return 0;
    }

    return 1;
}

/**
 * @brief Checks if a move is valid according to chess rules.
 * @return 1 if valid, 0 otherwise.
 */
int isValidMove(int fromRow, int fromCol, int toRow, int toCol) {
    char piece = board[fromRow][fromCol];
    char targetPiece = board[toRow][toCol];

    // 1. Check if there is a piece to move
    if (piece == ' ') return 0;

    // 2. Check if the piece belongs to the current player
    if ((currentPlayer == 0 && islower(piece)) || (currentPlayer == 1 && isupper(piece))) {
        return 0;
    }

    // 3. Check if the destination square has a friendly piece
    if (targetPiece != ' ' && ((isupper(piece) && isupper(targetPiece)) || (islower(piece) && islower(targetPiece)))) {
        return 0;
    }
    
    // 4. Check piece-specific rules
    switch (toupper(piece)) {
        case 'P': return isValidPawnMove(fromRow, fromCol, toRow, toCol);
        case 'R': return isValidRookMove(fromRow, fromCol, toRow, toCol);
        case 'N': return isValidKnightMove(fromRow, fromCol, toRow, toCol);
        case 'B': return isValidBishopMove(fromRow, fromCol, toRow, toCol);
        case 'Q': return isValidQueenMove(fromRow, fromCol, toRow, toCol);
        case 'K': return isValidKingMove(fromRow, fromCol, toRow, toCol);
        default: return 0;
    }
}

/**
 * @brief Makes a move on the board, updating piece positions.
 */
void makeMove(int fromRow, int fromCol, int toRow, int toCol) {
    char piece = board[fromRow][fromCol];

    // Check for special move conditions BEFORE the board state changes
    int isEnPassantCapture = (toupper(piece) == 'P' && abs(fromCol - toCol) == 1 && board[toRow][toCol] == ' ');
    int isCastle = (toupper(piece) == 'K' && abs(fromCol - toCol) == 2);

    // Standard move
    board[toRow][toCol] = piece;
    board[fromRow][fromCol] = ' ';

    // Handle secondary effects of special moves
    if (isEnPassantCapture) {
        if (currentPlayer == 0) { // White captured a black pawn
            board[toRow + 1][toCol] = ' '; 
        } else { // Black captured a white pawn
            board[toRow - 1][toCol] = ' ';
        }
    } else if (isCastle) {
        // Kingside
        if (toCol == 6) {
            board[fromRow][5] = board[fromRow][7];
            board[fromRow][7] = ' ';
        }
        // Queenside
        if (toCol == 2) {
            board[fromRow][3] = board[fromRow][0];
            board[fromRow][0] = ' ';
        }
    }

    // Update en passant target for the NEXT turn. This must be done after handling the capture.
    if (toupper(piece) == 'P' && abs(fromRow - toRow) == 2) {
        enPassantTargetCol = fromCol;
    } else {
        enPassantTargetCol = -1;
    }

    // Update castling flags if king or rook moves from its starting position
    if (piece == 'K') whiteKingMoved = 1;
    if (piece == 'k') blackKingMoved = 1;
    if (piece == 'R' && fromRow == 7 && fromCol == 0) whiteRookA_moved = 1;
    if (piece == 'R' && fromRow == 7 && fromCol == 7) whiteRookH_moved = 1;
    if (piece == 'r' && fromRow == 0 && fromCol == 0) blackRookA_moved = 1;
    if (piece == 'r' && fromRow == 0 && fromCol == 7) blackRookH_moved = 1;
}

/**
 * @brief Checks if a square is under attack by a given player.
 * @return 1 if attacked, 0 otherwise.
 */
int isSquareAttacked(int row, int col, int attackerPlayer) {
    for (int i = 0; i < 8; i++) {
        for (int j = 0; j < 8; j++) {
            char piece = board[i][j];
            if (piece != ' ' && ((attackerPlayer == 0 && isupper(piece)) || (attackerPlayer == 1 && islower(piece)))) {
                // Temporarily switch player to check move validity for the attacker
                int originalPlayer = currentPlayer;
                currentPlayer = attackerPlayer;
                if (isValidMove(i, j, row, col)) {
                    currentPlayer = originalPlayer; // Restore player
                    return 1; // Square is attacked
                }
                currentPlayer = originalPlayer; // Restore player
            }
        }
    }
    return 0;
}


/**
 * @brief Checks if a player's king is currently under attack.
 * @return 1 if in check, 0 otherwise.
 */
int isKingInCheck(int player) {
    int kingRow, kingCol = -1;
    char king = (player == 0) ? 'K' : 'k';
    int attackerPlayer = 1 - player;

    // Find the king
    for (int i = 0; i < 8; i++) {
        for (int j = 0; j < 8; j++) {
            if (board[i][j] == king) {
                kingRow = i;
                kingCol = j;
                break;
            }
        }
        if (kingCol != -1) break;
    }
    
    return isSquareAttacked(kingRow, kingCol, attackerPlayer);
}

/**
 * @brief Checks if a player has any valid moves available.
 * @return 1 if a valid move exists, 0 otherwise.
 */
int canPlayerMove(int player) {
    char tempBoard[8][8];
    int tempEnPassant;

    for (int r1 = 0; r1 < 8; r1++) {
        for (int c1 = 0; c1 < 8; c1++) {
            char piece = board[r1][c1];
            if (piece != ' ' && ((player == 0 && isupper(piece)) || (player == 1 && islower(piece)))) {
                for (int r2 = 0; r2 < 8; r2++) {
                    for (int c2 = 0; c2 < 8; c2++) {
                        if (isValidMove(r1, c1, r2, c2)) {
                            // Simulate the move
                            memcpy(tempBoard, board, 64);
                            tempEnPassant = enPassantTargetCol;
                            makeMove(r1, c1, r2, c2);

                            // If the move gets the king out of check, it's a valid move
                            if (!isKingInCheck(player)) {
                                memcpy(board, tempBoard, 64); // Revert
                                enPassantTargetCol = tempEnPassant;
                                return 1;
                            }
                            
                            memcpy(board, tempBoard, 64); // Revert
                            enPassantTargetCol = tempEnPassant;
                        }
                    }
                }
            }
        }
    }
    return 0;
}


// --- Piece Specific Validation Functions ---

int isValidPawnMove(int fromRow, int fromCol, int toRow, int toCol) {
    char piece = board[fromRow][fromCol];
    char targetPiece = board[toRow][toCol];
    int direction = (isupper(piece)) ? -1 : 1; // White moves up (-1), Black moves down (+1)

    // Standard 1-step forward move
    if (fromCol == toCol && toRow == fromRow + direction && targetPiece == ' ') {
        return 1;
    }

    // 2-step initial move
    int startRow = (isupper(piece)) ? 6 : 1;
    if (fromRow == startRow && fromCol == toCol && toRow == fromRow + 2 * direction && targetPiece == ' ' && board[fromRow + direction][fromCol] == ' ') {
        return 1;
    }

    // Capture move
    if (abs(fromCol - toCol) == 1 && toRow == fromRow + direction && targetPiece != ' ') {
        return 1;
    }

    // En passant capture
    if (enPassantTargetCol != -1 && toCol == enPassantTargetCol) {
        int enPassantRow = (isupper(piece)) ? 2 : 5; // The row the pawn must land on
        int pawnOnCorrectRank = (isupper(piece)) ? (fromRow == 3) : (fromRow == 4);

        if (pawnOnCorrectRank && toRow == enPassantRow && abs(fromCol-toCol) == 1 && targetPiece == ' ') {
            return 1;
        }
    }

    return 0;
}

int isValidRookMove(int fromRow, int fromCol, int toRow, int toCol) {
    if (fromRow != toRow && fromCol != toCol) return 0; // Must be horizontal or vertical

    // Check for pieces in the path
    if (fromRow == toRow) { // Horizontal move
        int step = (toCol > fromCol) ? 1 : -1;
        for (int c = fromCol + step; c != toCol; c += step) {
            if (board[fromRow][c] != ' ') return 0;
        }
    } else { // Vertical move
        int step = (toRow > fromRow) ? 1 : -1;
        for (int r = fromRow + step; r != toRow; r += step) {
            if (board[r][fromCol] != ' ') return 0;
        }
    }
    return 1;
}

int isValidKnightMove(int fromRow, int fromCol, int toRow, int toCol) {
    int dr = abs(fromRow - toRow);
    int dc = abs(fromCol - toCol);
    return (dr == 2 && dc == 1) || (dr == 1 && dc == 2);
}

int isValidBishopMove(int fromRow, int fromCol, int toRow, int toCol) {
    if (abs(fromRow - toRow) != abs(fromCol - toCol)) return 0; // Must be diagonal

    // Check for pieces in the path
    int r_step = (toRow > fromRow) ? 1 : -1;
    int c_step = (toCol > fromCol) ? 1 : -1;
    for (int r = fromRow + r_step, c = fromCol + c_step; r != toRow; r += r_step, c += c_step) {
        if (board[r][c] != ' ') return 0;
    }
    return 1;
}

int isValidQueenMove(int fromRow, int fromCol, int toRow, int toCol) {
    // A queen's move is valid if it's a valid rook or bishop move
    return isValidRookMove(fromRow, fromCol, toRow, toCol) || isValidBishopMove(fromRow, fromCol, toRow, toCol);
}

int isValidKingMove(int fromRow, int fromCol, int toRow, int toCol) {
    int dr = abs(fromRow - toRow);
    int dc = abs(fromCol - toCol);
    
    // Standard one-square move
    if (dr <= 1 && dc <= 1) {
        return 1;
    }
    
    // --- Castling Logic ---
    if (dr == 0 && dc == 2 && !isKingInCheck(currentPlayer)) {
        if (currentPlayer == 0) { // White's turn
            if (whiteKingMoved) return 0;
            // Kingside castling (e1g1)
            if (toCol == 6) { 
                if (whiteRookH_moved || board[7][5] != ' ' || board[7][6] != ' ') return 0;
                if (isSquareAttacked(7, 5, 1) || isSquareAttacked(7, 6, 1)) return 0;
                return 1;
            }
            // Queenside castling (e1c1)
            if (toCol == 2) {
                 if (whiteRookA_moved || board[7][1] != ' ' || board[7][2] != ' ' || board[7][3] != ' ') return 0;
                 if (isSquareAttacked(7, 2, 1) || isSquareAttacked(7, 3, 1)) return 0;
                 return 1;
            }
        } else { // Black's turn
            if (blackKingMoved) return 0;
            // Kingside castling (e8g8)
            if (toCol == 6) {
                if (blackRookH_moved || board[0][5] != ' ' || board[0][6] != ' ') return 0;
                if (isSquareAttacked(0, 5, 0) || isSquareAttacked(0, 6, 0)) return 0;
                return 1;
            }
            // Queenside castling (e8c8)
            if (toCol == 2) {
                if (blackRookA_moved || board[0][1] != ' ' || board[0][2] != ' ' || board[0][3] != ' ') return 0;
                if (isSquareAttacked(0, 2, 0) || isSquareAttacked(0, 3, 0)) return 0;
                return 1;
            }
        }
    }
    
    return 0;
}

