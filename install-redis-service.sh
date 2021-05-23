# First download a source distribution of redis, unzip it, cd into it, and run:
# make
# make test
# make install

sudo mkdir /etc/redis
sudo cp redis.conf /etc/redis/
sudo cp redis-server.service /etc/systemd/system/

sudo groupadd redis
sudo adduser --system -g redis --no-create-home redis
sudo mkdir /var/lib/redis
sudo chown redis:redis /var/lib/redis
sudo chmod 770 /var/lib/redis
sudo mkdir /var/log/redis
sudo chown redis:redis /var/log/redis
sudo chmod 744 /var/log/redis
