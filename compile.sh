#/bin/bash

directory="./build"

while [[ $# -gt 1 ]]
do
    key="$1"
    case $key in
        -t|--target)
        TARGET="$2"
        shift
        ;;
        -a|--address)
        IP="$2"
        shift
        ;;
        *)
        echo "Wrong argument $1"
        echo "use $0 -t|--target arm|x86_64 [-a|--address <ip|hostname  of target>]"
        exit
        ;;
    esac
shift
done

echo "$TARGET"
echo "$IP"

if [ $TARGET = "arm" ]
then
    toolchainTarget="arm-linux-gnueabihf"
elif [ $TARGET = "x86_64" ]
then
    toolchainTarget="x86_64-linux"
else
    echo "Unknown target: $TARGET"
    exit
fi

function generateFreshMakefile() {
    echo "** Creating directory"
    mkdir $directory
    cd $directory
    echo "** Starting cmake"
    cmake -DCMAKE_TOOLCHAIN_FILE=../toolchain-"$toolchainTarget".cmake ..
    echo "** Building"
    make VERBOSE=1
    if [[ $TARGET = "arm" && "$IP"  ]]
    then
        echo "** Sending file to arm"
        scp gettingstarted adaszek@"$IP":/home/adaszek/workspace
    else
        echo "address is not set so file is not uploaded"
    fi
}

if [ ! -d $directory ];
then
    generateFreshMakefile
else
    rm -rf $directory
    generateFreshMakefile
fi

