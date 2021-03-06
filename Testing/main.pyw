import time
from PIL import Image


def write_image(start_image, red, green, blue):  # Takes original image, overwrites new colour values and saves to new
    #  file
    image = Image.open(start_image)
    width, height = image.size
    for y in range(height):
        for x in range(width):
            image.putpixel((x, y), (red[y][x], green[y][x], blue[y][x]))

    new_image_name = "steg" + start_image
    image.save(new_image_name)
    print("Image Saved!!!")


def lsb_list(channel):  # Finds 2 least significant bits and returns them in one long list for that colour channel
    bit_list = []  # Initializes list as empty to be filled with base 10 equivalents of two LSBs
    zero_num = 0
    for row in channel:
        for value in row:

            if value % 2 == 0:
                zero_num += 0
                temp_num = value / 2
            else:
                zero_num += 1
                temp_num = (value - 1) / 2
            if temp_num % 2 == 0:
                zero_num += 0
            else:
                zero_num += 2
            bit_list.append(zero_num)
            zero_num = 0
    return bit_list


def return_two_lsbs_zeroed(non_zero_list, width, height):  # Returns a colour channel with the 2 LSBs of every pixel
    # ser to zero
    zero_list = []  # Stores list of values with last 2 LSBs subtracted (Base 10)
    zero_num = 0
    for li in non_zero_list:
        for number in li:
            if number % 2 == 0:
                zero_num += 0
                temp_num = number / 2
            else:
                zero_num += 1
                temp_num = (number - 1)/2
            if temp_num % 2 == 0:
                zero_num += 0
            else:
                zero_num += 2
            zero_list.append(number - zero_num)
            zero_num = 0
    zero_list_nested = []  # zero_list is one dimensional, this will store 2 dimensional version with rows and columns
    zero_row = []
    counter = 0
    for heightCount in range(height):
        for widthCount in range(width):
            if widthCount == 0:
                zero_row = []
            zero_row.append(zero_list[counter])
            counter += 1
        zero_list_nested.append(zero_row)
    return zero_list_nested


def byte_to_quad_bit_pair(byte):  # splits a byte into four pairs of bits - these are the bits to overwrite the least
    #  significant bits
    quad_bit = []
    current = 0
    if byte >= 128:
        current += 2
        byte -= 128
    if byte >= 64:
        current += 1
        byte -= 64
    quad_bit.append(current)
    current = 0
    if byte >= 32:
        current += 2
        byte -= 32
    if byte >= 16:
        current += 1
        byte -= 16
    quad_bit.append(current)
    current = 0
    if byte >= 8:
        current += 2
        byte -= 8
    if byte >= 4:
        current += 1
        byte -= 4
    quad_bit.append(current)
    current = 0
    if byte >= 2:
        current += 2
        byte -= 2
    if byte >= 1:
        current += 1
        byte -= 1
    quad_bit.append(current)

    return quad_bit


def txt_to_steg_code(plaintext):  # Takes the message to be encoded and returns code for encoding
    plaintext = plaintext + "EOFEOFEOFEOFEOF"  # This tells the program when to stop when reading the message,
    # otherwise gunk comes out
    plain_list = []  # To store numerical value for every character in text in a list
    pairs_list_dec = []  # To store base 10 values in lists of four for each character, therefore separating each
    # character into four bit pairs
    steg_list = []  # to store all the base 10 values in one list instead of a list of lists
    for char in plaintext:
        plain_list.append((ord(char)))
    for item in plain_list:
        pairs_list_dec.append(byte_to_quad_bit_pair(item))
    for item in pairs_list_dec:
        for subItem in item:
            steg_list.append(subItem)
    return steg_list


