import os
#import commands
import subprocess
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Input Parameters:")
    parser.add_argument("--suffix_labels1", default = "1,0;1,0;0,0;1,0;0,0;0,0", type = str,
                        help = "a list controling which method to generate in the suffix")
    parser.add_argument("--suffix_labels2", default = "0,0;1,0;0,0;1,0;1,0;1,0", type = str,
                        help = "a list controling which method to generate in the suffix")
    args = parser.parse_args()
    #print(args.suffix_labels1)
    
    #generate = "python /workdir/DQNTest/mars/main.py --suffix_labels1=\"1,0;1,0;0,0;1,0;0,0;0,0\" --suffix_labels2=\"0,0;1,0;0,0;1,0;1,0;1,0\""
    generate = "python /workdir/DQNTest/mars/main.py --suffix_labels1=\""
    generate += args.suffix_labels1
    generate += "\" --suffix_labels2=\""
    generate += args.suffix_labels2
    generate += "\""
    #print(generate)

    
    os.system(generate)
    move = "cp /workdir/DQNTest/mars/tests/test_try2_gen.cpp /workdir/PERIOD/test/mars/test_try2_gen.cpp"
    os.system(move)

    build = "/workdir/PERIOD/test/mars/build.sh"
    os.system(build)
    run = "/workdir/PERIOD/tool/DBDS/run_PDS.py -y -d  3 /workdir/PERIOD/test/mars/test_try2_gen"
    os.system(run)
    output = subprocess.getoutput(run)
    print(output)
    