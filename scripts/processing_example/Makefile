example.h5:
	time python make_large_file.py

blkflt_example: example.h5
	time python blkflt_example.py

pyramid_example: example.h5
	time python pyramid_example.py


clean:
	\rm -f ./*# ./*~

spotless: clean
	\rm *.h5
