from abc import ABC, abstractmethod

class Position:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        
    def __eq__(self, other):
        return self.row == other.row and self.col == other.col
    
    def __str__(self):
        return f"{chr(self.col+97)}{8-self.row}"

class Move:
    def __init__(self, piece, start, end, captured=None):
        self.piece = piece
        self.start = start
        self.end = end
        self.captured = captured

class Piece(ABC):
    def __init__(self, color, position):
        self.color = color
        self.position = position
        self.hasMoved = False
        
    def enemy(self, piece):
        return piece and piece.color != self.color

    @abstractmethod
    def get_moves(self, board):
        pass

    @abstractmethod
    def symbol(self):
        pass

class Pawn(Piece):
    def symbol(self):
        return "P" if self.color=="white" else "p"
    
    def get_moves(self, board):
        moves=[]
        direction = -1 if self.color=="white" else 1
        r=self.position.row
        c=self.position.col
        if board.empty(r+direction,c):
            moves.append(Position(r+direction,c))
        if not self.hasMoved and board.empty(r+direction,c) and board.empty(r+2*direction,c):
            moves.append(Position(r+2*direction,c))
        for dc in [-1,1]:
            nr=r+direction
            nc=c+dc
            if board.inside(nr,nc):
                piece = board.get(nr,nc)
                if self.enemy(piece):
                    moves.append(Position(nr,nc))
        return moves

class Rook(Piece):
    def symbol(self):
        return "R" if self.color=="white" else "r"
    
    def get_moves(self, board):
        moves=[]
        dirs=[(1,0),(-1,0),(0,1),(0,-1)]
        for dr,dc in dirs:
            r=self.position.row
            c=self.position.col
            while True:
                r+=dr
                c+=dc
                if not board.inside(r,c):
                    break
                piece=board.get(r,c)
                if piece is None:
                    moves.append(Position(r,c))
                elif self.enemy(piece):
                    moves.append(Position(r,c))
                    break
                else:
                    break
        return moves

class Bishop(Piece):
    def symbol(self):
        return "B" if self.color=="white" else "b"
    
    def get_moves(self, board):
        moves=[]
        dirs=[(1,1),(1,-1),(-1,1),(-1,-1)]
        for dr,dc in dirs:
            r=self.position.row
            c=self.position.col
            while True:
                r+=dr
                c+=dc
                if not board.inside(r,c):
                    break
                piece=board.get(r,c)
                if piece is None:
                    moves.append(Position(r,c))
                elif self.enemy(piece):
                    moves.append(Position(r,c))
                    break
                else:
                    break
        return moves

