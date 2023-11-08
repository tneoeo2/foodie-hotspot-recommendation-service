# redis를 docker로 실행해서 띄우는 파일
docker run \
-d \
--restart=always \
--name=redis \
-p 6379:6379 \
-e TZ=Asia/Seoul \
-v /srv/workspace/redis/redis.conf:/etc/redis/redis.conf \
-v redis_data:/data \
redis:latest redis-server /etc/redis/redis.conf
