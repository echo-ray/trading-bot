#!/usr/bin/env bash

rm -r ./screens/*
for ((n=1;n<11;n++))
do
  python3 trading_bot.py -c ../shared/credentials -p ETH-USDT -d 0 -str selenium-test -index ${n}
done