def image_reading(filename):  # Reads image and generates lists from red, green and blue values. Also returns width
    # and height variables
    file_extension = filename[-3:]  # Finds file extension - needed for .png support at the moment
    image = Image.open(filename)
    width, height = image.size
    print("width: " + (str(width)))
    print("height: " + (str(height)))
    redarray = []  # Stores all red values
    greenarray = []  # Stores all green values
    bluearray = []  # Stores all blue values
    if file_extension == "png":  # will work for png with alpha channel
        image.putalpha(0)  # adds alpha channel in case it is png without alpha channel, should replace existing
    for heightCount in range(height):  # Compiles rows together to form 2d structure
        for widthCount in range(width):  # Compiles rows into lists through sequential reading
            if widthCount == 0:  # Reset row lists for a new row
                red_row = []
                green_row = []
                blue_row = []
            if file_extension == "png":  # will work for png with alpha channel
                red, green, blue, alpha = image.getpixel((widthCount, heightCount))
                red_row.append(red)
                green_row.append(green)
                blue_row.append(blue)
            else:
                red, green, blue = image.getpixel((widthCount, heightCount))
                red_row.append(red)
                green_row.append(green)
                blue_row.append(blue)
        # Add row to the larger array when row is complete
        redarray.append(red_row)
        greenarray.append(green_row)
        bluearray.append(blue_row)

    print("Arrays Generated")  # Was useful when running slow to show stuff is happening - may remove at later date
    return redarray, greenarray, bluearray, width, height


def steg_channel(zero_channel, steg_list, down_counter, width, height, counter):  # Takes a colour channel and
    # returns it with the steg encoding added to each value
    steganography_coded_channel = []  # To Store the channel with the added code
    steg_row = []  # To store each individual row before compiling all the rows back into the larger array
    for heightCount in range(height):

        for widthCount in range(width):

            if widthCount == 0:  # Initializes the row to empty at the start of each row
                steg_row = []
            if down_counter > 0:  # Add the steg encoding to this colour value
                steg_row.append((zero_channel[heightCount][widthCount] + steg_list[counter]))
            else:  # Don't add encoding when there is no encoding left
                steg_row.append((zero_channel[heightCount][widthCount]))
            down_counter -= 1  # Counts down the number of bits of encoding left
            counter += 1  # Counts up to track which index is being used reading through the steg code
        steganography_coded_channel.append(steg_row)
    return steganography_coded_channel, down_counter, counter


def encode():
    start_time = time.clock()
    steg_list = []
    start_image = str(input("enter a .bmp or .png file to encode.\n"))
    red_chan, green_chan, blue_chan, width, height = image_reading(start_image)
    current_time = time.clock()
    print(str(start_time-current_time) + " seconds")
    start_time = current_time
    data_to_be_hidden = str(input("Would you like to hide a message or a file?\n 'message' or 'file'\n"))
    if data_to_be_hidden == "message":
        steg_list = txt_to_steg_code(str(input("enter the message to encode into the image\nDO NOT use the enter key "
                                               "or paste anything with line breaks or new lines,\nonly the first "
                                               "paragraph will be encoded.\n")))
    elif data_to_be_hidden == "file":
        secret_file = str(input("Please enter a file path for the file you wish to hide:\n"))
        with open(secret_file, "rb") as f:
            steg_list = file_to_steg_code(f)
    current_time = time.clock()
    print(str(start_time - current_time) + " seconds")
    start_time = current_time
    # Remove the two least significant bits from every pixel
    zero_red = return_two_lsbs_zeroed(red_chan, width, height)
    zero_blue = return_two_lsbs_zeroed(blue_chan, width, height)
    zero_green = return_two_lsbs_zeroed(green_chan, width, height)
    # Adds the encoding to each colour channel
    current_time = time.clock()
    print(str(start_time-current_time) + " seconds")
    start_time = current_time
    steg_red, down_counter, counter = steg_channel(zero_red, steg_list, (len(steg_list)), width, height, 0)
    steg_green, down_counter, counter = steg_channel(zero_green, steg_list, down_counter, width, height, counter)
    steg_blue, down_counter, counter = steg_channel(zero_blue, steg_list, down_counter, width, height, counter)
    # Writes finished image to file
    write_image(start_image, steg_red, steg_green, steg_blue)

    print("Done!!\n\n\n")
    current_time = time.clock()
    print(str(start_time-current_time) + " seconds")


