##############################################################################
#
# Program Name:
#
# Steganographer
#
# Description:
#
# This program encodes .png image files with messages, in such a way that
# the encoded image looks indistinguishable from the original image.  The
# idea is that two people can send innocent looking images back and forth
# but they actually are having a conversation, sending each other secret
# messages!
#
# The encoding works as follows:
# 1.    The messages must be in ASCII format.
# 2.    The message is converted into a binary string based on ASCII encoding.
# 3.    Each bit of the message is then encoded sequentially in each rgb value
#       of each pixel of the image, starting from the top left pixel. The
#       encoding works by changing the least significant bit of each rgb value
#       to the bit corresponding with the next bit in the message.
# 4.    If the message is shorter than the number of rgb values in the image,
#       the LSB of each remaining rgb value is set to '0'.
# 5.    If the binary message is longer than the number of rgb values, the
#       program simply encodes as much of the message as it can.
#
# The program can also decode encoded images. The choice to decode or encode
# is made by the user at the command line:
#
#   $python Steganographer.py <imagefile> --encode <message>
#
# If the user does not include the optional argument --encode, the program
# assumes that decode was required.
#
# This code represents an extension to project 2 Semester 2 2013 of the
# University of Melbourne subject Foundations of Computing.
#
# Authors:
#
# Daniel Williams (code) (daniel.williams.unimelb.edu.au)
# Bernie Pope (project design) (bjpope@unimelb.edu.au)
#
# Date created:
#
# 2 September 2013
#
# Date modified and reason:
#
# 5 September 2013:     tidied up code, implemented some extra helper 
#                        functions
# 21 September 2013:    added functions to allow for command line argument
#                       parsing
# 25 September 2013:    spot check of documentation and coding style, fixed
#                       some non-PEP8 complient docstrings etc
#
##############################################################################

import bits
from SimpleImage import read_image, write_image
import argparse
import sys

# constants
BYTE_LENGTH = 8
ZERO_BYTE = '00000000'
PNG = '.png'
PNG_ERROR = "image provided is not in .png format"
FNF_ERROR = "The file {} was not found"
ENCODE_EXTENSION = "_encoded"
DISPLAY_MESSAGE = "The file {0} is encoded with the message:\n\n{1}"
IMAGE_HELP = "name of the image (PNG format) to be processed"
ENCODE_HELP = """encode the message ENCODE in the image. \
If this option not used, decoding will occur"""
ENCODE_OUT = "Encoded your message to {}"


# functions for processing user commands
def process_commands():
    """ Build the command line argument parser and use it
    to return the parsed arguments from the command line.

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help=IMAGE_HELP)
    parser.add_argument("--encode", help=ENCODE_HELP, type=str)
    return parser.parse_args()


def open_image(filename):
    """ Open up the image and return it.  Will exit if the file
    does not have .png extension, or if the file cannot be found.

    Arguments:
    filename -- the name of the file

    """
    if filename[-4:].lower() != PNG:
        print PNG_ERROR
        sys.exit()

    try:
        image = read_image(open(filename))
    except IOError:
        print FNF_ERROR.format(filename)
        sys.exit()

    return image


def get_user_input():
    """ Get the user input from the command line and return the
    tuple (image,message,arg.image), where:
        - image is the image to be processed in the SimpleImage format
        - message is the message to be encoded (message = False if
            user requires decoding)
        - arg.image is the filename of the image

     """
    args = process_commands()
    image = open_image(args.image)

    if args.encode:
        message = args.encode
    else:
        message = False

    return (image, message, args.image)


def make_output_filename(filename):
    """ convert a filename from the format filename.png to the
    format filename_encoded.png

    Arguments:
    filename -- the name of the file

    """
    return filename[:-4] + ENCODE_EXTENSION + PNG


# functions for encoding and decoding messages
def message_to_bits(text):
    """Takes a string of ASCII characters and returns a string
    of binary digits corresponding to that string

    Arguments:
    text -- the message to be converted to a binary string

    """
    output = ''
    for char in text:
        output += bits.char_to_bits(char)
    return output


def bits_to_message(message_bits):
    """ Takes a string of binary digits and returns the
    corresponding string of ASCII characters

    Arguments:
    message_bits -- message in binary format

    """
    output = ''
    index = 0
    currByte = message_bits[index:index + BYTE_LENGTH]
    while len(currByte) >= BYTE_LENGTH:
        if currByte == ZERO_BYTE:
            return output
        else:
            output += bits.bits_to_char(currByte)
        index += BYTE_LENGTH
        currByte = message_bits[index:index + BYTE_LENGTH]
    return output


def round_trip(message):
    """ A simple test function - not used in main program """
    return bits_to_message(message_to_bits(message)) == message


def encode(image, message):
    """ conducts the encoding of the message, according to the
    method described in the header comments.  Takes an image and
    a message and returns a new image which is encoded with
    the message.

    Arguments:
    image -- the image to be encoded. Image must be in the format
             generated by the SimpleImage module (i.e. a list of lists
             of tuples, where each tuple represents a pixel)
    message -- the string to be encoded in the message

    """
    binarymsg = message_to_bits(message)
    output = []
    index = 0
    current_row = 0
    for row in image:
        output.append([])
        for pixel in row:
            new_pixel = []
            for intensity in pixel:
                # check if there is any message left to be encoded
                if index < len(binarymsg):
                    new_pixel.append(bits.set_bit(int(intensity),
                                                  binarymsg[index], 0))
                    index += 1
                else:
                    new_pixel.append(bits.set_bit(int(intensity), 0, 0))
            output[current_row].append(tuple(new_pixel))
        current_row += 1
    return output


def decode(image):
    """ takes an encoded image and returns the message that was
    encoded inside that image.

    Arguments:
    image -- the image to be encoded. Image must be in the format
             generated by the SimpleImage module (i.e. a list of lists
             of tuples, where each tuple represents a pixel)

    """
    output = ''
    curr_chunk = ''

    for row in image:
        for pixel in row:
            for num in pixel:
                curr_chunk += bits.get_bit(num, 0)
                if len(curr_chunk) == BYTE_LENGTH:
                    if curr_chunk == ZERO_BYTE:
                        # found a byte 00000000, so no more message to
                        # decode
                        return output
                    else:
                        output += bits.bits_to_char(curr_chunk)
                        curr_chunk = ''
    return output


 # main function
def main():
    """drives the program"""
    image, message, filename = get_user_input()

    if message:
        encoded_filename = make_output_filename(filename)
        write_image(encode(image, message), encoded_filename)
        print ENCODE_OUT.format(encoded_filename)
    else:
        print DISPLAY_MESSAGE.format(filename, decode(read_image(filename)))

main()
