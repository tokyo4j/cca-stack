#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

#define NR_PAGES (256 * 1024) // 1024MB

int main(int argc, char *argv[]) {
	puts("AppStart");
	sleep(30);

	puts("AllocStart");
	char *ptr = mmap(0, 4096 * NR_PAGES, PROT_READ | PROT_WRITE,
			MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
	for (uint32_t i = 0; i < NR_PAGES; i++)
		*(uint32_t *)&ptr[4096 * i] = i;
	puts("AllocEnd");
	sleep(30);

	if (argc == 2 && !strcmp(argv[1], "--no-rme")) {
		puts("KsmStart");
		sleep(30);
	} else {
		puts("MadviseStart");
		// madvise(ptr, 4096 * NR_PAGES, 26);
		puts("MadviseEnd");
		sleep(30);
	}

	puts("LoopStart");

	while (1) {
	}

	return 0;
}
