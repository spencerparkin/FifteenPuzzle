# FifteenPuzzle.py

import argparse
import os
import random
import time
import copy
import math

class Node:
    def __init__( self, number ):
        self.number = number
        self.adj_node = {}

def ExplorePuzzle( puzzle, max_depth, cur_depth = 1, move_path = [] ):
    for move in [ 'u', 'd', 'l', 'r' ]:
        opposite_move = puzzle.OppositeMove( move )
        if puzzle.empty_node.adj_node[ opposite_move ]:
            puzzle.MakeMove( move )
            move_path.append( move )
            yield( puzzle, move_path )
            if cur_depth < max_depth:
                yield from ExplorePuzzle( puzzle, max_depth, cur_depth + 1 )
            puzzle.MakeMove( opposite_move )
            move_path.pop()

class Puzzle:
    def __init__( self, rows = 4, cols = 4 ):
        self.rows = rows
        self.cols = cols
        self.lattice = []
        number = 1
        for i in range( rows ):
            lattice_column = []
            for j in range( cols ):
                node = Node( number )
                lattice_column.append( node )
                number += 1
            self.lattice.append( lattice_column )
        for i in range( rows ):
            for j in range( cols ):
                self.lattice[i][j].adj_node['u'] = self.lattice[i-1][j] if i > 0 else None
                self.lattice[i][j].adj_node['d'] = self.lattice[i+1][j] if i < rows - 1 else None
                self.lattice[i][j].adj_node['l'] = self.lattice[i][j-1] if j > 0 else None
                self.lattice[i][j].adj_node['r'] = self.lattice[i][j+1] if j < cols - 1 else None
        self.empty_node = self.lattice[ self.rows - 1 ][ self.cols - 1 ]
    
    def Print( self ):
        largest_number = self.rows * self.cols
        largest_number_len = len( str( largest_number ) )
        row_sep_str = '-' * ( largest_number_len + 3 ) * self.cols + '-'
        for i in range( self.rows ):
            print( row_sep_str )
            row_str = ''
            for j in range( self.cols ):
                node = self.lattice[i][j]
                number_str = str( node.number ) if node is not self.empty_node else ''
                number_str_len = len( number_str )
                pad_size = largest_number_len - number_str_len
                row_str += '| ' + ( pad_size * ' ' ) + number_str + ' '
            row_str += '|'
            print( row_str )
        print( row_sep_str )
        
    def ExecCommand( self, command ):
        if 'udlr'.find( command ) >= 0 and len( command ) == 1:
            self.MakeMove( command )
        elif command == 'solve':
            return self.Solve()
        elif command == 'scramble':
            self.Scramble()
            
    def Scramble( self ):
        for i in range( 10 * self.rows * self.cols ):
            while True:
                random_move = [ 'u', 'd', 'l', 'r' ][ random.randint( 0, 3 ) ]
                if self.MakeMove( random_move ):
                    break
    
    def Clone( self ):
        clone = copy.deepcopy( self )
        return clone
    
    def IsSolved( self ):
        return True if self.FirstUnsolvedNumber() == self.rows * self.cols + 1 else False
    
    def FirstUnsolvedNumber( self ):
        number = 1
        for i in range( self.rows ):
            for j in range( self.cols ):
                node = self.lattice[i][j]
                if node.number != number:
                    return number
                number += 1
        return number
    
    def CalcNumberCoords( self, number ):
        return( math.floor( ( number - 1 ) / self.cols ), ( number - 1 ) % self.cols )
    
    def FindNumberCoords( self, number ):
        for i in range( self.rows ):
            for j in range( self.cols ):
                node = self.lattice[i][j]
                if node.number == number:
                    return( i, j )
        return None
    
    def TaxiCabDistance( self, number ):
        solve_coords = self.CalcNumberCoords( number )
        coords = self.FindNumberCoords( number )
        distance = abs( coords[0] - solve_coords[0] ) + abs( coords[1] - solve_coords[1] )
        return distance
    
    # This was my initial attempt, and it sucks.  There's got to be a smarter way.
    def Solve( self ):
        move_sequence = []
        puzzle = self.Clone()
        search_depth = 7
        while not puzzle.IsSolved():
            best_unsolved_number = puzzle.FirstUnsolvedNumber()
            smallest_distance = puzzle.TaxiCabDistance( best_unsolved_number )
            print( 'unsolved number: ' + str( best_unsolved_number ) )
            print( 'distance: ' + str( smallest_distance ) )
            print( 'search depth: ' + str( search_depth ) )
            sub_sequence = []
            for state in ExplorePuzzle( puzzle, search_depth ):
                unsolved_number = state[0].FirstUnsolvedNumber()
                if unsolved_number > best_unsolved_number:
                    best_unsolved_number = unsolved_number
                    sub_sequence = copy.deepcopy( state[1] )
                    search_depth = 7
                elif unsolved_number == best_unsolved_number:
                    distance = puzzle.TaxiCabDistance( best_unsolved_number )
                    if distance < smallest_distance:
                        smallest_distance = distance
                        sub_sequence = copy.deepcopy( state[1] )
            if len( sub_sequence ) == 0:
                search_depth += 1
            for move in sub_sequence:
                puzzle.MakeMove( move )
            move_sequence += sub_sequence
        return move_sequence
    
    def OppositeMove( self, move ):
        if move == 'u':
            return 'd'
        if move == 'd':
            return 'u'
        if move == 'l':
            return 'r'
        if move == 'r':
            return 'l'
        return None
    
    def MakeMove( self, move ):
        opposite_move = self.OppositeMove( move )
        adj_node = self.empty_node.adj_node[ opposite_move ]
        if not adj_node:
            return False
        self.empty_node.number = adj_node.number
        self.empty_node = adj_node
        self.empty_node.number = self.rows * self.cols
        return True
    
def Main():
    
    parser = argparse.ArgumentParser( description = 'Play with the 15-puzzle or a similar puzzle of some other set of dimensions.' )
    
    parser.add_argument( '--rows', help = 'Specify the number of rows in the lattice of the puzzle; 4 is the default.', type = int )
    parser.add_argument( '--cols', help = 'Specify the number of columns in the lattice of the puzzle; 4 is the default.', type = int )
    
    args = parser.parse_args()
    
    puzzle = Puzzle( args.rows if args.rows else 4, args.cols if args.cols else 4 )
    puzzle.Print()
    
    while True:
        command = input( 'command: ' )
        if command == 'exit':
            break
        command_queue = [ command ]
        while len( command_queue ) > 0:
            command = command_queue[0]
            del command_queue[0]
            command_sequence = puzzle.ExecCommand( command )
            if type( command_sequence ) is list:
                command_queue += command_sequence
            puzzle.Print()
    
if __name__ == '__main__':
    Main()

# FifteenPuzzle.py