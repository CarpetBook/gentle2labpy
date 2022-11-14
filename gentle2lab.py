import json
import argparse

unkReplace = True
# false = no replace, <unk>/<oov> label
# true = replace with unk/oov word

notFoundReplace = True
# false = "not-found-in-audio" words are labeled as "?"
# true = "not-found-in-audio" words are labeled as the missing word

# floatTime = False
# // this is deprecated already because uhhh no //
# false = label timestamps are nanoseconds
# true = label timestamps are seconds, two decimal places
# (gentle will only align to two decimal places of precision, more decimals are unnecessary)

includeBIE = False
# false = no B, I, E markers
# true = leaves "_B", "_I", and "_E" on the end of labels to mark beginning, intermediate, and ending of words

neatNumbers = True
# round times to two decimal places in lab file
# stops 5.01 from looking like 5.00999999999999999 or 5.01000000000000001

filey = None
lines = None

def convertFiles(fileys):
    for f in fileys:
        try:
            with open(f) as filey:
                lines = json.load(filey)

                lablines = [] # labels to write, tuple of (word, start, end)

                for x in range( len(lines["words"]) ):
                    word = lines["words"][x] # word object

                    res = "" # will be aligned phone or unaligned word
                    
                    if word["case"] != "not-found-in-audio":
                        totalOff = word["start"] # word offset used for relative phone starting time
                        for p in word["phones"]:
                            st = totalOff
                            en = totalOff + p["duration"]
                            res = p["phone"]
                            if neatNumbers:
                                st = round(st, 2)
                                en = round(en, 2)
                            if not includeBIE:
                                res = p["phone"].split("_")[0] # remove _B, _I, _E
                            res = ( res, st, en )
                            lablines.append(res)
                            totalOff = en # add duration to next starting time
                        continue

                if notFoundReplace: res = word["word"]
                else: res = "?"

                st = lablines[ len(lablines)-1 ][2] # unmatched word start matches last line's ending time
                en = st + 0.01
                if neatNumbers:
                    st = round(st, 2)
                    en = round(en, 2)
                res = ( res, st, en )
                lablines.append(res)

            # print lab lines to a file
            with open(str(f) + ".lab", "w") as out:
                for line in lablines:
                    mewhen = str(line[1]) + " " + str(line[2]) + " " + line[0]
                    print(mewhen, file=out)
            print("Wrote " + str(len(lablines)) + " labels to " + str(f) + ".lab")

        except FileNotFoundError as fe:
            print("Oops! I can't find that file. Did you type the filename correctly?")
            print(fe)
        except json.decoder.JSONDecodeError as je:
            print("Oops! The file has invalid JSON. Please check your file's formatting and try again.")
            print(je)
        except Exception as e:
            print("Oops! Something went wrong. Please see error below for details.")
            print(e)

def main():
    global unkReplace
    global notFoundReplace
    global includeBIE
    global neatNumbers

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--file", "-f",
        action="extend",
        nargs="+",
        type=str,
        help="input json file(s)",
        required=True
    )
    parser.add_argument(
        "--unk", "-u",
        action="store_false",
        help="replace unknown words with 'unk'"
    )
    parser.add_argument(
        "--noreplace", "-n",
        action="store_false",
        help="replace unaligned words with '?'"
    )
    parser.add_argument(
        "--bie", "-b",
        action="store_true",
        help="do not remove _B, _I, and _E"
    )
    parser.add_argument(
        "--messy", "-m",
        action="store_false",
        help="do not round timestamps"
    )
    
    args = parser.parse_args()
    unkReplace = args.unk
    notFoundReplace = args.noreplace
    includeBIE = args.bie
    neatNumbers = args.messy
    convertFiles(args.file)

if __name__ == "__main__":
    main()