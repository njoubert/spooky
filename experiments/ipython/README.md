# IPython Experimentation

## Installing SNOPT and SNOPT-Python

Go to ```https://gcc.gnu.org/wiki/GFortranBinaries```

Download and install the appropriate gfortran compiler

Get the ```SNOPT.zip```

Extract it at a place you're happy to keep it forever.

Run

	./configure
	make
	sudo make install

Add the following line to your ```~/.bash_profile```

	export SNOPT7=$HOME/snopt7

Now clone ```https://github.com/snopt/snopt-python```

Cd into the directory and run

	python setup.py build
	python setup.py install --user


Done!