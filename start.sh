#!/bin/bash

pids=()

trap 'kill "${pids[@]}" 2>/dev/null; exit' INT TERM

# 3つのアプリを並列起動
python app_chat.py &
pids+=($!)

python app_retrieval.py &
pids+=($!)

python app_ui.py &
pids+=($!)

# どれか1つが終わったら全部止める
wait -n
kill "${pids[@]}" 2>/dev/null