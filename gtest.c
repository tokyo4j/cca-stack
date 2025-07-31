#include <stdint.h>
#include <stdio.h>
#include <sys/mman.h>
#include <unistd.h>

#define NR_PAGES (256 * 64) // 64MB

int main() {
	// Allocate 64 MB memory
	char *ptr = mmap(0, 4096 * NR_PAGES, PROT_READ | PROT_WRITE,
			MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
	// Initialize the allocated pages with fixed values
	for (uint32_t i = 0; i < NR_PAGES; i++)
		*(uint32_t *)&ptr[4096 * i] = i;
	// Try merging
	for (uint32_t i = 0; i < NR_PAGES; i++)
		madvise(ptr + 4096 * i, 4096, 26);

	puts("Entering infinite loop...");

	while (1) {
	}

	return 0;
}
