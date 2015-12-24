#!/usr/bin/env sh

if [ $# = 0 ]; then
    echo "Usage: ./pick_designs.sh <round> [options]"
    exit
else
    round=$1
    shift
fi

if [ "$round" -eq 1 ]; then
    ./show_seqs.py "$@"     \
        us/0/0              \
        us/0/1              \
        us/0/2              \
        us/0/3              \

elif [ "$round" = 2 ]; then
    ./show_seqs.py "$@"     \
        us/1/0              \
        us/1/1              \
        us/1/2              \
        us/1/3              \
        us/2/2              \
        us/2/6              \
        us/2/10             \
        us/2/14             \
        us/4/2              \
        us/4/6              \
        us/4/10             \
        us/4/14             \
        ls/5/0              \
        ls/6/0              \
        ls/6/2              \
        ls/6/4              \
        ls/6/6              \
        nx/0                \
        nx/1                \
        nx/2                \
        nx/3                \
        hp/17               \
        hp/18               \
        hp/33               \

elif [ "$round" = 3 ]; then
    ./show_seqs.py "$@"     \
        id/5/0              \
        id/3/0              \
        id/5/1              \
        id/3/1              \
        id/5/2              \
        id/3/2              \
        id/5/3              \
        id/3/3              \
        id/5/4              \
        id/3/4              \
        us/0/0/4            \
        us/0/0/12           \
        us/0/0/20           \
        us/0/0/28           \
        nxx/0/0             \
        nxx/1/1             \
        nxx/2/2             \
        nxx/2/2/10          \
        nxx/2/2/16          \
        nxx/2/2/0/2         \
        nxx/2/3             \
        nxx/2/3/10          \
        nxx/2/3/16          \
        nxx/2/3/0/2         \
        nxx/3/4             \
        nxx/3/4/10          \
        nxx/3/4/16          \
        nxx/2/4/0/2         \

elif [ "$round" = 4 ]; then
    ./show_seqs.py "$@"     \
        us/0/0/0/2          \
        us/0/0/0/3          \

elif [ "$round" = 5 ]; then
    # Estimated price: $1157
    ./show_seqs.py "$@"     \
        fh/1/0              \
        fh/2/0              \
        sb/2                \
        sb/5                \
        sb/8                \
        sl                  \
        slx                 \
        sh/5                \
        sh/7                \
        cb                  \
        cl                  \
        ch/4                \

elif [ "$round" = 6 ]; then
    # Estimated price: $2581
    ./show_seqs.py "$@"     \
        sb/2/bo             \
        sb/3                \
        sb/3/mo             \
        sb/3/bo             \
        sb/4                \
        sb/4/wo             \
        sb/4/mo             \
        sb/4/bo             \
        sb/5/mo             \
        sb/6                \
        sb/6/mo             \
        slx/wo              \
        slx/mx              \
        sh/4                \
        sh/4/wx             \
        sh/4/mx             \
        sh/4/bx             \
        sh/5/mx             \
        sh/5/bxg            \
        sh/6                \
        sh/7/wx             \
        cb/wo               \
        cb/mo               \
        cb/bo               \
        cl/wo               \
        ch/5                \
        ch/5/wo             \
        ch/6                \
        ch/6/wo             \

elif [ "$round" = 7 ]; then
    ./show_seqs.py "$@"     \
        sb/6/wo             \
        slx/mo              \
        slx/bo              \
        sh/5/wx             \
        cb/wo2              \
        cl/mo               \
        cl/bo               \

#elif [ "$round" = 8 ]; then
#        cb/wo/2             \
#        cbc/wo/slx/wo       \
#        cbc/wo/sh/5         \
#        cbc/wo/sh/7         \
#        tet/cb/wo           \
#        3mx/cb/wo           \

else
    echo "Error: round '$round' not yet defined."
fi