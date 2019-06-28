one = '1⃣'
two = '2⃣'
three = '3⃣'
four = '4⃣'
five = '5⃣'
six = '6⃣'
seven = '7⃣'
eight = '8⃣'
nine = '9⃣'
zero = '0⃣'

numbers_unicode_list = [one, two, three, four, five, six, seven, eight, nine, zero]

# voting system
yes = '✅'
no = '❎'
table = '👋'


def get_index(emoji):
    return numbers_unicode_list.index(emoji) + 1
