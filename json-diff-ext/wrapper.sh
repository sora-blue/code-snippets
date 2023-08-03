set -ex
name=$1
shift
python3 tester.py "in/$name.json" "out/$name.json" "$@"