class Knight(Piece):
    def symbol(self):
        return "N" if self.color=="white" else "n"
    
    def get_moves(self, board):
        moves=[]
        jumps=[(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]
        for dr,dc in jumps:
            r=self.position.row+dr
            c=self.position.col+dc
            if board.inside(r,c):
                piece=board.get(r,c)
                if piece is None or self.enemy(piece):
                    moves.append(Position(r,c))
        return moves

class Queen(Piece):
    def symbol(self):
        return "Q" if self.color=="white" else "q"
    
    def get_moves(self, board):
        return Rook.get_moves(self,board)+Bishop.get_moves(self,board)

class King(Piece):
    def symbol(self):
        return "K" if self.color=="white" else "k"
    
    def get_moves(self, board):
        moves=[]
        dirs=[(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
        for dr,dc in dirs:
            r=self.position.row+dr
            c=self.position.col+dc
            if board.inside(r,c):
                piece=board.get(r,c)
                if piece is None or self.enemy(piece):
                    moves.append(Position(r,c))
        return moves

class Archbishop(Piece):
    def symbol(self):
        return "A" if self.color=="white" else "a"
    
    def get_moves(self, board):
        return Bishop.get_moves(self,board)+Knight.get_moves(self,board)

class Chancellor(Piece):
    def symbol(self):
        return "C" if self.color=="white" else "c"
    
    def get_moves(self, board):
        return Rook.get_moves(self,board)+Knight.get_moves(self,board)

class Camel(Piece):
    def symbol(self):
        return "M" if self.color=="white" else "m"
    
    def get_moves(self, board):
        moves=[]
        jumps=[(3,1),(3,-1),(-3,1),(-3,-1),(1,3),(1,-3),(-1,3),(-1,-3)]
        for dr,dc in jumps:
            r=self.position.row+dr
            c=self.position.col+dc
            if board.inside(r,c):
                piece=board.get(r,c)
                if piece is None or self.enemy(piece):
                    moves.append(Position(r,c))
        return moves

class Wizard(Piece):
    def symbol(self):
        return "W" if self.color=="white" else "w"
    
    def get_moves(self, board):
        moves=[]
        dirs=[(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
        for dr,dc in dirs:
            r=self.position.row
            c=self.position.col
            jumped=False
            while True:
                r+=dr
                c+=dc
                if not board.inside(r,c):
                    break
                piece=board.get(r,c)
                if piece is None:
                    moves.append(Position(r,c))
                elif not jumped:
                    jumped=True
                    r+=dr
                    c+=dc
                    if board.inside(r,c) and (board.empty(r,c) or self.enemy(board.get(r,c))):
                        moves.append(Position(r,c))
                    break
                else:
                    break
        return moves

class CheckersPiece(Piece):
    def symbol(self):
        return "o" if self.color=="white" else "x"
    
    def get_moves(self, board):
        moves=[]
        direction=-1 if self.color=="white" else 1
        r=self.position.row
        c=self.position.col
        for dc in [-1,1]:
            nr=r+direction
            nc=c+dc
            if board.empty(nr,nc):
                moves.append(Position(nr,nc))
            jump_r=r+2*direction
            jump_c=c+2*dc
            if board.inside(jump_r,jump_c):
                middle=board.get(nr,nc)
                if middle and self.enemy(middle) and board.empty(jump_r,jump_c):
                    moves.append(Position(jump_r,jump_c))
        return moves

class CheckersKing(CheckersPiece):
    def symbol(self):
        return "O" if self.color=="white" else "X"
    
    def get_moves(self, board):
        moves=[]
        dirs=[(1,1),(1,-1),(-1,1),(-1,-1)]
        for dr,dc in dirs:
            r=self.position.row+dr
            c=self.position.col+dc
            if board.empty(r,c):
                moves.append(Position(r,c))
        return moves

class Board:
    def __init__(self):
        self.grid=[[None for _ in range(8)] for _ in range(8)]
        
    def inside(self,r,c):
        return 0<=r<8 and 0<=c<8
    
    def get(self,r,c):
        return self.grid[r][c]
    
    def empty(self,r,c):
        return self.inside(r,c) and self.grid[r][c] is None
    
    def place(self,piece):
        r=piece.position.row
        c=piece.position.col
        self.grid[r][c]=piece
        
    def move(self,move):
        sr,sc=move.start.row,move.start.col
        er,ec=move.end.row,move.end.col
        piece=self.grid[sr][sc]
        move.captured=self.grid[er][ec]
        self.grid[er][ec]=piece
        self.grid[sr][sc]=None
        piece.position=Position(er,ec)
        piece.hasMoved=True
        if isinstance(piece,Pawn):
            if piece.color=="white" and er==0:
                self.grid[er][ec]=Queen("white",Position(er,ec))
            if piece.color=="black" and er==7:
                self.grid[er][ec]=Queen("black",Position(er,ec))
        if isinstance(piece,CheckersPiece):
            if piece.color=="white" and er==0:
                self.grid[er][ec]=CheckersKing("white",Position(er,ec))
            if piece.color=="black" and er==7:
                self.grid[er][ec]=CheckersKing("black",Position(er,ec))
                
    def undo(self,move):
        sr,sc=move.start.row,move.start.col
        er,ec=move.end.row,move.end.col
        piece=self.grid[er][ec]
        self.grid[sr][sc]=piece
        self.grid[er][ec]=move.captured
        piece.position=Position(sr,sc)
        
    def setup_chess(self, variant="standard"):
        for i in range(8):
            self.place(Pawn("white", Position(6,i)))
            self.place(Pawn("black", Position(1,i)))
        if variant=="standard":
            back_white=[Rook,Knight,Bishop,Queen,King,Bishop,Knight,Rook]
            back_black=[Rook,Knight,Bishop,Queen,King,Bishop,Knight,Rook]
        elif variant=="new":
            back_white=[Rook,Wizard,Archbishop,Queen,King,Chancellor,Knight,Rook]
            back_black=[Rook,Wizard,Archbishop,Queen,King,Chancellor,Knight,Rook]
        for i,p in enumerate(back_white):
            self.place(p("white", Position(7,i)))
        for i,p in enumerate(back_black):
            self.place(p("black", Position(0,i)))
            
    def setup_checkers(self):
        for r in range(3):
            for c in range(8):
                if (r+c)%2==1:
                    self.place(CheckersPiece("black",Position(r,c)))
        for r in range(5,8):
            for c in range(8):
                if (r+c)%2==1:
                    self.place(CheckersPiece("white",Position(r,c)))
                    
    def print(self, threatened=None, check_pos=None):
        print()
        for r in range(8):
            print(8-r,end=" ")
            for c in range(8):
                piece = self.grid[r][c]
                if piece:
                    symbol = piece.symbol()
                    if check_pos and (r,c)==check_pos:
                        print("!"+symbol,end=" ")
                    elif threatened and (r,c) in threatened:
                        print("!"+symbol,end=" ")
                    else:
                        print(symbol,end=" ")
                else:
                    print(".",end=" ")
            print()
        print("  a b c d e f g h")

class Game:
    def __init__(self):
        self.board=Board()
        mode=input("Choose game (chess/checkers): ")
        if mode=="checkers":
            self.board.setup_checkers()
        else:
            variant=input("Choose chess variant (standard/new): ")
            if variant not in ["standard","new"]:
                variant="standard"
            self.board.setup_chess(variant)
        self.turn="white"
        self.history=[]
        
    def help(self):
        print()
        print("Commands:")
        print("e2 e4 - move")
        print("show e2 - show moves")
        print("undo - undo move")
        print("help - show help")
        print("info - show figure info")
        print("exit - quit")
        
    def parse(self,s):
        col=ord(s[0])-97
        row=8-int(s[1])
        return Position(row,col)
    
    def show_moves(self,piece):
        moves=piece.get_moves(self.board)
        print("Moves:")
        for m in moves:
            print(m,end=" ")
        print()
        
    def threatened_pieces(self, color):
        threatened=[]
        for r in range(8):
            for c in range(8):
                piece=self.board.get(r,c)
                if piece and piece.color==color:
                    for r2 in range(8):
                        for c2 in range(8):
                            enemy=self.board.get(r2,c2)
                            if enemy and enemy.color!=color:
                                moves=enemy.get_moves(self.board)
                                for m in moves:
                                    if (m.row,m.col)==(r,c):
                                        threatened.append((r,c))
        return threatened
    
    def in_check_position(self, color):
        king_pos=None
        for r in range(8):
            for c in range(8):
                piece=self.board.get(r,c)
                if piece and isinstance(piece, King) and piece.color==color:
                    king_pos=(r,c)
                    break
        if king_pos is None:
            return None
        for r2 in range(8):
            for c2 in range(8):
                enemy=self.board.get(r2,c2)
                if enemy and enemy.color!=color:
                    moves=enemy.get_moves(self.board)
                    for m in moves:
                        if (m.row,m.col)==king_pos:
                            return king_pos
        return None
    
    def play(self):
        self.help()
        while True:
            threat=self.threatened_pieces(self.turn)
            check_pos=self.in_check_position(self.turn)
            self.board.print(threatened=threat, check_pos=check_pos)
            if check_pos:
                print("CHECK!")
            print(self.turn,"move")
            cmd=input("> ")
            if cmd=="help":
                self.help()
                continue
            if cmd=="info":
                print()
                print("Chess Figures:")
                print("Pawn (P/p) - forward 1, 2 on first move, captures diagonally, promotion on last rank")
                print("Rook (R/r) - any distance horizontal/vertical")
                print("Knight (N/n) - L-shape jumps")
                print("Bishop (B/b) - any distance diagonal")
                print("Queen (Q/q) - any distance horizontal, vertical, diagonal")
                print("King (K/k) - 1 cell any direction")
                print("Archbishop (A/a) - Bishop + Knight moves")
                print("Chancellor (C/c) - Rook + Knight moves")
                print("Camel (M/m) - jumps 3+1")
                print("Wizard (W/w) - like Queen, can jump over 1 piece once")
                print()
                print("Checkers:")
                print("Checker (o/x) - forward diagonal 1, captures by jumping")
                print("King (O/X) - diagonal 1 any direction, captures")
                continue
            if cmd=="exit":
                break
            if cmd=="undo":
                if self.history:
                    move=self.history.pop()
                    self.board.undo(move)
                    self.turn="white" if self.turn=="black" else "black"
                continue
            if cmd.startswith("show"):
                pos=self.parse(cmd.split()[1])
                piece=self.board.get(pos.row,pos.col)
                if piece:
                    self.show_moves(piece)
                continue
            try:
                a,b=cmd.split()
                start=self.parse(a)
                end=self.parse(b)
            except:
                print("invalid input")
                continue
            piece=self.board.get(start.row,start.col)
            if not piece or piece.color!=self.turn:
                print("wrong piece")
                continue
            moves=piece.get_moves(self.board)
            valid=False
            for m in moves:
                if m==end:
                    valid=True
            if not valid:
                print("illegal move")
                continue
            move=Move(piece,start,end)
            self.board.move(move)
            self.history.append(move)
            self.turn="white" if self.turn=="black" else "black"

game=Game()
game.play()
