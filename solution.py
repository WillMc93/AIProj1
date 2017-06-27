assignments = []
rows = 'ABCDEFGHI'
cols = '123456789'


def cross(A, B): # needed here for setting up unit and peer lists
	"Cross product of elements in A and elements in B."
	return [a+n for a in A for n in B]


def generate_diagonals():
	# Get the zip of rows with cols (which will be the left to right diagonal)
	A = [r+c for (r,c) in zip(rows, cols)]
	# Get the zip of rows with cols reversed (which will be the right to left diagonal)
	B = [r+c for (r,c) in zip(rows, cols[::-1])]
	# Return the lists
	return [A, B]


# Setup unit and peer lists here
boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diagonal_units = generate_diagonals()
unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)


def assign_value(values, box, value):
	"""
	Please use this function to update your values dictionary!
	Assigns a value to a given box. If it updates the board record it.
	"""

	# Don't waste memory appending actions that don't actually change any values
	if values[box] == value:
		return values

	values[box] = value
	if len(value) == 1:
		assignments.append(values.copy())
	return values


def naked_twins(values):
	"""
	Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

	# Generate a list with all boxes of length two (pairs)
	pairlist = [box for box in values.keys() if len(values[box]) == 2]
	twinlist = []
	for pair in pairlist:
		for peer in peers[pair]:
			# For each peer of a pair in pairlist: Check if the peer has the same value as the pair
			# and check that the reverse tuple is not already added before adding to twinlist
			if set(values[pair]) == set(values[peer]) and (peer, pair) not in twinlist:
				twinlist.append((pair, peer))

	# Eliminate the naked twins as possibilities for their peers
	for twins in twinlist:
		# Get only mutual peers
		mutual = set(peers[twins[0]]) & set(peers[twins[1]])

		# Since we twins[0] and twins[1] are equal
		twin = twins[0]

		# For each mutual peer: if the peer box contians more than one value, and
		# the peer box is not in our twinlist then remove the values
		# of our naked twins from that peer
		for peer in mutual:
			if len(values[peer]) > 1 and peer not in twinlist:
				for i in values[twin]:
					assign_value(values, peer, values[peer].replace(i, ''))

	return values


def grid_values(grid):
	"""
	Convert grid into a dict of {square: char} with '123456789' for empties.
	Args:
		grid(string) - A grid in string form.
	Returns:
		A grid in dictionary form
			Keys: The boxes, e.g., 'A1'
			Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
	"""
	# Taken from Strategy 1: Elimination lesson

	all_values = '123456789'

	# For each character in the grid string: if the char is '.' fill in all values
	# else just use the character
	values = []
	for box in grid:
		if box == '.':
			values.append(all_values)
		elif box in all_values:
			values.append(box)
	assert len(values) == 81
	return dict(zip(boxes, values))


def display(values):
	"""
	Display the values as a 2-D grid.
	Args:
		values(dict): The sudoku in dictionary form
	"""
	# Taken from Strategy 1: Elimination lesson
	# Print all boxes with lines in proper place.
	boxes = cross(rows, cols)
	width = 1 + max(len(values[box]) for box in boxes)
	line = '+'.join(['-'*(width*3)]*3)
	for row in rows:
		print(''.join(values[row+col].center(width)+('|' if col in '36' else '')
					  for col in cols))
		if row in 'CF': print(line)
	return


def eliminate(values):
	# Get the number of cells of length 1 (get all solved cells)
	solved = [box for box in values.keys() if len(values[box]) == 1]
	for idx in solved:
		for peer in peers[idx]:
			# For each peer of a solved box remove the value of the solved box from the peer
			assign_value(values, peer, values[peer].replace(values[idx], ''))

	return values


def only_choice(values):
	all_values = '123456789'

	for unit in unitlist:
		for i in all_values:
			# For each value in all_values: if the value only appears in one box in a unit,
			# remove all other values from that box (i.e. assign that value)
			place = [box for box in unit if i in values[box]]
			if len(place) == 1:
				assign_value(values, place[0], i)

	return values


def solved_to_length(values, length=1):
	# Return number of boxes with number of possibilities == length
	# Default this to 1 because we search for that length most often.
	return len([box for box in values.keys() if len(values[box]) == length])


def reduce_puzzle(values):
	stalled = False

	while not stalled:
		# Get all values of length == 1 before reducing puzzle
		solved_before = solved_to_length(values)

		# Reduce puzzle by calling all of our reducing methods
		values = eliminate(values)
		values = only_choice(values)
		values = naked_twins(values)

		# Get all values of length == 1 after reducing the puzzle
		solved_after = solved_to_length(values)

		# If the number solved has not changed, we have reduced the puzzle as much
		# as possible this go round (i.e. will exit the loop after this iteration)
		stalled = solved_before == solved_after

		# If any of our boxes have no value something has gone horribly wrong
		if solved_to_length(values, 0):
			return False

	return values


def search(values):
	# Reduce the puzzle as much as we can first.
	values = reduce_puzzle(values)

	# If values is Flase, then reduce_puzzle() broke
	if values is False:
		return False
	# Else if all boxes have length of 1, then the puzzle is solved
	elif all(len(values[box]) == 1 for box in boxes):
		return values

	# To search find the box with the lowest number of possibilities (hopefully close to two)
	_, box = min((len(values[box]), box) for box in boxes if len(values[box]) > 1)

	# For each value in that minimum possibilities box, make a temporary copy
	# and assign that value to the box and search
	# If the search returns False then then try one of the other possible values until a valid puzzle is returned.
	for value in values[box]:
		puzzle = values.copy()
		puzzle[box] = value
		run = search(puzzle)
		if run:
			return run


def solve(grid):
	"""
	Find the solution to a Sudoku grid.
	Args:
		grid(string): a string representing a sudoku grid.
			Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
	Returns:
		The dictionary representation of the final sudoku grid. False if no solution exists.
	"""
	# Get the grid setup and dive in to the search.
	return search(grid_values(grid))


if __name__ == '__main__':
	grid3 = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

	display(solve(grid3))
	try:
		from visualize import visualize_assignments
		visualize_assignments(assignments)

	except SystemExit:
		pass
	except:
		print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
