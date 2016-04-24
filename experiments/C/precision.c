// Copyright (C) 2016 Stanford University
// Contact: Niels Joubert <niels@cs.stanford.edu>
//


#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

void calculate_precision(const char* raw_val) {

	printf("Precision of    \"%s\":\n", raw_val);


	double double_val = atof(raw_val);
	printf("  double:        %.16f\n", double_val);

	float float_val = (float) double_val;
	printf("  float:         %.16f\n", float_val);

	int32_t int32_t_scaled_val = (int32_t) (double_val * 1e7);
	printf("  int32_t * 1e7:  %d\n", int32_t_scaled_val);

}

int main(int argc, const char* argv[]) {
	
	if (argc < 2) {
		printf("Usage:\n");
		printf("  precision <double> ... <double>\n");
		return -1;
	}

	for (int i = 1; i < argc; i++) {
		calculate_precision(argv[i]);
	}

	return 0;
}
