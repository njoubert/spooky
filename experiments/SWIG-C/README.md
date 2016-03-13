# First attempt to use SWIG to generate Python bindings

You need to install swig!

	```brew install swig```

then run make!

	```make```

This is following http://www.swig.org/tutorial.html

We can now use the Python module as follows:

	```
	>>> import example
	>>> example.fact(5)
	120
	>>> example.my_mod(7,3)
	1
	>>> example.get_time()
	'Sun Feb 11 23:01:07 1996'
	>>>
	```