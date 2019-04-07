PHONY:
	@docker build -t habraproxy . && docker run -d --network="host" habraproxy

clean:
	@docker stop `docker ps -a -q --filter ancestor=habraproxy` && docker rm `docker ps -a -q --filter ancestor=habraproxy`