def file_to_steg_code(file_content):
    steg_list = []
    bit_pair_list = []
    byte = file_content.read(1)
    while byte:
        byte_base_10 = ord(byte)
        bit_pairs = byte_to_quad_bit_pair(byte_base_10)
        bit_pair_list.append(bit_pairs)
        byte = file_content.read(1)
    for char in separator:
        byte_base_10 = ord(char)
        bit_pairs = byte_to_quad_bit_pair(byte_base_10)
        bit_pair_list.append(bit_pairs)
    for item in bit_pair_list:
        for subItem in item:
            steg_list.append(subItem)

    return steg_list


def steg_decode(long_steg_list):
    length = len(long_steg_list)
    decoded_text = ""
    for index in range(0, (length - 3), 4):  # Each character is stored across four pairs of bits, therefore
        # incrementing in fours

        # Initializes a variable to store the numerical value for the current character
        ord_num = 0
        ord_num += (long_steg_list[index]) * 64  # First two significant bits, worth 128 and 64
        ord_num += (long_steg_list[(index + 1)]) * 16  # Next two significant bits, worth 32 and 16
        ord_num += (long_steg_list[(index + 2)]) * 4  # Next two significant bits, worth 8 and 4
        ord_num += (long_steg_list[(index + 3)])    # Last tow, worth 2 and 1
        decoded_text = decoded_text + chr(ord_num)  # Adds the current character to the developing string
    return decoded_text


def decode():
    start_image = str(input("enter a .bmp or .png file to decode.\n"))
    message_format = str(input("Is the hidden data a message or a file?\n'message'\tor\t'file'\n"))
    while message_format != "message" and message_format != "file":
        message_format = str(input("Let's try again:\nIs the hidden data a message or a file?\n'message'\tor\t'file'\n"))
    red_chan, green_chan, blue_chan, width, height = image_reading(start_image)
    encoded_message = lsb_list(red_chan) + lsb_list(green_chan) + lsb_list(blue_chan)  # Reads encoded message into
    # least significant bit lists
    if message_format == "message":
        decoded_message = str(steg_decode(encoded_message))  # takes LSB list and returns plaintext
        decoded_message = decoded_message.split(separator, 1)[0]  # Uses separator to split decrypted text from junk
        # output
        print("the encoded message was:\n" + decoded_message)

    elif message_format == "file":
        extension = str(input("enter file extension:\n"))
        make_file_from_steg_code(encoded_message, extension, start_image)
        print("encrypted file written!")


def make_file_from_steg_code(encoded_file, extension, destination_file):
    length = len(encoded_file)
    byte_list = []
    for index in range(0, (length - 3), 4):  # Each character is stored across four pairs of bits, therefore
        # incrementing in fours

        # Initializes a variable to store the numerical value for the current character
        byte = 0
        byte += (encoded_file[index]) * 64
        byte += (encoded_file[(index + 1)]) * 16
        byte += (encoded_file[(index + 2)]) * 4
        byte += (encoded_file[(index + 3)])
        byte_list.append(byte)
    # need to strip separator from byte_list "[69,79,70,69,79,70,69,79,70,69,79,70,69,79,70]"
    byte_string = ""  # Need better name
    for byte in byte_list:
        byte_string += chr(byte)
    byte_string = byte_string.split(separator, 1)[0]
    eof_point = len(byte_string)
    byte_list = byte_list[:eof_point]
    filename = "decoded___"
    filename += destination_file[:-4]
    filename += extension
    with open(filename, "bw+") as f:
        formatted_bytes = bytes(byte_list)
        f.write(formatted_bytes)


separator = "EOFEOFEOFEOFEOF"

option = ""
while option != "quit":  # Runs repetitively until user ends program
    option = str(input('Type "encode" to encode a message into an image and "decode" to read a message from an image, '
                       'when finished type "quit" to end the program\n').lower())  # '.lower()' used in case user
    # capitalizes
    if option == "encode":
        encode()
    elif option == "decode":
        decode()
    elif option != "quit":
        print("I don't understand that, please retry below.")

print("Program quitting")
print("Goodbye!")
