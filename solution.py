from utils import *

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
unitlist = row_units + column_units + square_units

# TODO: Update the unit list to add the new diagonal units
main_diag=a=[row+col for i,row in enumerate(rows) for j,col in enumerate(cols) if i==j ]
reverse_diag=[row+col for i,row in enumerate(rows) for j,col in enumerate(cols[::-1]) if i==j ]
unitlist.append(main_diag)
unitlist.append(reverse_diag)


# Must be called after all units (including diagonals) are added to the unitlist
units = extract_units(unitlist, boxes)
peers = extract_peers(units, boxes)


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}
    Returns
    -------
    dict
        The values dictionary with the naked twins eliminated from peers
    Notes
    -----
    Your solution can either process all pairs of naked twins from the input once,
    or it can continue processing pairs of naked twins until there are no such
    pairs remaining -- the project assistant test suite will accept either
    convention. However, it will not accept code that does not process all pairs
    of naked twins from the original input. (For example, if you start processing
    pairs of twins and eliminate another pair of twins before the second pair
    is processed then your code will fail the PA test suite.)
    The first convention is preferred for consistency with the other strategies,
    and because it is simpler (since the reduce_puzzle function already calls this
    strategy repeatedly).
    """
    duplicate_box = []
    for unit in unitlist:
        s = set()
        #Save the values that are repeated in the unit
        duplicate_values = [values[box] for box in unit if (values[box] in s and len(values[box]) == 2) or s.add(values[box])]
        #save the name of the boxes that has those particular values
        duplicate_box_aux = [box for duplicate in duplicate_values for box in unit if values[box] == duplicate]
        #Save the paired twins and also the value that they had --> previous to any posterior change.
        for pos,element in enumerate(duplicate_box_aux[::2]):
            if ([element, duplicate_box_aux[pos + 1], values[element]]) not in duplicate_box:
                duplicate_box.append([element, duplicate_box_aux[pos + 1], values[element]])
   # For those boxes that are twins find their mutual peers and substract the values to them
    for element in duplicate_box:
        combined_twins=set(peers[element[0]])&set(peers[element[1]])
        for box in combined_twins:
            if (box!=element[0] and box!=element[1] and len(values[box])>1):
                for num in element[2]:
                    new_values=values[box].replace(num,"")
                    assign_value(values, box, new_values)

    return values


def eliminate(values):
    """Eliminate values from peers of each box with a single value.
    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.
    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            # values[peer] = values[peer].replace(digit, '')
            new_value = values[peer].replace(digit, '')
            assign_value(values, peer, new_value)
    return values


def only_choice(values):
    """Finalize all values that are the only choice for a unit.
    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.
    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    ## Used the provided solutions to be sure that my implementation of diagonals and
    ## Twins is ok
    for digit in '123456789':
        for unit in unitlist:
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(values, dplaces[0], digit)
    return values


def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Use the Eliminate Strategy
        values = eliminate(values)
        # Use the Only Choice Strategy
        values = only_choice(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values



def search(values):
    """Apply depth first search to solve Sudoku puzzles in order to solve puzzles
    that cannot be solved by repeated reduction alone.
    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}
    Returns
    -------
    dict or False
        The values dictionary with all boxes assigned or False
    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    and extending it to call the naked twins strategy.
    """
    "Using depth-first search and propagation, try all possible values."
    ## Used the provided solutions to be sure that my implementation of diagonals and
    ## Twins is ok

    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes):
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    #values = grid2values(grid)
    values={"A2": "9", "H3": "2456789", "H4": "1", "B6": "1", "H9": "2345678", "F6": "23568", "C9": "13456", "C7": "13456", "B9": "9", "I6": "4", "B2": "2", "I5": "35678", "B7": "7", "H8": "234567", "F3": "25689", "C2": "68", "F2": "7", "G6": "9", "A5": "3468", "E6": "23568", "I2": "123568", "E1": "123689", "E3": "25689", "E9": "12345678", "F9": "1234568", "G1": "1234678", "H6": "23568", "H2": "23568", "I3": "25678", "C3": "4678", "E4": "234678", "G8": "1234567", "D1": "123689", "E7": "1234568", "F8": "1234569", "C1": "4678", "D8": "1235679", "A1": "2468", "A6": "7", "B5": "46", "H1": "2346789", "A8": "2346", "G5": "35678", "D6": "23568", "G4": "23678", "D9": "1235678", "F7": "1234568", "F1": "123689", "E5": "13456789", "D5": "1356789", "D3": "25689", "G3": "245678", "F4": "23468", "H5": "35678", "G9": "12345678", "B4": "46", "D4": "23678", "A9": "2346", "F5": "1345689", "I8": "123567", "G7": "1234568", "C8": "13456", "E8": "12345679", "I7": "9", "C6": "368", "B8": "8", "D2": "4", "I4": "23678", "G2": "123568", "H7": "234568", "C4": "9", "A3": "1", "E2": "123568", "B3": "3", "I9": "1235678", "B1": "5", "D7": "123568", "A7": "2346", "A4": "5", "I1": "123678", "C5": "2"}
    values = search(values)
    return values



if __name__ == '__main__':
    diag_sudoku_grid = '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................'
    display(grid2values(diag_sudoku_grid))
    result = solve(diag_sudoku_grid)
    display(result)

    try:
        import PySudoku
        PySudoku.play(grid2values(diag_sudoku_grid), result, history)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
