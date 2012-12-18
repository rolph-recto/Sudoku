#!/usr/bin/env python
#Sudoku solver by Rolph Recto

import numpy as np

def CheckRange(val, min, max):
    if val >= min and val <= max: return True
    else: return False

#Sudoku class
#calculates and stores solution grid
class Sudoku:
    #bit-value 11111111
    #used for the default value of cells in internal grid
    ALL_POSSIBLE_VALUES = 511
    BLOCK               = 1
    COLUMN              = 2
    ROW                 = 3

    def __init__(self, known_values=[]):
        #two dimensional grid that contains all possible values for each cell
        #the possible values are encoded as a bitset
        #each possible value is assigned to one bit
        #this internal grid is used to calculate the solution grid
        self._grid = np.array(self.ALL_POSSIBLE_VALUES, ndmin=2)
        self._grid = np.resize(self._grid, (9,9))

        #has the actual correct values for each cell
        self.solution_grid = np.array(-1, ndmin=2)
        self.solution_grid = np.resize(self.solution_grid, (9,9))

        #plug all the known values in the grid
        for row, column, value in known_values:
            self.SetCellValue(row, column, value, False)

    #sets the correct value for the cell
    #calculate argument determines whether to run solving algorithm
    #the only time calculate is false is at initialization,
    #because the user has to call Solve() to solve the grid
    def SetCellValue(self, row, column, value, calculate=True):
        if not CheckRange(value, 1, 9): raise ValueError()

        #converts the decimal value into a binary placeholder
        #example: 3 becomes 000000100; 2 becomes 0000000010
        value_bit = 2**(value-1)

        #get coordinates of cell's block
        block = (int(row/3), int(column/3), )

        #set correct value of the cell
        self._grid[row][column] = value_bit
        self.solution_grid[row][column] = value

        #run solving algorithm:
        #-remove all instances of value in the cell block, column, and row
        #-check if a correct value can be determined for each modified cell or
        #another cell in its block
        if calculate:
            #gather list of cells from which to remove value
            cells = []

            #get all cells from the cell's block
            for y in range(3):
                for x in range(3):
                    cell = (block[0]*3 + x, block[1]*3 + y)
                    #make sure the list doesn't include solved cells!
                    if self.IsCellSolved(cell[0], cell[1]) == -1:
                        cells.append(cell)

            #get all cells from the cell's rows and columns
            for index in range(9):
                cell1 = (index, column, )
                cell2 = (row, index, )

                #only add the cell if it isn't on the list already
                #or if it isn't solved yet
                if cells.count(cell1) == 0:
                    if self.IsCellSolved(cell1[0], cell1[1]) == -1:
                        cells.append(cell1)

                if cells.count(cell2) == 0:
                    if self.IsCellSolved(cell2[0], cell2[1]) == -1:
                        cells.append(cell2)

            #remove value from all cells in the list
            #value_XOR sets all bits to 1 EXCEPT the value bit
            value_bit_XOR = self.ALL_POSSIBLE_VALUES^value_bit

            #perform bitwise AND operation to remove value bit
            #Example:
            #grid value     : 1011011111
            #value_XOR      : 1111111101
            #grid&value_XOR : 1011011101
            for cell in cells:
                cell_possible_values = self._grid[cell[0]][cell[1]]

                #only remove the bit if it's still there!
                if not (cell_possible_values & value_bit) == 0:
                    self._grid[cell[0]][cell[1]] &= value_bit_XOR

                    #check whether the correct value for the modified cell
                    #can be determined
                    self.CheckCell(cell[0], cell[1])

                    #check if the value of any other cell in that
                    #cell's block/row/column can be determined
                    self.CheckSection(cell[0], cell[1], Sudoku.BLOCK)
                    #self.CheckSection(cell[0], cell[1], Sudoku.ROW)
                    #self.CheckSection(cell[0], cell[1], Sudoku.COLUMN)

    #check if cell is already solved
    #if the bitset only has one value bit set at 1,
    #that value is the correct value for the cell
    def IsCellSolved(self, row, column):
        value_list = [2**x for x in range(9)]
        if value_list.count(self._grid[row][column]) > 0:
            return value_list.index(self._grid[row][column])+1
        else:
            return -1

        bitset = self._grid[row][column]

    #check if the cell's correct value can be determined
    #if there is only one value bit remaining for the cell,
    #it is the correct value for the cell
    #returns true if the cell's correct value was determined;
    #otherwise, returns false
    def CheckCell(self, row, column):
        value = self.IsCellSolved(row, column)
        if not value == -1:
            self.SetCellValue(row, column, value)
            return True
        else:
            return False

    #check if the value of any other cell in that cell's block/row/column
    #can be determined
    #if a certain value is only possible in one cell in the block,
    #then that it the cell's value
    def CheckSection(self, cell_x, cell_y, section=BLOCK):
        #list of the places
        value_list = [ [] for x in range(9) ]
        cell_list = []

        #get all cells from the cell's block
        if section == Sudoku.BLOCK:
            block_x = int(cell_x/3)
            block_y = int(cell_y/3)
            for y in range(3):
                for x in range(3):
                    cell = (block_x*3 + x, block_y*3 + y)
                    cell_list.append(cell)
        #get all cells from the cell's row
        elif section == Sudoku.ROW:
            for row in range(9):
                cell = (cell_x, row)
                cell_list.append(cell)
        #get all cells from the cell's column
        elif section == Sudoku.COLUMN:
            for column in range(9):
                cell = (column, cell_y)
                cell_list.append(cell)

        #tally possible values
        for cell in cell_list:
            for value in range(9):
                if not (self._grid[cell[0]][cell[1]] & 2**value) == 0:
                    value_list[value].append(cell)

        #values with only one instance in the section
        value_solved_list = [x+1 for x in range(9) if len(value_list[x]) == 1]
        #solve the cells with such values
        for value in value_solved_list:
            cell = value_list[value-1][0]
            self.SetCellValue(cell[0], cell[1], value)

        #at least one cell was solved
        if len(value_solved_list) > 0: return True
        #no cells were solved
        else: return False

    #runs the solving algorithm!
    def Solve(self):
        #iterate through each cell and check if it's value can be determined
        for row in range(9):
            for column in range(9):
                self.CheckCell(row, column)

        for row in range(3):
            for column in range(3):
                self.CheckSection(row*3, column*3, Sudoku.BLOCK)
                #self.CheckSection(row*3, column*3, Sudoku.COLUMN)
                #self.CheckSection(row*3, column*3, Sudoku.ROW)


#create a list of known values from a grid
def GenerateKnownValues(grid):
    known_values = []
    for row in range(len(grid)):
        for column in range(len(grid)):
            if not grid[row][column] == -1:
                known_values.append( (row, column, grid[row][column],) )

    return known_values

"""
grid = [ \
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1]]
"""

grid = [
    [ 2,  9, -1,  3, -1, -1, -1, -1, -1],
    [-1, -1,  1, -1, -1, -1,  6, -1,  3],
    [-1, -1, -1,  4, -1,  1, -1,  2, -1],
    [-1, -1,  4, -1, -1, -1,  8,  1, -1],
    [-1,  8, -1, -1, -1, -1, -1,  7,  2],
    [-1,  6, -1, -1, -1,  2, -1, -1, -1],
    [ 8, -1, -1,  7,  5, -1, -1,  9, -1],
    [ 4, -1,  2, -1, -1,  9,  5, -1, -1],
    [ 3, -1, -1, -1, -1, -1, -1, -1,  1]]

def main():
    global grid
    known_values = GenerateKnownValues(grid)
    sudoku = Sudoku(known_values)
    print sudoku.solution_grid
    sudoku.Solve()
    print sudoku.solution_grid

if __name__ == '__main__':
    main()
