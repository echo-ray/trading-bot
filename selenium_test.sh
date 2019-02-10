#!/usr/bin/env bash

for ((n=1;n<21;n++))
do
  python3 trading_bot.py -c ../shared/credentials -p ETH-USDT -d 0 -str selenium-test -index ${n}
done