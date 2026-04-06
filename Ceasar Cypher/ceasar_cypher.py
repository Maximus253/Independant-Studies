
def decrypt(string, shift=0):
    array = list(string)
    if (shift > 0):
        print("".join(shift_char(char, -shift) for char in array))
        return
    for i in range(26):
        print("".join(shift_char(char, -i) for char in array))
    
def encrypt(string, shift=7):
    array=list(string)
    print("".join(shift_char(char, shift) for char in array))
    return


def shift_char(char, shift):
    if 'a' <= char <= 'z':
        return chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
    elif 'A' <= char <= 'Z':
        return chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
    else:
        return char


option = int(input("Select an option: \n1: Decrypt (requires string and an optional shift key) \n2: Encrypt (requires a string and a shift key)\n"))
if option not in (1, 2):
    print("Please select an option")
    exit()

if (option == 1):
    string = input("Please enter your cypher: ")
    shift_input = input("Please enter your shift (can be left blank): ")
    shift = int(shift_input) if shift_input else 0
    decrypt(string, shift)
    
if (option == 2):
    string = input("Please enter your plaintext: ")
    shift_input = input("Please enter your shift: ")
    shift = int(shift_input) if shift_input else 0
    encrypt(string, shift)


