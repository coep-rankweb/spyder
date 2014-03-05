#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <hiredis/hiredis.h>

#define IN	0
#define OUT	1
#define MAX_URL_LEN 512

typedef struct {
	unsigned int num_inlinks;
	off_t inlinks_offset;
	unsigned int num_outlinks;
	off_t outlinks_offset;
	char url[MAX_URL_LEN];
} Element;

redisContext *c;
redisReply *r;
char command[256];

int initDatabase(void) {
	const char *hostname = "127.0.0.1";
	int port = 6379;
	struct timeval timeout = {1, 500000};

	c = redisConnectWithTimeout(hostname, port, timeout);
	if(!c) {
			perror("redisContext");
			return 1;
	} else if(c->err) {
			perror("connection");
			redisFree(c);
			return 1;
	}

	return 0;
}

int process_command() {
	r = (redisReply *)redisCommand(c, command);
	if(!r || r->type == REDIS_REPLY_ERROR || r->type == REDIS_REPLY_NIL)
			return -1;
	return 0;
}

void build_links(FILE *meta, FILE *web, FILE *link, int type) {
	off_t pos, epos;
	char buf[64];
	Element e;
	long int u, v, prev_u = 0;
	int count = 0;


	pos = ftell(link);
	while(fgets(buf, 64, web)) {
		u = atol(strtok(buf, "\t"));
		v = atol(strtok(NULL, "\t"));

		sprintf(command, "GET HASH2ID:%ld", u);
		if(process_command() == -1)
			continue;
		if(!prev_u)
			prev_u = u;

		if(prev_u != u) {
			sprintf(command, "GET HASH2ID:%ld", prev_u);
			if(process_command() == -1)
				continue;
			epos = fseek(meta, (atol(r->str) - 1) * sizeof(Element), SEEK_SET);
			fread(&e, sizeof(Element), 1, meta);

			if(type == IN) {
				e.num_inlinks = count;
				count = 0;
				e.inlinks_offset = pos;
				pos = ftell(link);
			} else {
				e.num_outlinks = count;
				count = 0;
				e.outlinks_offset = pos;
				pos = ftell(link);
			}

			sprintf(command, "GET HASH2URL:%ld", prev_u);
			if(process_command() == -1)
				continue;
			strcpy(e.url, r->str);

			fseek(meta, epos, SEEK_SET);
			fwrite(&e, sizeof(Element), 1, meta);

			prev_u = u;
		}

		sprintf(command, "GET HASH2ID:%ld", v);
		if(process_command() == -1)
			continue;
		count++;
		fwrite(&v, sizeof(long int), 1, link);
	}

	fclose(web);
}

int main(int argc, char *argv[]) {
	FILE *meta, *link, *web;
	
	initDatabase();
	if(!(meta = fopen("/home/nvidia/kernel_panic/core/spyder/data/meta", "rb+"))) {
		perror("");
		return errno;
	}

	if(!(web = fopen("/home/nvidia/kernel_panic/core/spyder/data/out_matrix.mtx", "r+"))) {
		perror("");
		exit(errno);
	}
	if(!(link = fopen("/home/nvidia/kernel_panic/core/spyder/data/out_links", "wb"))) {
		perror("");
		return errno;
	}
	build_links(meta, web, link, OUT);
	fclose(web);
	fclose(link);

	system("sort -f1 /home/nvidia/kernel_panic/core/spyder/data/in_matrix.mtx > /tmp/inlinks.mtx");
	system("mv /tmp/inlinks.mtx /home/nvidia/kernel_panic/core/spyder/data/in_matrix.mtx");

	if(!(web = fopen("/home/nvidia/kernel_panic/core/spyder/data/in_matrix.mtx", "r+"))) {
		perror("");
		exit(errno);
	}
	if(!(link = fopen("/home/nvidia/kernel_panic/core/spyder/data/in_links", "wb"))) {
		perror("");
		return errno;
	}
	build_links(meta, web, link, IN);
	fclose(web);
	fclose(link);

	fclose(meta);
	return 0;
}
