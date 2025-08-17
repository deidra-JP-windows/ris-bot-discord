#!/bin/sh

# 引数が指定されていない場合はエラーメッセージを表示
if [ $# -eq 0 ]; then
  echo "使用法: $0 up | exec | down | rebuild"
  exit 1
fi

# first-up
if [ "$1" = "first-up" ]; then
  docker build -t ris-bot-discord .
  echo "コンテナを起動します..."
  MSYS_NO_PATHCONV=1 docker run -itd --name ris-bot-discord -v /c/Users/$USERNAME/.ssh:/root/.ssh ris-bot-discord
  MSYS_NO_PATHCONV=1 docker exec -it ris-bot-discord /bin/bash -c "
    chmod 600 /root/.ssh/config
    chmod 600 /root/.ssh/id_ed25519
    chown root:root /root/.ssh/config
    git clone git@github.com:deidra-JP-windows/ris-bot-discord.git
    cd /ris-bot-discord && exec /bin/bash
  "

# up
elif [ "$1" = "up" ]; then
  echo "コンテナを起動します..."
  MSYS_NO_PATHCONV=1 docker run -itd --name ris-bot-discord -v /c/Users/$USERNAME/.ssh:/root/.ssh ris-bot-discord
  MSYS_NO_PATHCONV=1 docker exec -it ris-bot-discord /bin/bash -c "
    cd /ris-bot-discord && exec /bin/bash
  "

# exec
elif [ "$1" = "exec" ]; then
  echo "コンテナに接続します..."
  if [ "$(docker ps -aq -f name=ris-bot-discord)" ] && [ "$(docker ps -q -f name=ris-bot-discord -f status=exited)" ]; then
    echo "コンテナを再起動します..."
    MSYS_NO_PATHCONV=1 docker start ris-bot-discord
  else
    echo "コンテナはすでに起動しています。"
  fi
  MSYS_NO_PATHCONV=1 docker exec -it ris-bot-discord /bin/bash -c "cd /ris-bot-discord && exec /bin/bash"


# stop
elif [ "$1" = "stop" ]; then
  echo "コンテナを停止します..."
  docker stop ris-bot-discord


# down
elif [ "$1" = "down" ]; then
  echo "コンテナを停止して削除します..."
  docker stop ris-bot-discord
  docker rm ris-bot-discord

# rebuild
elif [ "$1" = "rebuild" ]; then
  echo "イメージを再ビルドしてコンテナを再起動します..."
  docker stop ris-bot-discord
  docker rm ris-bot-discord
  docker build -t ris-bot-discord .
  MSYS_NO_PATHCONV=1 docker run -itd --name ris-bot-discord -v /c/Users/$USERNAME/.ssh:/root/.ssh ris-bot-discord
  MSYS_NO_PATHCONV=1 docker exec -it ris-bot-discord /bin/bash -c "
    chmod 600 /root/.ssh/config
    chmod 600 /root/.ssh/id_ed25519
    chown root:root /root/.ssh/config
    git clone git@github.com:deidra-JP-windows/ris-bot-discord.git
    cd /ris-bot-discord && exec /bin/bash
  "
else
  echo "不明なコマンド: $1"
  echo "使用法: $0 up | exec | down | rebuild"
  exit 1
fi
