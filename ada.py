class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()

# read file sample
# file_iter = open("k1.txt", 'rU')
#    for line in file_iter:
#        line = line.strip().rstrip(' ')                         # Remove trailing comma
#        record = line.split(':')
#        k1_itemset.append(record[1])


# write file sample
# with open('k2.txt', 'w') as f:
# f.write(str(int(support)) +
#                        ":"+str(item).replace(" ", ";")+"\n")
# f.close()

    # Example command:
    # python examples/savesettings_logincallback.py -u "yyy" -p "zzz" -settings "test_credentials.json"
    # parser = argparse.ArgumentParser(description='Pagination demo')
    # parser.add_argument('-u', '--username', dest='username', type=str, required=True)
    # parser.add_argument('-p', '--password', dest='password', type=str, required=True)
    # parser.add_argument('-debug', '--debug', action='store_true')
